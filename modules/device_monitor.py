import sys
import os
import time
import requests
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from database import db_manager
import subprocess
import socket
from scapy.all import ARP, Ether, srp, conf
import ipaddress
import psutil
from socket import AF_INET
def arp_scan ():
    try:
        result = subprocess.run(['arp', '-a'] , capture_output= True, text=True)
        lines = result.stdout.splitlines()
    except Exception as e:
        print(f"Error executing arp command: {e}")
        return []
    output = []
    for line in lines:
        if 'dynamic' in line:
            ip, mac = line.split()[:2]
            try:
                hostname = socket.gethostbyaddr(ip)[0]
            except socket.herror as e:
                hostname = "Unknown"
            output.append({"ip": ip, "mac": mac, "hostname": hostname})
    return output

def scapy_scan():
    # # Auto-detect local network
    # local_ip = conf.route.route("0.0.0.0")[1]
    # netmask = conf.route.route("0.0.0.0")[3]
    # # Convert netmask to prefix length
    # prefix = ipaddress.IPv4Network(f"0.0.0.0/{netmask}").prefixlen
    # network = ipaddress.IPv4Network(f"{local_ip}/{prefix}", strict=False)
    #------------------------useless code above------------------------
    network = get_local_network()
    if not network:
        print("Could not determine local network. Please check your network settings.")
        return []

    print(f"Scanning network: {network}")

    # ARP scan
    arp = ARP(pdst=str(network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, verbose=0)[0]

    devices = []
    for sent, received in result:
        ip = received.psrc
        mac = received.hwsrc
        try:
            hostname = socket.gethostbyaddr(ip)[0]
        except socket.herror:
            hostname = "Unknown"
        devices.append({'ip': ip, 'mac': mac, 'hostname': hostname})
    print("Active devices:")
    for dev in devices:
        print(f"  {dev['ip']} → {dev['mac']} (Hostname: {dev['hostname']})")
    return devices
def scan_network():
    # print("Starting ARP scan...")
    # arp_results = arp_scan()
    # print("\nStarting Scapy scan...")
    # scapy_results = scapy_scan()
    # return arp_results, scapy_results
    # ---------Try Scapy scan first, if it fails , fall back to ARP scan -----------------
    try:
        print("\nStarting Scapy scan...")
        devices = scapy_scan()
    except :
        print("Scapy scan failed, falling back to ARP scan...")
        devices = arp_scan()
    scanned_macs = []
    for device in devices:
        vendor = get_vendor(device['mac'])
        time.sleep(1)  # To avoid hitting API rate limits
        db_manager.insert_device(
            ip_address=device['ip'],
            mac_address=device['mac'],
            host_name=device['hostname'],
            vendor=vendor,
            device_type="Unknown"
        )
        scanned_macs.append(device['mac'])
    db_manager.mark_inactive_devices(scanned_macs)
    return devices

def get_local_network():
    for name, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family == AF_INET:
                ip = addr.address
                # Skip APIPA and loopback addresses
                if ip.startswith("169.254.") or ip == "127.0.0.1":
                    continue
                if ip.startswith("169.254.") or ip == "127.0.0.1" or ip.startswith("192.168.10."):
                    continue
                # Return the first valid interface found
                network = ipaddress.IPv4Interface(f"{ip}/{addr.netmask}").network
                return str(network)
    return None  # is not found , return none here 
def get_vendor(mac_address: str) -> str:
    try:
        mac_prefix = mac_address[:8]
        response = requests.get(f"https://api.macvendors.com/{mac_prefix}")
        if response.status_code == 200:
            return response.text  # ← return not print!
        return "Unknown"
    except requests.RequestException:
        return "Unknown"
if __name__ == "__main__":
    scan_network()