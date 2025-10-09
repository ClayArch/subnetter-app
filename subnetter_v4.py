# The Subnetter Program

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
    """
    Parse inputs to (IPv4Address, prefixlen).
    Why: Centralized validation + support for both CIDR and dotted masks.
    """
    ip_input = ip_input.strip()
    if "/" in ip_input and mask_input is None:
        # e.g., "192.168.1.10/24"
        try:
            iface = ipaddress.ip_interface(ip_input)
            return ipaddress.IPv4Address(iface.ip), int(iface.network.prefixlen)
        except Exception as exc:
            raise ValueError(f"Invalid 'IP/CIDR' input: {ip_input}") from exc

    if mask_input is None:
        raise ValueError("Missing subnet mask. Provide dotted mask or use IP/CIDR.")

    # Separate IP and dotted/CIDR mask
    try:
        ip = ipaddress.IPv4Address(ip_input)
    except Exception as exc:
        raise ValueError(f"Invalid IPv4 address: {ip_input}") from exc

    mask_raw = mask_input.strip()
    if mask_raw.startswith("/"):
        try:
            prefix = int(mask_raw[1:])
            if not (0 <= prefix <= 32):
                raise ValueError
            return ip, prefix
        except Exception as exc:
            raise ValueError(f"Invalid CIDR mask: {mask_raw}") from exc

    # Dotted-decimal mask -> prefixlen; ipaddress will enforce contiguity
    try:
        dummy = ipaddress.ip_network(f"0.0.0.0/{mask_raw}", strict=False)
        return ip, int(dummy.prefixlen)
    except Exception as exc:
        raise ValueError(f"Invalid dotted mask (must be contiguous): {mask_raw}") from exc


def wildcard_from_netmask(mask: ipaddress.IPv4Address) -> ipaddress.IPv4Address:
    """Compute wildcard mask (inverse of netmask)."""
    return ipaddress.IPv4Address(int(mask) ^ 0xFFFFFFFF)


def compute_subnet(ip: ipaddress.IPv4Address, prefix: int) -> SubnetInfo:
    """
    Produce full subnet information using ipaddress.
    Why: Correct handling of edge cases (/31, /32) and validation.
    """
    net = ipaddress.IPv4Network((ip, prefix), strict=False)
    network = net.network_address
    broadcast = net.broadcast_address
    mask = net.netmask
    wildcard = wildcard_from_netmask(mask)

    host_bits = 32 - prefix
    total = 1 << host_bits

    # Usable host address rules: /31 has 2 usable, /32 has 1, others subtract network+broadcast.
    if prefix == 32:
        usable = 1
        first_host = last_host = ip
    elif prefix == 31:
        usable = 2
        first_host = network
        last_host = broadcast
    else:
        usable = max(total - 2, 0)
        # Guard tiny nets where +1/-1 would wrap
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


# --- Optional: bitwise helpers for learning -----------------------------------
def ip_to_int(ip: str) -> int:
    parts = ip.split(".")
    if len(parts) != 4:
        raise ValueError("IPv4 must have four octets")
    n = 0
    for p in parts:
        o = int(p)
        if not (0 <= o <= 255):
            raise ValueError("Octet out of range")
        n = (n << 8) | o
    return n


def int_to_ip(n: int) -> str:
    return ".".join(str((n >> (8 * i)) & 0xFF) for i in reversed(range(4)))


def dotted_mask_to_prefix(mask: str) -> int:
    try:
        return int(ipaddress.ip_network(f"0.0.0.0/{mask}", strict=False).prefixlen)
    except Exception as exc:
        raise ValueError("Non-contiguous or invalid mask") from exc


def manual_compute_subnet(ip_str: str, mask_str_or_cidr: str) -> SubnetInfo:
    """
    Manual/bitwise path to mirror ipaddress results.
    """
    ip = ipaddress.IPv4Address(ip_str)  # reuse parsing for safety
    if mask_str_or_cidr.startswith("/"):
        prefix = int(mask_str_or_cidr[1:])
    else:
        prefix = dotted_mask_to_prefix(mask_str_or_cidr)

    ip_int = int(ip)
    mask_int = (0xFFFFFFFF << (32 - prefix)) & 0xFFFFFFFF if prefix > 0 else 0
    network_int = ip_int & mask_int
    host_bits = 32 - prefix
    total = 1 << host_bits
    broadcast_int = (network_int | ((1 << host_bits) - 1)) & 0xFFFFFFFF

    if prefix == 32:
        first = last = ip_int
        usable = 1
    elif prefix == 31:
        first = network_int
        last = broadcast_int
        usable = 2
    else:
        first = network_int + 1 if total >= 4 else network_int
        last = broadcast_int - 1 if total >= 4 else broadcast_int
        usable = max(total - 2, 0)

    netmask_int = mask_int
    wildcard_int = (~netmask_int) & 0xFFFFFFFF

    return SubnetInfo(
        ip=str(ip),
        cidr=prefix,
        network=int_to_ip(network_int),
        broadcast=int_to_ip(broadcast_int),
        netmask=int_to_ip(netmask_int),
        wildcard=int_to_ip(wildcard_int),
        first_host=int_to_ip(first),
        last_host=int_to_ip(last),
        total_hosts=total,
        usable_hosts=usable,
        host_bits=host_bits,
    )


# --- CLI ----------------------------------------------------------------------
def main() -> None:
    print("Subnetter Version 4")
    print("======================")
    ip_in = input("Enter IP (e.g., 192.168.0.10 or 192.168.0.10/24): ").strip()

    # Allow either single field with CIDR or separate mask prompt.
    if "/" in ip_in:
        try:
            ip, prefix = parse_ip_and_mask(ip_in)
        except Exception as e:
            print(f"\nError: {e}")
            return
    else:
        mask_in = input("Enter subnet mask (e.g., 255.255.255.0 or /24): ").strip()
        try:
            ip, prefix = parse_ip_and_mask(ip_in, mask_in)
        except Exception as e:
            print(f"\nError: {e}")
            return

    try:
        info = compute_subnet(ip, prefix)
    except Exception as e:
        print(f"\nError computing subnet: {e}")
        return

    print("\n" + "=" * 40)
    print(f"IP Address       : {info.ip}")
    print(f"CIDR Notation    : /{info.cidr}")
    print(f"Subnet Mask      : {info.netmask}")
    print(f"Wildcard Mask    : {info.wildcard}")
    print(f"Network Address  : {info.network}")
    print(f"Broadcast Address: {info.broadcast}")
    print(f"First Host       : {info.first_host}")
    print(f"Last Host        : {info.last_host}")
    print(f"Total Addresses  : {info.total_hosts}")
    print(f"Usable Hosts     : {info.usable_hosts}")
    print(f"Host Bits        : {info.host_bits}")
    print("=" * 40)


if __name__ == "__main__":
    main()
