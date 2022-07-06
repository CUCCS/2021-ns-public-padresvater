import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)
from scapy.all import *

dst_ip = "192.168.48.128"
src_port = RandShort()
dst_port = 53
dst_timeout = 1

print('UDP scan:')

def udp_scan(dst_ip,dst_port,dst_timeout):
    print('============================================')
    udp_scan_resp = sr1(IP(dst=dst_ip)/UDP(dport=dst_port),timeout=dst_timeout)
    print('============================================')
    if (str(type(udp_scan_resp))=="<class 'NoneType'>"):
        retrans = []
        for count in range(0,3):
            retrans.append(sr1(IP(dst=dst_ip)/UDP(dport=dst_port),timeout=dst_timeout))
        for item in retrans:
            if (str(type(item))!="<class 'NoneType'>"):
                udp_scan(dst_ip,dst_port,dst_timeout)
        print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Filtered or Open")
    elif (udp_scan_resp.haslayer(UDP) or udp_scan_resp.getlayer(IP).proto == IP_PROTOS.udp):
        print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Open")
    elif(udp_scan_resp.haslayer(ICMP)):
        if(int(udp_scan_resp.getlayer(ICMP).type)==3 and int(udp_scan_resp.getlayer(ICMP).code)==3):
            print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Closed")
        elif(int(udp_scan_resp.getlayer(ICMP).type)==3 and int(udp_scan_resp.getlayer(ICMP).code) in [1,2,9,10,13]):
            print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Filtered")

udp_scan(dst_ip,dst_port,dst_timeout)