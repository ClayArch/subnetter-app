# File: subnetter_app.py
"""
Subnetter App (Streamlit)
Run:    pip install streamlit
        streamlit run subnetter_app.py
"""

from __future__ import annotations

import io
import ipaddress
from dataclasses import dataclass, asdict
from typing import Optional, Tuple

import streamlit as st


# ---------------------------- Core logic (your v6) ----------------------------

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


# ------------------------------ Streamlit UI ----------------------------------

st.set_page_config(page_title="Subnetter", page_icon="🌐", layout="centered")
st.title("Subnetter")
st.caption("IPv4 subnet calculator — shareable, simple, accurate.")

# Inputs
with st.form("input_form", clear_on_submit=False):
    ip_in = st.text_input("IP (or IP/CIDR)", placeholder="192.168.1.10 or 192.168.1.10/24", value="")
    show_mask = "/" not in ip_in if ip_in else True
    mask_in = None
    if show_mask:
        mask_in = st.text_input("Subnet Mask (dotted or /CIDR)", placeholder="255.255.255.0 or /24", value="")
    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        if ip_in.strip() == "":
            st.error("Please enter an IP or IP/CIDR.")
        else:
            ip, prefix = parse_ip_and_mask(ip_in, mask_in if show_mask and mask_in else None)
            info = compute_subnet(ip, prefix)

            # Output columns
            c1, c2 = st.columns(2)
            with c1:
                st.subheader("Addresses")
                st.write("**IP Address**:", info.ip)
                st.write("**CIDR**:", f"/{info.cidr}")
                st.write("**Subnet Mask**:", info.netmask)
                st.write("**Wildcard Mask**:", info.wildcard)
                label = "Peer Address (/31)" if info.cidr == 31 else "Broadcast Address"
                st.write("**Network Address**:", info.network)
                st.write(f"**{label}**:", info.broadcast)
            with c2:
                st.subheader("Hosts")
                st.write("**First Host**:", info.first_host)
                st.write("**Last Host**:", info.last_host)
                st.metric("Total Addresses", f"{info.total_hosts}")
                st.metric("Usable Hosts", f"{info.usable_hosts}")
                st.write("**Host Bits**:", info.host_bits)

            # Extra note for /31
            if info.cidr == 31:
                st.info("`/31` point-to-point: both addresses are usable (RFC 3021).")

            # Download CSV
            csv = io.StringIO()
            data = asdict(info)
            csv.write("field,value\n")
            for k, v in data.items():
                csv.write(f"{k},{v}\n")
            st.download_button("Download results as CSV", csv.getvalue(), file_name="subnet_result.csv", mime="text/csv")

    except Exception as e:
        st.error(str(e))

st.divider()
st.caption("Tip: share this file; classmates run `pip install streamlit` then `streamlit run subnetter_app.py`.")