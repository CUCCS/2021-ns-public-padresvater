from scapy.all import *
import logging
logging.getLogger("scapy.runtime").setLevel(logging.ERROR)

dst_ip = "192.168.56.114"
src_port = RandShort()
dst_port = 80

print('TCP xmas scan:')
print('================================================')
xmas_scan_resp = sr1(IP(dst=dst_ip)/TCP(dport=dst_port,flags="FPU"),timeout=10)
print('================================================')

if (str(type(xmas_scan_resp))=="<class 'NoneType'>"):
    print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Filtered or Open")
elif(xmas_scan_resp.haslayer(TCP)):
    if(xmas_scan_resp.getlayer(TCP).flags == 0x14):
        print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Closed")
elif(xmas_scan_resp.haslayer(ICMP)):
    if(int(xmas_scan_resp.getlayer(ICMP).type)==3 and int(xmas_scan_resp.getlayer(ICMP).code) in [1,2,3,9,10,13]):
        print('State of port '+ str(dst_port) +' of '+ str(dst_ip) +": Filtered")