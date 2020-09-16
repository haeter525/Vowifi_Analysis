#!/usr/bin/python3
# %%
# 讀取訓練模型檔案
from joblib import dump, load
modelFile = '../VowifiParser_v0916083537.joblib'

print('讀取模型...', end='')
trained_clf = load(modelFile)
print('完成！')
# %%
# 讀取 Pcap 並預測
import ipaddress
import scapy.all
import scapy.layers.inet

UE_ADDRESS   = ipaddress.IPv4Address('10.42.0.110')
EPDG_ADDRESS = ipaddress.IPv4Address('221.120.23.1')

index = 0
vowifi_event = 0
def analyize_packet(packet):
    global index
    index = index + 1
    if not packet.haslayer(scapy.layers.ipsec.ESP): return

    direct = None
    ip = packet.getlayer(scapy.layers.inet.IP)
    ip_src = ipaddress.IPv4Address(ip.src)
    ip_dst = ipaddress.IPv4Address(ip.dst)
    if ip_src == UE_ADDRESS and ip_dst == EPDG_ADDRESS :
        direct = -1
    elif ip_dst == UE_ADDRESS and ip_src == EPDG_ADDRESS :
        direct = 1
    else :
        return

    global vowifi_event
    inp = [[direct, len(packet), vowifi_event]]

    nxt = trained_clf.predict(inp)
    if nxt[0] != vowifi_event :
        print(f'{index:>3}\t{len(packet)}\t{vowifi_event} -> {nxt[0]}')
        vowifi_event = nxt[0]
    else :
        print(f'{index:>3}\t{len(packet)}')
    

assert(('trained_clf' in globals()), "先讀取模型！")
scapy.all.sniff(
    offline='../../Wireshark_pkt/Wifi連線_接起/Wifi_110to240_VOICE_1636_tidyup.pcap',
    prn=analyize_packet,
    store=0
)
# %%
