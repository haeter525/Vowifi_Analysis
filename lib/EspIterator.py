
import sys
import ipaddress

import dpkt

class EspIter:

    def __init__(self, pcap_file, file=sys.stderr):
        self.pcap_file = pcap_file
        self.out = file

    def _convert2Ethernet(self, pkt):
        return dpkt.ethernet.Ethernet(pkt)
    
    def _convert2Ip(self, eth):
        return None if not isinstance(eth.data, dpkt.ip.IP) else eth.data
    
    def _convert2Udp(self, ip):
        return None if not isinstance(ip.data, dpkt.udp.UDP) else ip.data
    
    def _convert2Esp(self, udp):
        try:
            return dpkt.esp.ESP(udp.data)
        except (dpkt.dpkt.NeedData, dpkt.dpkt.UnpackError):
            return None
    
    def __iter__(self):
        reader = dpkt.pcap.Reader(self.pcap_file)
        index = 0
        
        for timestamp, pkt in reader :
            index += 1
            
            eth = self._convert2Ethernet(pkt)
            ip = self._convert2Ip(eth)
            if ip is None :
                print( f'[{index}]-[{timestamp}] not a IP packet.', file=self.out)
                continue
            
            udp = self._convert2Udp(ip)
            if udp is None :
                print( f'[{index}]-[{timestamp}] not a UDP packet.', file=self.out)
                continue
            
            esp = self._convert2Esp(udp)
            if esp is None :
                print( f'[{index}]-[{timestamp}] not a ESP packet.', file=self.out)
                continue
                
            yield index, timestamp, [eth, ip, udp, esp]



if __name__ == '__main__':
    pass
