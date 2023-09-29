import ipinfo, os
from dotenv import load_dotenv

class Locator:
     def __init__(self) -> None:
          load_dotenv()
          self.token=os.getenv("ACCESS_TOKEN")
          print(self.token)

     def run(self, ips:list[str]):
          handler = ipinfo.getHandler(self.token)
          locations=handler.getBatchDetails(ips)
          
          return {
               ip:(locations[ip]["longitude"], locations[ip]["latitude"]) 
               for ip in ips
          }

if __name__=="__main__":
     from pprint import pprint

     ip_address=[
          '149.6.131.89',
          '154.54.61.197',
          '154.54.57.229',
          '154.54.61.129',
          '154.54.85.241',
          '154.54.7.158',
          '154.54.28.70',
          '154.54.0.54',
          '154.54.5.217',
          '154.54.44.86',
          '154.54.42.102',
     ]
     l=Locator()
     pprint(l.run(ip_address))