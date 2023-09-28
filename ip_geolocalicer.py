import ipinfo, asyncio

ip_info = []
coordinates = []

async def do_req(ip):
     details = await handler.getDetails(ip)
     # print("Hostname:", details.hostname)
     # print("City:", details.city)
     # print("Location:", details.loc)
     # print("Country:", details.country)
     # print("Region:", details.region)
     # print("Organization:", details.org)
     # print("Postal Code:", details.postal)
     # print("Timezone:", details.timezone)
     # print("Country Name:", details.country_name)
     # print("Latitude:", details.latitude)
     # print("Longitude:", details.longitude)
     # print("=====================================\n")
     ip_info.append(details.all)
     coordinates.append((details.latitude, details.longitude))

with open('access_token.txt', 'r') as f:
        access_token = f.read()

handler = ipinfo.getHandlerAsync(access_token)

ip_address = [
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

loop = asyncio.get_event_loop()

print("Requesting IP details...\n")

for ip in ip_address:
     loop.run_until_complete(do_req(ip))

print(ip_info)
print(coordinates)