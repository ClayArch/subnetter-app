# Subnetter
import ipaddress
from dataclasses import dataclass
from typing import Tuple, Optional

@dataclass(frozen=True)
class SubnetInfo:
    ip: str
    cidr: int
    network: str
    broadcast: str
    netmask: str
    wildcard: str
    first_host: str
    last_host: str
    total_hosts: int
    usable_hosts: int
    host_bits: int

def parse_ip_and_mask(ip_input: str, mask_input: Optional[str] = None) -> Tuple[ipaddress.IPv4Address, int]:
    ip_input = ip_input.strip()
    if "/" in ip_input and mask_input is None:
        iface = ipaddress.ip_interface(ip_input)
        return ipaddress.IPv4Address(iface.ip), int(iface.network.prefixlen)
    if mask_input is None:
        raise ValueError("Missing subnet mask. Provide dotted mask or use IP/CIDR.")
    ip = ipaddress.IPv4Address(ip_input)
    mask_raw = mask_input.strip()
    if mask_raw.startswith("/"):
        prefix = int(mask_raw[1:])
        if not (0 <= prefix <= 32):
            raise ValueError("CIDR must be /0..../32")
        return ip, prefix
    dummy = ipaddress.ip_network(f"0.0.0.0/{mask_raw}", strict=False)
    return ip, int(dummy.prefixlen)

def wildcard_from_netmask(mask: ipaddress.IPv4Address) -> ipaddress.IPv4Address:
    return ipaddress.IPv4Address(int(mask) ^ 0xFFFFFFFF)

def compute_subnet(ip: ipaddress.IPv4Address, prefix: int) -> SubnetInfo:
    net = ipaddress.IPv4Network((ip, prefix), strict=False)
    network = net.network_address
    broadcast = net.broadcast_address
    mask = net.netmask
    wildcard = wildcard_from_netmask(mask)
    host_bits = 32 - prefix
    total = 1 << host_bits
    if prefix == 32:
        usable = 1
        first_host = last_host = ip
    elif prefix == 31:
        usable = 2
        first_host = network
        last_host = broadcast
    else:
        usable = max(total - 2, 0)
        first_host = network + 1 if total >= 4 else network
        last_host = broadcast - 1 if total >= 4 else broadcast
    return SubnetInfo(
        ip=str(ip),
        cidr=prefix,
        network=str(network),
        broadcast=str(broadcast),
        netmask=str(mask),
        wildcard=str(wildcard),
        first_host=str(first_host),
        last_host=str(last_host),
        total_hosts=total,
        usable_hosts=usable,
        host_bits=host_bits,
    )

def main() -> None:
    print("")
    print("Subnetter Version 5")
    print("====================")
    last_ip: Optional[str] = None
    last_mask: Optional[str] = None
    try:
        while True:
            ip_in = input("\nIP Address: ").strip()
            if ip_in.lower() in {"q", "quit", "exit"}:
                break
            if ip_in == "":
                if not last_ip:
                    print("No previous IP to reuse.")
                    continue
                ip_in = last_ip

            if "/" in ip_in:
                try:
                    ip, prefix = parse_ip_and_mask(ip_in)
                    last_ip, last_mask = ip_in, None  # stored for reuse
                except Exception as e:
                    print(f"Error: {e}")
                    continue
            else:
                mask_in = input("Subnet Mask (255.255.255.0 or /24): ").strip()
                if mask_in == "":
                    if not last_mask:
                        print("No previous mask to reuse.")
                        continue
                    mask_in = last_mask
                try:
                    ip, prefix = parse_ip_and_mask(ip_in, mask_in)
                    last_ip, last_mask = ip_in, mask_in
                except Exception as e:
                    print(f"Error: {e}")
                    continue

            try:
                info = compute_subnet(ip, prefix)
            except Exception as e:
                print(f"Error computing subnet: {e}")
                continue

            print("\n" + "=" * 40)
            print(f"IP Address        : {info.ip}")
            print(f"CIDR Notation     : /{info.cidr}")
            print(f"Subnet Mask       : {info.netmask}")
            print(f"Wildcard Mask     : {info.wildcard}")
            print(f"Network Address   : {info.network}")
            print(f"Broadcast Address : {info.broadcast}")
            print(f"First Host        : {info.first_host}")
            print(f"Last Host         : {info.last_host}")
            print(f"Total Addresses   : {info.total_hosts}")
            print(f"Usable Hosts      : {info.usable_hosts}")
            print(f"Host Bits         : {info.host_bits}")
            print("=" * 40)
    except KeyboardInterrupt:
        print("\nExiting...")  

if __name__ == "__main__":
    main()
