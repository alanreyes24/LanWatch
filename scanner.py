import nmap
import sqlite3
import datetime
import os
import socket
import subprocess
import re
from mac_vendor_lookup import MacLookup

time = datetime.datetime.now()
nm = nmap.PortScanner()

connection = sqlite3.connect(r"C:\repos\LanWatch\LanWatch\db\database.db") # later make this path tied to an environment variable
cursor = connection.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

sql =  '''

CREATE TABLE if not exists scans (

    id INTEGER PRIMARY KEY,
    time TEXT NOT NULL

)

'''
cursor.execute(sql)

sql = '''

CREATE TABLE if not exists hosts (
    ip TEXT NOT NULL,
    mac TEXT,
    dns TEXT,
    os TEXT,
    uptime INTEGER,
    scanID INTEGER NOT NULL,
    FOREIGN KEY (scanID) REFERENCES scans(id)
)

'''

cursor.execute(sql)

sql = "INSERT INTO scans (time) VALUES (?)"
cursor.execute(sql, (time,))
scanID = cursor.lastrowid

liveHosts = []
localNetwork = "192.168.1.0/24"

print("starting ping scan")
nm.scan(hosts=localNetwork, arguments = "-sn")
os.system('cls' if os.name == 'nt' else 'clear')

for host in nm.all_hosts():
    if nm[host].state() == "up":
        liveHosts.append(host)

liveHosts = ' '.join(liveHosts)

print("starting detailed scan")
nm.scan(hosts=liveHosts, arguments = "-O --osscan-guess")
os.system('cls' if os.name == 'nt' else 'clear')

for host in nm.all_hosts():

    ip = None
    mac = None
    os = None
    uptime = None
    friendly_name = None

    ip = host
    dns = nm[host].hostname()
    if not dns:
        dns = None
    
    if 'mac' in nm[host]['addresses']:
        mac = nm[host]['addresses']['mac']
        
        try:
            mac_lookup = MacLookup()
            vendor = mac_lookup.lookup(mac)
            friendly_name = f"{vendor} device"
        except:
            pass
    
    # Try NetBIOS name resolution (Windows devices)
    try:
        if os.name == 'nt':  # Windows
            output = subprocess.check_output(f"nbtstat -A {ip}", shell=True).decode('utf-8', errors='ignore')
            match = re.search(r"<00>\s+UNIQUE\s+(\S+)", output)
            if match:
                netbios_name = match.group(1).strip()
                friendly_name = netbios_name
        else:  # Linux/Mac
            output = subprocess.check_output(f"nmblookup -A {ip}", shell=True).decode('utf-8', errors='ignore')
            if "<00>" in output:
                netbios_name = output.split("<00>")[0].strip()
                friendly_name = netbios_name
    except:
        pass
        
    # Try mDNS resolution (Apple/IoT devices)
    try:
        mdns_name = socket.gethostbyaddr(ip)[0]
        if mdns_name and ".local" in mdns_name:
            friendly_name = mdns_name
    except:
        pass
    
    if friendly_name and not dns:
        dns = friendly_name

    if nm[host]['osmatch']:
        os = nm[host]['osmatch'][0]['name']

    if 'uptime' in nm[host]:
        uptime = nm[host]['uptime']
        seconds = int(uptime["seconds"])
        uptime = seconds

    print(f"Host: {ip}, Name: {dns if dns else 'Unknown'}")
    
    sql = "INSERT INTO hosts (ip, mac, dns, os, uptime, scanID) VALUES (?, ?, ?, ?, ?, ?)"
    cursor.execute(sql, (ip, mac, dns, os, uptime, scanID))

print("finished!")

connection.commit()