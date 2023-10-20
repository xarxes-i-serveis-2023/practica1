from dotenv import load_dotenv
from scapy.all import sr1, IP, ICMP, UDP  # type: ignore
from mpl_toolkits.basemap import Basemap
import matplotlib.pyplot as plt
import socket, time, argparse, ipinfo, os

class Locator:
    def __init__(self, token:str|None=None, env_file:str=".env") -> None:
        if not token:
            load_dotenv(env_file)
            self.token=os.getenv("ACCESS_TOKEN")
        else: self.token=token
        
        if self.token is None: raise Exception("No token provided")

    def run(self, ips:list[str]):
        handler = ipinfo.getHandler(self.token)
        ip_data = handler.getBatchDetails(ips)

        return {
            ip:(float(ip_data[ip]["latitude"]), float(ip_data[ip]["longitude"])) 
            for ip in ips if ip_data[ip]["longitude"] and ip_data[ip]["latitude"]
        }

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

        m.scatter(x[0], y[0], marker='o', color='green', label='Start', zorder=6)
        m.scatter(x[1:-2], y[1:-2], marker='o', color='red', label='Nodes', zorder=5)
        m.scatter(x[-1], y[-1], marker='o' if not timeout else 'x', color='blue' if not timeout else 'black', label='End', zorder=6)

        for i in range(len(coordinates) - 1):
            x1, y1 = m(coordinates[i][1], coordinates[i][0]) 
            x2, y2 = m(coordinates[i+1][1], coordinates[i+1][0])
            plt.plot([x1, x2], [y1, y2], color='black', linewidth=2, zorder=3)

        plt.legend()
        if image_filaname: plt.savefig(image_filaname, bbox_inches='tight')
        plt.show()

class Jumper:
    PACKER_MIN=28
    INITIAL_UDP_PORT=33434

    def __init__(self, destination:str, interface:str, timeout:int=2, verbose:int=0, packet_size:int=60, use_udp:bool=False, max_ttl:int=30):
        print(f"visualtraceroute to {destination}, {max_ttl} max hops, {packet_size} byte packets, " + ("UDP" if use_udp else "ICMP") + " protocol.")

        self.destination = destination
        self.interface = interface
        self.timeout = timeout
        self.verbose = verbose # 0 = silent, 1 = verbose, 2 = very verbose
        self.packet_size = packet_size
        if packet_size<self.PACKER_MIN: raise Exception(f"packet can't be smaller than: {self.PACKER_MIN}")
        self.use_udp = use_udp
        self.max_ttl = max_ttl

    def single_jump(self, ttl:int=1):
        packet=IP(dst=self.destination, ttl=ttl) / \
            ( ICMP() if not self.use_udp else UDP(dport=self.INITIAL_UDP_PORT+ttl)) / \
                ("X"*(self.packet_size-self.PACKER_MIN))

        start_time=time.time()
        sent=sr1(packet, timeout=self.timeout, verbose=self.verbose, iface=self.interface)
        end_time=time.time()
        
        return end_time-start_time, sent

    def path_finder(self):
        hops=[]
        ttl=1
        timeout=True
        while ttl<self.max_ttl:
            time_taken, reply=self.single_jump(ttl)
            ttl+=1

            if reply is None or not reply.haslayer(ICMP) or reply.type not in [0,11,3]:
                print("***")
                continue

            print(f"{ttl-1} RTT al host=\"{self.resolve_ip(reply.src)}\" ({reply.src}) = {time_taken*1000} ms")
            hops.append(reply.src)

            if reply.src == self.destination:
                print("Hem arribat al desti.")
                timeout=False
                break

        return timeout, hops

    def resolve_ip(self, ip:str):
        try: return socket.gethostbyaddr(ip)[0]
        except: return ip
    
if __name__=="__main__":
    parser = argparse.ArgumentParser(description="Ping tool using Scapy")
    parser.add_argument("destination", help="Destination IP address to ping")
    parser.add_argument("-i", "--interface", help="Network interface to use", default=None)
    parser.add_argument("-t", "--timeout", type=int, help="Timeout for the ping response", default=2)
    parser.add_argument("-v", "--verbose", action="store_true", help="Increase verbosity", default=False)
    parser.add_argument("-m", "--max-ttl", type=int, help="Maximum TTL number", default=30)
    parser.add_argument("-p", "--packet-size", type=int, help="Packet size sent in bytes. Default 60B, minimum 28B.", default=60)
    parser.add_argument("-o", "--output", help="Output image filename", default="world_map.png")
    parser.add_argument("-u", "--udp", action="store_true", help="Send UDP packets", default=False)
    args = parser.parse_args()
    
    j=Jumper(destination=args.destination, interface=args.interface, timeout=args.timeout, verbose=args.verbose, packet_size=args.packet_size, use_udp=args.udp, max_ttl=args.max_ttl)
    timeout, ips=j.path_finder()
    
    print("\nLocating ips...")
    
    l=Locator()
    locations=l.run(ips)
    
    print("\nMapping...")
    
    m=Mapper()
    m.mapit(
        [locations[ip] for ip in ips if ip in locations.keys() and locations[ip]], 
        timeout=timeout, 
        image_filaname=args.output
    )
    