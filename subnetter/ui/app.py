import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import io
from dataclasses import asdict

import streamlit as st

from subnetter.core.calculator import parse_ip_and_mask, compute_subnet


st.set_page_config(page_title="Subnetter", page_icon="🌐", layout="centered")
st.title("Subnetter")
st.caption("IPv4 Subnet Calculator")

# Inputs
with st.form("input_form", clear_on_submit=False):
    ip_in = st.text_input("IP Address (or IP/CIDR)", placeholder="192.168.1.10 or 192.168.1.10/24", value="")
    show_mask = "/" not in ip_in if ip_in else True
    mask_in = None
    if show_mask:
        mask_in = st.text_input("Subnet Mask (dotted or /CIDR)", placeholder="255.255.255.0 or /24", value="")
    submitted = st.form_submit_button("Calculate")

if submitted:
    try:
        if ip_in.strip() == "":
            st.error("Please enter an IP address or IP/CIDR.")
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