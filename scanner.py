import nmap
import time

nm = nmap.PortScanner()


# CREATE TABLE scans (
#     id INTEGER PRIMARY KEY,
#     liveHosts INTEGER NOT NULL,


# )

# CREATETABLE host (
    
#     ip STRING NOT NULL,
#     mac TEXT,
#     os STRING,
#     uptime INTEGER

# )



liveHosts = []
localNetwork = "192.168.1.0/24"

print("Starting ping scan to find out how many devices are connected to network...")
pingScanStart = time.time()
nm.scan(hosts=localNetwork, arguments = "-sn")
pingScanEnd = time.time()
print(f"Ping scan finished after {pingScanEnd - pingScanStart:.2f} seconds")

for host in nm.all_hosts():
    if nm[host].state() == "up":
        liveHosts.append(host)

print(f"Found {len(liveHosts)} devices currently connected to the network")

liveHosts = ' '.join(liveHosts) # space seperates the IPs

print("Starting OS detection scan on devices currently connected to the network")
osScanStart = time.time()
nm.scan(hosts=liveHosts, arguments = "-O --osscan-guess")

osScanEnd = time.time()
print(f"OS detection scan finished in {osScanEnd - osScanStart} seconds")

for host in nm.all_hosts():

    print(f'Host: {host} ({nm[host].hostname()}) - State: {nm[host].state()}')

    # Retrieve MAC address if available
    if 'mac' in nm[host]['addresses']:
        mac_address = nm[host]['addresses']['mac']
        print(f'  MAC Address: {mac_address}')
    else:
        print("  MAC Address: Not available")

    # Sort osmatch by accuracy in descending order and pick the most likely match
    if nm[host]['osmatch']:
        most_likely_os = max(nm[host]['osmatch'], key=lambda x: int(x['accuracy']))
        print(f'  Most Likely OS: {most_likely_os["name"]} (accuracy: {most_likely_os["accuracy"]}%)')

    # # Access osclass details if available
    # if 'osclass' in most_likely_os:
    #     osclass = most_likely_os['osclass'][0]  # Take the first osclass entry
    #     print(f'    OS Class: {osclass["type"]}, Vendor: {osclass["vendor"]}, Family: {osclass["osfamily"]}')
    #     print(f'    OS Generation: {osclass.get("osgen", "N/A")}, Accuracy: {osclass["accuracy"]}%')

    else:
        print("  OS detection not available.")

    if 'uptime' in nm[host]:
        uptime = nm[host]['uptime']
        seconds = int(uptime["seconds"])
        days = seconds // (24 * 3600)
        hours = (seconds % (24 * 3600)) // 3600
        minutes = (seconds % 3600) // 60
        print(f'  Uptime: {days} days, {hours} hours, {minutes} minutes')
        print(f'  Last Boot Time: {uptime["lastboot"]}')
    else:
        print("  Uptime information not available.")

    print("-" * 50)

totalScanTime = pingScanEnd -  pingScanStart + osScanEnd - osScanStart
print(f"Total scan time: {totalScanTime:.2f}")

