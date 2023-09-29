from pprint import pprint

import ipinfo, os
from dotenv import load_dotenv

class Locator:
    def __init__(self, token:str|None=None, env_file:str=".env") -> None:
        if not token:
            load_dotenv(env_file)
            self.token=os.getenv("ACCESS_TOKEN")
        else: self.token=token

    def run(self, ips:list[str]):
        handler = ipinfo.getHandler(self.token)
        ip_data=handler.getBatchDetails(ips)

        return {
            ip:(float(ip_data[ip]["latitude"]), float(ip_data[ip]["longitude"])) 
            for ip in ips if ip_data[ip]["longitude"] and ip_data[ip]["latitude"]
        }

from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt

class Mapper:
    def mapit(self, coordinates:list[tuple[float, float]], timeout:bool=False, image_filaname:str|None="world_map.png"):
        m=Basemap(projection='mill', resolution='l')
        m.drawcoastlines()
        m.drawcountries()
        m.drawmapboundary(fill_color='aqua')
        m.fillcontinents(color='lightgreen', lake_color='aqua')

        if not coordinates: raise Exception("No coordinates to map")
        lats, lons = zip(*coordinates)
        x, y = m(lons, lats)

        m.scatter(x[0], y[0], marker='o', color='green', label='Start', zorder=5)
        m.scatter(x[1:-2], y[1:-2], marker='o', color='red', label='Nodes', zorder=5)
        m.scatter(x[-1], y[-1], marker='o' if not timeout else 'x', color='blue' if not timeout else 'black', label='End', zorder=5)

        for i in range(len(coordinates) - 1):
            x1, y1 = m(coordinates[i][1], coordinates[i][0]) 
            x2, y2 = m(coordinates[i+1][1], coordinates[i+1][0])
            plt.plot([x1, x2], [y1, y2], color='black', linewidth=2, zorder=3)

        plt.legend()
        if image_filaname: plt.savefig(image_filaname, bbox_inches='tight')
        plt.show()

import socket, time,argparse
from scapy.all import sr1, IP, ICMP  # type: ignore

class Jumper:
    def __init__(self, destination:str, interface:str, timeout:int=2, verbose:int=0, max_requests:int=5):
        self.destination = destination
        self.interface = interface
        self.timeout = timeout
        self.verbose = verbose # 0 = silent, 1 = verbose, 2 = very verbose
        self.max_requests = max_requests
    
    def single_jump(self, ttl:int=1):
        packet=IP(dst=self.destination, ttl=ttl)/ICMP()/"XXXXXXXXX"
        start_time=time.time()
        sent=sr1(packet, timeout=self.timeout, verbose=self.verbose, iface=self.interface)
        end_time=time.time()
        
        return end_time-start_time, sent

    def path_finder(self, max_ttl:int=255):
        hops=[]
        ttl=1
        not_sent_cnt=0
        prev_ip=""
        timeout=False
        while ttl<max_ttl:
            timeout=True
            time_taken, sent=self.single_jump(ttl)
            ttl+=1
            
            if not sent:
                print("***")
                not_sent_cnt+=1
                if not_sent_cnt>self.max_requests:
                    print("TIMEOUT")
                    break
                continue

            not_sent_cnt=0
            if prev_ip==sent.src: 
                print("REPEATED IP")
                break
            
            resolved_ip=self.resolve_ip(sent.src)
            print(f"{ttl-1} RTT al host=\"{resolved_ip}\" ({sent.src}) = {time_taken*1000} ms")
            hops.append(sent.src)
            timeout=False

            if sent.src == self.destination:
                print("Hem arribat al desti.")
                break
            prev_ip=sent.src

        return timeout, hops

    def resolve_ip(self, ip:str):
        try: return socket.gethostbyaddr(ip)[0]
        except: return ip
    

if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Ping tool using Scapy")

    parser.add_argument("-i", "--interface", help="Network interface to use", default=None)
    parser.add_argument("-t", "--timeout", type=int, help="Timeout for the ping response", default=2)
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity", default=False)
    parser.add_argument("-d", "--destination", required=True, help="Destination IP address to ping")
    parser.add_argument("-m", "--max-requests", type=int, help="Maximum requests to the same destination", default=5)
    parser.add_argument("-o", "--output", help="Output image filename", default="world_map.png")
    args = parser.parse_args()
    
    j=Jumper(destination=args.destination, interface=args.interface, timeout=args.timeout, verbose=args.verbose, max_requests=args.max_requests)
    timeout, ips=j.path_finder()
    
    l=Locator()
    locations=l.run(ips)
    
    m=Mapper()
    m.mapit(
        [locations[ip] for ip in ips if ip in locations.keys() and locations[ip]], 
        timeout=timeout, 
        image_filaname=args.output
    )