import subprocess
import socket
from scapy.all import ARP, Ether, srp, conf
import ipaddress
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
    # Auto-detect local network
    local_ip = conf.route.route("0.0.0.0")[1]
    netmask = conf.route.route("0.0.0.0")[3]
    # Convert netmask to prefix length
    prefix = ipaddress.IPv4Network(f"0.0.0.0/{netmask}").prefixlen
    network = ipaddress.IPv4Network(f"{local_ip}/{prefix}", strict=False)

    print(f"Scanning network: {network}")

    # ARP scan
    arp = ARP(pdst=str(network))
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp

    result = srp(packet, timeout=2, verbose=0)[0]

    devices = []
    for sent, received in result:
        devices.append({'ip': received.psrc, 'mac': received.hwsrc})

    print("Active devices:")
    for dev in devices:
        print(f"  {dev['ip']} → {dev['mac']}")
    return devices
def scan_network():
    print("Starting ARP scan...")
    arp_results = arp_scan()
    print("\nStarting Scapy scan...")
    scapy_results = scapy_scan()
    return arp_results, scapy_results
if __name__ == "__main__":
    scan_network()