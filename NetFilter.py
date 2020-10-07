import scapy.layers.inet
import scapy.all
import socket
import ipaddress
import joblib
import netfilterqueue

import lib.Event
import lib.Direction

INDEX = 0
CURRENT_STATE = lib.Event.Event.NONE.value
BLOCK_EVENTS = None

BLOCK_CONNECT = False

def show_info():
    print(f'RUN_TYPE:\t{RUN_TYPE}')
    print(f'UE_IP:\t{str(UE_ADDRESS)}')
    print(f'EPDG_IP:\t{str(EPDG_ADDRESS)}')

    if not BLOCK_EVENTS is None:
        print(f'BLOCK_ON: {[ lib.Event.EVENT_NAMES[i] for i in BLOCK_EVENTS ]}')

def start_blocking():
    global BLOCK_CONNECT
    BLOCK_CONNECT = True

def end_blocking():
    global BLOCK_CONNECT
    BLOCK_CONNECT = False

def on_target_state(state, nf_packet):
    print('---|攔截|---')
    start_blocking()
    nf_packet.drop()

def _rt_anlyize(nf_packet):
    # Convert nfqueue packet obj to scapy packet obj
    pkt = scapy.layers.inet.IP(nf_packet.get_payload())


    # Does it need to block
    if BLOCK_CONNECT:
        print('.')
        nf_packet.drop()
        return

    # Does the target state meet
    if (_st_anlyize(pkt) == True) and (not (BLOCK_EVENTS is None)) and (CURRENT_STATE in BLOCK_EVENTS) :
        on_target_state(CURRENT_STATE, nf_packet)
    else:
        nf_packet.accept()

def _st_anlyize(scapy_packet):
    global INDEX, CURRENT_STATE
    UP_VAL = lib.Direction.Direction.UPWARD.value
    DOWN_VAL = lib.Direction.Direction.DOWNWARD.value

    pkt_input = [UP_VAL, 0, CURRENT_STATE]

    # Counter plus
    INDEX = INDEX + 1

    # Check for ESP (by port)
    if not (scapy_packet.sport == 4500 or scapy_packet.dport == 4500):
        return False

    # Check for Length
    pkt_len = len(scapy_packet) + 14
    if pkt_len < 190:
        return False
    pkt_input[1] = pkt_len

    # Check for ip
    ip = scapy_packet.getlayer(scapy.layers.inet.IP)
    ip_src, ip_dst = ipaddress.IPv4Address(ip.src), ipaddress.IPv4Address(ip.dst)
    if ip_src == UE_ADDRESS and ip_dst == EPDG_ADDRESS:
        pkt_input[0] = UP_VAL
    elif ip_dst == UE_ADDRESS and ip_src == EPDG_ADDRESS:
        pkt_input[0] = DOWN_VAL
    else:
        return False

    # Predict
    next_state = trained_clf.predict([pkt_input])

    # Show state
    dp_len = len(scapy_packet)
    dp_dir = '^' if pkt_input[0]==UP_VAL else 'v'
    print(f'{INDEX:>3}\t{dp_dir}\t{dp_len}', end='')

    if CURRENT_STATE != next_state:
        dp_event = next_state
        print(f'\t-> {dp_event}')
    else:
        print('')

    # Update state
    CURRENT_STATE = next_state

    return True

def set_model(model_file):
    global trained_clf
    trained_clf = joblib.load(model_file)

def set_block_event(index_list):
    global BLOCK_EVENTS
    if index_list is None:
        BLOCK_EVENTS = None
    else:
        for i in index_list:
            assert( i in range(len(lib.Event.EVENT_NAMES)) )
        BLOCK_EVENTS = index_list

def set_addresses(ue_addr, epdg_addr):
    global UE_ADDRESS
    UE_ADDRESS = ipaddress.IPv4Address(ue_addr)
    global EPDG_ADDRESS
    EPDG_ADDRESS = ipaddress.IPv4Address(epdg_addr)

def run_on_pcap(pcapFile, callback):
    print('Index\tDir\tLength\tTransfrom')
    scapy.all.sniff(
        offline=pcapFile,
        prn=_st_anlyize,
        store=0
    )

def run_in_realtime(queue_num, callback):
    nfqueue = netfilterqueue.NetfilterQueue()
    nfqueue.bind(queue_num, _rt_anlyize, 16, netfilterqueue.COPY_PACKET)

    try:
        nfqueue.run()
    except KeyboardInterrupt as e:
        print('使用者中斷，停止程式')
    finally:
        nfqueue.unbind()

if __name__ == "__main__":
    print('讀取模型...', end='')
    set_model('Model/VowifiParser_retrained.joblib')
    print('完成！')

    set_addresses('10.42.0.110', '221.120.23.1')

    # RUN_TYPE = 'PCAP'
    RUN_TYPE = 'RT'
    # RUN_TYPE = 'TEST'

    set_block_event([8])

    print('')
    show_info()
    print('\n等待中...')

    if RUN_TYPE == 'RT':
        run_in_realtime(1, _rt_anlyize)
    elif RUN_TYPE == 'PCAP':
        pcap_file = input('輸入 Pcap 檔案位置:')
        run_on_pcap(pcap_file, _st_anlyize)

