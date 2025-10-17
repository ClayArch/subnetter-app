import sys
from pathlib import Path
import io
from dataclasses import asdict

import streamlit as st
import pandas as pd

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from subnetter.core.calculator import parse_ip_and_mask, compute_subnet

st.set_page_config(page_title="Subnetter", page_icon="🌐", layout="wide")

# Header
st.title("🌐 Subnetter")
st.caption("IPv4 subnet calculator — fast, accurate, shareable")

# Tabs for organization
tab1, tab2 = st.tabs(["Calculator", "Reference"])

with tab1:
    # Input section
    st.subheader("Enter Network Details")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        ip_in = st.text_input(
            "IP Address",
            placeholder="192.168.1.10 or 192.168.1.10/24",
            help="Enter an IP address with or without CIDR notation"
        )
    
    show_mask = "/" not in ip_in if ip_in else True
    mask_in = None
    
    with col2:
        if show_mask:
            mask_in = st.text_input(
                "Subnet Mask",
                placeholder="255.255.255.0 or /24",
                help="Enter dotted notation or /CIDR format"
            )
    
    # Calculate button
    if st.button("Calculate", type="primary", use_container_width=True):
        try:
            if ip_in.strip() == "":
                st.error("Please enter an IP address.")
            else:
                ip, prefix = parse_ip_and_mask(ip_in, mask_in if show_mask and mask_in else None)
                info = compute_subnet(ip, prefix)
                
                # Success indicator
                st.success("✓ Subnet calculated successfully")
                
                # Results in tabs
                result_col1, result_col2, result_col3 = st.columns(3)
                
                with result_col1:
                    st.subheader("Network Info")
                    st.metric("Network Address", info.network)
                    st.metric("Broadcast Address", info.broadcast)
                    st.metric("Subnet Mask", info.netmask)
                    st.metric("Wildcard Mask", info.wildcard)
                
                with result_col2:
                    st.subheader("Host Range")
                    st.metric("First Host", info.first_host)
                    st.metric("Last Host", info.last_host)
                    st.metric("Total Addresses", info.total_hosts)
                    st.metric("Usable Hosts", info.usable_hosts)
                
                with result_col3:
                    st.subheader("Additional Info")
                    st.metric("Your IP", info.ip)
                    st.metric("CIDR Notation", f"/{info.cidr}")
                    st.metric("Host Bits", info.host_bits)
                
                # Special note for /31
                if info.cidr == 31:
                    st.info("📌 **/31 Point-to-Point**: Both addresses are usable")
                
                # Results table
                st.divider()
                st.subheader("Full Results Table")
                
                data_dict = asdict(info)
                results_df = pd.DataFrame(
                    list(data_dict.items()),
                    columns=["Field", "Value"]
                )
                st.dataframe(results_df, use_container_width=True, hide_index=True)
                
                # Download CSV
                csv = io.StringIO()
                csv.write("field,value\n")
                for k, v in data_dict.items():
                    csv.write(f"{k},{v}\n")
                
                st.download_button(
                    label="📥 Download as CSV",
                    data=csv.getvalue(),
                    file_name="subnet_result.csv",
                    mime="text/csv",
                    use_container_width=True
                )
        
        except Exception as e:
            st.error(f"Error: {str(e)}")

with tab2:
    st.subheader("Common Subnet Masks")
    
    common_masks = {
        "/8": "255.0.0.0 (Class A)",
        "/16": "255.255.0.0 (Class B)",
        "/24": "255.255.255.0 (Class C) — Most common",
        "/25": "255.255.255.128",
        "/26": "255.255.255.192",
        "/27": "255.255.255.224",
        "/28": "255.255.255.240",
        "/30": "255.255.255.252",
        "/31": "255.255.255.254 (Point-to-Point)",
        "/32": "255.255.255.255 (Single host)",
    }
    
    for cidr, mask in common_masks.items():
        st.text(f"{cidr:5} → {mask}")
    
    st.divider()
    st.subheader("Quick Tips")
    st.markdown("""
    - **Usable hosts** = Total addresses - 2 (network & broadcast)
    - **/31 networks** have 2 usable addresses (point-to-point)
    - **/32 networks** are single hosts
    - Use **/24** for most LANs (~250 hosts)
    - Use **/30** for router links (4 addresses, 2 usable)
    """)