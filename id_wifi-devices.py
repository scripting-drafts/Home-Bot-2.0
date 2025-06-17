import subprocess
import socket
import time
from scapy.all import ARP, Ether, srp
from colorama import Fore, Style, init

init(autoreset=True)

def ping_scan(subnet):
    """Use Nmap to find active IPs in subnet via ping scan."""
    try:
        result = subprocess.check_output(
            ["nmap", "-sn", subnet],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
    except subprocess.CalledProcessError:
        print(Fore.RED + "Error: Failed to run nmap ping scan.")
        return []

    active_ips = []
    for line in result.splitlines():
        if line.startswith("Nmap scan report for"):
            ip = line.split()[-1]
            active_ips.append(ip)
    return active_ips

def get_mac(ip):
    """Get MAC address using ARP request (via scapy)."""
    arp = ARP(pdst=ip)
    ether = Ether(dst="ff:ff:ff:ff:ff:ff")
    packet = ether / arp
    result = srp(packet, timeout=2, verbose=False)[0]
    for _, received in result:
        return received.hwsrc
    return "Unknown"

def detect_os(ip):
    """Run OS detection using nmap -O"""
    try:
        result = subprocess.check_output(
            ["nmap", "-O", ip],
            stderr=subprocess.DEVNULL,
            universal_newlines=True
        )
        for line in result.splitlines():
            if "OS details:" in line:
                return line.split("OS details:")[1].strip()
            elif "Running:" in line:
                return line.split("Running:")[1].strip()
    except:
        pass
    return "Unknown"

def get_hostname(ip):
    try:
        return socket.gethostbyaddr(ip)[0]
    except:
        return "Unknown"

def scan_devices(subnet):
    devices = {}
    active_ips = ping_scan(subnet)

    for ip in active_ips:
        mac = get_mac(ip)
        hostname = get_hostname(ip)
        os_info = detect_os(ip)

        devices[mac] = {
            "ip": ip,
            "hostname": hostname,
            "os": os_info
        }

    return devices

def display_devices(devices):
    print("\n📡 Current Devices on Network:")
    print("-" * 70)
    print(f"{'IP Address':<16} {'MAC Address':<18} {'Hostname':<20} {'OS'}")
    print("-" * 70)
    for mac, info in devices.items():
        print(f"{info['ip']:<16} {mac:<18} {info['hostname']:<20} {info['os']}")
    print("-" * 70)

def print_device_event(event_type, mac, info):
    symbol = "+" if event_type == "joined" else "-"
    color = Fore.GREEN if event_type == "joined" else Fore.RED
    print(color + f"[{symbol}] {event_type.upper():7} | {info['ip']} ({mac}) - {info['hostname']} | OS: {info['os']}")

def monitor_network(subnet, interval=60):
    print(f"🌐 Monitoring devices on {subnet} every {interval} seconds...\n")

    known_devices = scan_devices(subnet)
    display_devices(known_devices)

    try:
        while True:
            current_devices = scan_devices(subnet)

            new_macs = current_devices.keys() - known_devices.keys()
            for mac in new_macs:
                print_device_event("joined", mac, current_devices[mac])

            left_macs = known_devices.keys() - current_devices.keys()
            for mac in left_macs:
                print_device_event("left", mac, known_devices[mac])

            known_devices = current_devices
            time.sleep(interval)
    except KeyboardInterrupt:
        print("\n👋 Monitoring stopped.")

if __name__ == "__main__":
    subnet = "192.168.1.0/24"  # Change to match your network
    monitor_network(subnet, interval=90)  # Interval increased for OS scan time
