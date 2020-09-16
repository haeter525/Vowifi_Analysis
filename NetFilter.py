# %%
# imports
import scapy.layers.inet
import scapy.all
import ipaddress
import joblib

import lib.Event
import lib.Direction

# %%
# 讀取訓練模型檔案
modelFile = 'Model/VowifiParser_preFinal.joblib'

print('讀取模型...', end='')
trained_clf = joblib.load(modelFile)
print('完成！')
# %%
# 讀取 Pcap 並預測
UE_ADDRESS = ipaddress.IPv4Address('10.42.0.110')
EPDG_ADDRESS = ipaddress.IPv4Address('221.120.23.1')

index = 0
vowifi_event = 0

def analyize_packet(packet):
    global index
    index = index + 1
    if not packet.haslayer(scapy.layers.ipsec.ESP):
        return
    if len(packet) < 190:
        return

    direct = None
    ip = packet.getlayer(scapy.layers.inet.IP)
    ip_src = ipaddress.IPv4Address(ip.src)
    ip_dst = ipaddress.IPv4Address(ip.dst)
    
    if ip_src == UE_ADDRESS and ip_dst == EPDG_ADDRESS:
        direct = lib.Direction.Direction.UPWARD.value
    elif ip_dst == UE_ADDRESS and ip_src == EPDG_ADDRESS:
        direct = lib.Direction.Direction.DOWNWARD.value
    else:
        return

    global vowifi_event
    inp = [[direct, len(packet), vowifi_event]]

    nxt = trained_clf.predict(inp)
    display_len = str(len(packet))
    display_direct = '^' if direct == lib.Direction.Direction.UPWARD.value else 'v'
    if nxt[0] != vowifi_event:
        display_event = lib.Event.EVENT_NAMES[nxt[0]]
        print(f'{index:>3}\t{display_direct}\t{display_len}\t-> {display_event}')

        vowifi_event = nxt[0]
    else:
        print(f'{index:>3}\t{display_direct}\t{display_len}')


assert(('trained_clf' in globals()), "先讀取模型！")
print('Index\tDir\tLength\tTransfrom')
scapy.all.sniff(
    offline='Wireshark_pkt/Wifi連線_接起/Wifi_110to240_VOICE_1637_tidyup.pcap',
    prn=analyize_packet,
    store=0
)
# %%
