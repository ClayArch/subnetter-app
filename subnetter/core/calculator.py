from __future__ import annotations

import ipaddress
from dataclasses import dataclass
from typing import Optional, Tuple


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
        if not isinstance(iface.ip, ipaddress.IPv4Address):
            raise ValueError("IPv6 is not supported in this tool.")
        return iface.ip, int(iface.network.prefixlen)

    if mask_input is None:
        raise ValueError("Missing subnet mask. Provide dotted mask or use IP/CIDR.")

    ip = ipaddress.IPv4Address(ip_input)
    mask_raw = mask_input.strip()
    if mask_raw.startswith("/"):
        prefix = int(mask_raw[1:])
        if not (0 <= prefix <= 32):
            raise ValueError("CIDR must be between /0 and /32.")
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