#!/usr/bin/python3

import matplotlib.pyplot as plt

import os
import dpkt
import ipaddress
import numpy

import click

from lib.EspIterator import *
from lib.Direction import *

from pylab import rcParams
rcParams['figure.figsize'] = 30, 10

# UE/ePDG IP Address
DEFAULT_ADDR_UE = '10.42.0.110'
DEFAULT_ADDR_EPDG = '221.120.23.1'

@click.command()
@click.argument('pcap_file',    type=click.File(mode='rb'))
@click.option('-i', '--index',  type=int, nargs=2, help='開始、結束編號(包含).')
@click.option('-o', '--output', type=click.File(mode='w', ), help='輸出檔案位置')
@click.option('-v', '--verbose', is_flag=True, default=False)
@click.option('-u', '--ue',     type=str, default=DEFAULT_ADDR_UE, help='Address of UE')
@click.option('-e', '--epdg',     type=str, default=DEFAULT_ADDR_EPDG, help='Address of ePDG')

def main(pcap_file, index, output, verbose, ue, epdg):
    if not output:
        output_name = os.path.splitext(os.path.basename(pcap_file.name))[0] + '.png'
        output = open(output_name, 'w')

    data = {'Timestamp':[], 'Upward/Downward':[], 'Length':[], 'Event':[]}
    
    espiter = EspIter(pcap_file, file=sys.stderr if verbose else open(os.devnull,'w'))
    
    addr_ue = ipaddress.ip_address(ue)
    addr_epdg = ipaddress.ip_address(epdg)
    
    for ind, timestamp, pktlist in espiter :
    
        if len(index) > 1 :
            if ind < index[0] : continue
            elif ind > index[1] : break
    
        ip = pktlist[1]
        addr_src = ipaddress.ip_address(ip.src)
        addr_dst = ipaddress.ip_address(ip.dst)
        if not checkIp(ip, addr_ue, addr_epdg) :
            print( f'[{ind}]-[{timestamp}] not from UE/ePDG', file=sys.stderr)
            print( f'Src: {str(addr_src)}, DST:{str(addr_dst)}', file=sys.stderr)
            print()
            continue

        #Record this packet 
        data['Timestamp'] += [timestamp]
        data['Upward/Downward'] += [ Direction.UPWARD.value if addr_src==addr_ue else Direction.DOWNWARD.value ]
        udp = pktlist[2]
        data['Length'] += [ udp.ulen ]

        print( f'[{ind}]-[{timestamp}] length {udp.ulen} recorded.')

    number_packet = len(data['Length'])
    print(f'Finish Scanning. Total packet recorded: {number_packet}')

    print(f'Output file: {output.name}')
    print('Saving...')


    upward = {'Timestamp':[], 'Length':[]}
    downward = {'Timestamp':[], 'Length':[]}
    for index in range(len(data['Length'])) :
        if data['Upward/Downward'][index] == Direction.UPWARD.value:
            upward['Timestamp'] += [data['Timestamp'][index]]
            upward['Length'] += [data['Length'][index]]
        else :
            downward['Timestamp'] += [data['Timestamp'][index]]
            downward['Length'] += [data['Length'][index]]
        
    plt.title('Source:' + os.path.basename(pcap_file.name))
    print(len(upward['Length']))
    print(len(downward['Length']))
    
    plt.plot(upward['Timestamp'], upward['Length'], marker = 'o', color='blue')
    plt.plot(downward['Timestamp'], downward['Length'], marker = 'x', color='red')
    
    if len(upward['Timestamp'])==0 and len(downward['Timestamp'])==0 :
        pass
    elif len(upward['Timestamp'])==0 :
        end = max(downward['Timestamp'])
        start = max(end - 1, 0 )
    elif len(downward['Timestamp']) :
        start = min(upward['Timestamp'])
        end = start + 1
    else :
        start = min( min(upward['Timestamp']), min(downward['Timestamp']) )
        end = max( max(upward['Timestamp']), max(downward['Timestamp']) )

    plt.xticks(numpy.arange(start, end+1, 1.0)) 

    plt.savefig(output.name, dpi=100.0)
    print('Down.')

def checkIp(ip, addr_ue, addr_epdg):
        addr_src = ipaddress.ip_address(ip.src)
        addr_dst = ipaddress.ip_address(ip.dst)
        return (addr_src == addr_ue and addr_dst == addr_epdg) or (addr_dst == addr_ue and addr_src == addr_epdg)       

if __name__ == '__main__':
    main()
