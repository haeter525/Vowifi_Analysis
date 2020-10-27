import scapy.layers.inet
import scapy.all
import socket
import ipaddress
import joblib
import netfilterqueue

import lib.Event
import lib.Direction

import CustomTree

INDEX = 0
CURRENT_STATE = lib.Event.Event.NONE.value

MAX_STAIR = None
STEP = None
FLOORS = [lib.Event.Event.NONE.value, lib.Event.Event.RINGING6.value, lib.Event.Event.VOICE11.value]
CURRENT_FLOOR = None

BLOCK_EVENT = None

BLOCK_CONNECT = False

def show_info():
    print(f'RUN_TYPE:\t{RUN_TYPE}')
    print(f'UE_IP:\t{str(UE_ADDRESS)}')
    print(f'EPDG_IP:\t{str(EPDG_ADDRESS)}')

    if not BLOCK_EVENT is None:
        print(f'BLOCK_ON: {lib.Event.EVENT_NAMES[BLOCK_EVENT]}')

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
    if (_core_anlyize(pkt) == True) and (not (BLOCK_EVENT is None)) and (CURRENT_STATE >= BLOCK_EVENT) :
        on_target_state(CURRENT_STATE, nf_packet)
    else:
        nf_packet.accept()

def _st_anlyize(scapy_packet):
    _core_anlyize(scapy_packet)

def _core_anlyize(scapy_packet):
    global INDEX, CURRENT_STATE, STEP, CURRENT_FLOOR
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
        print(f'\t-> {dp_event}', end='')

        STEP = MAX_STAIR
        for i in range(len(FLOORS)):
            if next_state == FLOORS[i]:
                CURRENT_FLOOR = i
                
    elif (MAX_STAIR is not None) and (next_state != FLOORS[CURRENT_FLOOR]):
        STEP = STEP - 1
        if STEP==0:
            next_state = FLOORS[CURRENT_FLOOR]
            print(f'\ttimeout -> {next_state}',end='')
            STEP = MAX_STAIR

    print('')
                
    # Update state
    CURRENT_STATE = next_state

    return True

def set_model(model_file):
    global trained_clf
    trained_clf = joblib.load(model_file)

def init_custom_tree():
    global trained_clf
    trained_clf = CustomTree.StateTree()

    global MAX_STAIR, STEP, CURRENT_FLOOR
    MAX_STAIR = 8
    STEP = MAX_STAIR
    CURRENT_FLOOR = 0

def set_block_event(index):
    global BLOCK_EVENT
    if index is None:
        BLOCK_EVENT = None
    else:
        assert( index < len(lib.Event.EVENT_NAMES) )
        BLOCK_EVENT = index

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

if __name__ == '__main__':
    RUN_TYPE = 'PCAP'
    # RUN_TYPE = 'RT'
    # RUN_TYPE = 'TEST'

    # TREE_TYPE = 'TRAINED'
    TREE_TYPE = 'CUSTOM'

    if TREE_TYPE == 'TRAINED':
        print('讀取模型...', end='')
        set_model('Model/VowifiParser_v1026095919.joblib')
        print('完成！')
    elif TREE_TYPE == 'CUSTOM':
        print('自建決策樹...', end='')
        init_custom_tree()
    print('完成！')

    set_addresses('10.42.0.110', '221.120.23.1')


    set_block_event(12)

    print('')
    show_info()
    print('\n等待中...')

    if RUN_TYPE == 'RT':
        run_in_realtime(1, _rt_anlyize)
    elif RUN_TYPE == 'PCAP':
        pcap_file = 'Wireshark_pkt/Wifi連線_接起/Wifi_110to240_VOICE_1651_tidyup.pcap'
        run_on_pcap(pcap_file, _st_anlyize)

