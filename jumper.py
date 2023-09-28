import socket, time,argparse
from scapy.all import sr1, IP, ICMP

from pprint import pprint


class Jumper:
    def __init__(self, destination:str, interface:str, timeout:int=2, verbose:int=0):
        self.destination = destination
        self.interface = interface
        self.timeout = timeout
        self.verbose = verbose # 0 = silent, 1 = verbose, 2 = very verbose
    
    def single_jump(self, ttl:int=1):
        packet=IP(dst=self.destination, ttl=ttl)/ICMP()/"XXXXXXXXX"
        start_time=time.time()
        sent=sr1(packet, timeout=self.timeout, verbose=self.verbose)
        end_time=time.time()
        
        return end_time-start_time, sent

    def path_finder(self, max_ttl:int=255):
        hops=[]
        ttl=1
        not_sent_cnt=0
        prev_ip=""
        while ttl<max_ttl:
            time_taken, sent=self.single_jump(ttl)
            ttl+=1
            
            if not sent:
                print("***")
                not_sent_cnt+=1
                if not_sent_cnt>5: break
                continue

            not_sent_cnt=0
            if prev_ip==sent.src: break
            
            resolved_ip=self.resolve_ip(sent.src)
            print(f"{ttl-1} RTT al host=\"{resolved_ip}\" ({sent.src}) = {time_taken*1000} ms")
            hops.append(sent.src)
            
            if sent.src == self.destination:
                print("Hem arribat al desti.")
                break
            prev_ip=sent.src

        return hops


    def resolve_ip(self, ip:str):
        try: return socket.gethostbyaddr(ip)[0]
        except: return ip
    

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Ping tool using Scapy")

    parser.add_argument("-i", "--interface", help="Network interface to use", default=None)
    parser.add_argument("-t", "--timeout", type=int, help="Timeout for the ping response", default=2)
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity")
    parser.add_argument("-d", "--destination", required=True, help="Destination IP address to ping")
    args = parser.parse_args()
    
    j=Jumper(destination=args.destination, interface=args.interface, timeout=args.timeout, verbose=args.verbose)
    j.path_finder()