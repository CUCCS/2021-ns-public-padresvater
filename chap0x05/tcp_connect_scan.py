import logging
from scapy.all import *
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

dst_ip = "192.168.56.114"
src_port = RandShort()
dst_port = 80

print('TCP connect scan:')
print('==================================================')
tcp_connect_scan_resp = sr1(IP(dst=dst_ip)/TCP(sport=src_port,dport=dst_port,flags="S"),timeout=10)
print('==================================================')


if(str(type(tcp_connect_scan_resp))=="<class 'NoneType'>"):
    print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Closed")
elif(tcp_connect_scan_resp.haslayer(TCP)):
    if(tcp_connect_scan_resp.getlayer(TCP).flags == 0x12):       
        send_rst = sr(IP(dst=dst_ip)/TCP(sport=src_port,dport=dst_port,flags="AR"),timeout=10)
        print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Open")
    elif(tcp_connect_scan_resp.getlayer(TCP).flags == 0x14):
        # 
        print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Closed")
elif(tcp_connect_scan_resp.haslayer(ICMP)):
    if(int(tcp_connect_scan_resp.getlayer(ICMP).type)==3 and int(tcp_connect_scan_resp.getlayer(ICMP).code) in [1,2,3,9,10,13]):
        print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Filtered")