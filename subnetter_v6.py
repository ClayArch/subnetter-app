
import sys, os
import ipaddress
from dataclasses import dataclass
from typing import Tuple, Optional

# --- Color helpers ---
try:
    import colorama  # type: ignore
    colorama.init(autoreset=True)
except Exception:
    pass

_ENABLE_COLOR = sys.stdout.isatty() and os.environ.get("NO_COLOR", "") == ""

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
FG_RED = "\033[31m"
FG_GREEN = "\033[32m"
FG_YELLOW = "\033[33m"
FG_BLUE = "\033[34m"
FG_MAGENTA = "\033[35m"
FG_CYAN = "\033[36m"

def c(text: str, code: str) -> str:
    # why: centralize color usage and fall back cleanly
    return f"{code}{text}{RESET}" if _ENABLE_COLOR else text

# --- Data model ----------------------------------------------------------------
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

# --- Core logic ----------------------------------------------------------------
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

# --- Presentation --------------------------------------------------------------
def print_report(info: SubnetInfo) -> None:
    sep = c("=" * 40, DIM)
    print("\n" + sep)

    def row(label: str, value: str, lcol: str = FG_BLUE, vcol: str = FG_GREEN) -> None:
        print(f"{c(label + ':', lcol):<20} {c(value, vcol)}")

    row("IP Address",        info.ip)
    row("CIDR Notation",     f"/{info.cidr}")
    row("Subnet Mask",       info.netmask)
    row("Wildcard Mask",     info.wildcard)
    row("Network Address",   info.network)
    row("Broadcast Address", info.broadcast)
    row("First Host",        info.first_host)
    row("Last Host",         info.last_host)

    # highlight counts; warn when unusable
    counts_color = FG_YELLOW if info.usable_hosts > 0 else FG_RED
    row("Total Addresses",   str(info.total_hosts), vcol=counts_color)
    row("Usable Hosts",      str(info.usable_hosts), vcol=counts_color)
    row("Host Bits",         str(info.host_bits), vcol=FG_YELLOW)

    print(sep)

# --- CLI loop ------------------------------------------------------------------
def main() -> None:
    print("")
    title = c("Subnetter Version 6", BOLD + FG_MAGENTA)
    print(title)
    print(c("====================", DIM))

    last_ip: Optional[str] = None
    last_mask: Optional[str] = None
    try:
        while True:
            ip_in = input(c("\nIP Address: ", FG_CYAN)).strip()
            if ip_in.lower() in {"q", "quit", "exit"}:
                break
            if ip_in == "":
                if not last_ip:
                    print(c("No previous IP to reuse.", FG_RED))
                    continue
                ip_in = last_ip

            if "/" in ip_in:
                try:
                    ip, prefix = parse_ip_and_mask(ip_in)
                    last_ip, last_mask = ip_in, None
                except Exception as e:
                    print(c(f"Error: {e}", FG_RED))
                    continue
            else:
                mask_in = input(c("Subnet Mask (255.255.255.0 or /24: ", FG_CYAN)).strip()
                if mask_in == "":
                    if not last_mask:
                        print(c("No previous mask to reuse.", FG_RED))
                        continue
                    mask_in = last_mask
                try:
                    ip, prefix = parse_ip_and_mask(ip_in, mask_in)
                    last_ip, last_mask = ip_in, mask_in
                except Exception as e:
                    print(c(f"Error: {e}", FG_RED))
                    continue

            try:
                info = compute_subnet(ip, prefix)
            except Exception as e:
                print(c(f"Error computing subnet: {e}", FG_RED))
                continue

            print_report(info)
    except KeyboardInterrupt:
        print("\nExiting...")

if __name__ == "__main__":
    main()
