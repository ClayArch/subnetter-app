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
st.caption("IPv4 Subnet Calculator")

# Tabs for organization
tab1, tab2, tab3 = st.tabs(["Calculator", "Reference", "Notes"])

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
                    st.subheader("Host Info")
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
                st.dataframe(
                    results_df, 
                    use_container_width=True, 
                    hide_index=True,
                    height=423
                )
                
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
        "/8": "255.0.0.0",
        "/12": "255.240.0.0",
        "/16": "255.255.0.0",
        "/24": "255.255.255.0",
        "/25": "255.255.255.128",
        "/26": "255.255.255.192",
        "/27": "255.255.255.224",
        "/28": "255.255.255.240",
        "/29": "255.255.255.248",
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

with tab3:
    st.subheader("Subnetting Fundamentals")
    
    st.markdown("""
    ### Key Concepts
    
    **CIDR Notation:** `/24` represents the number of bits in the subnet mask
    - Example: `192.168.1.0/24` means the first 24 bits identify the network
    
    **Subnet Bits vs Host Bits:**
    - Total bits in IPv4: 32
    - Subnet bits: determined by CIDR prefix
    - Host bits: 32 - CIDR prefix
    - Example: `/24` = 24 subnet bits, 8 host bits
    
    ### Subnetting Calculation Steps
    
    1. **Identify subnet prefix** — How many bits for the network?
    2. **Calculate host bits** — 32 - prefix length
    3. **Determine subnet size** — 2^(host bits)
    4. **Calculate number of subnets** — How many can you create?
    5. **List all subnets** — Find start and end addresses
    
    ### Binary Representation of Subnet Masks
                
    | Prefix | Binary Netmask | Decimal Netmask | # of Subnets | # of Hosts | 128 | 64 | 32 | 16 | 8 | 4 | 2 | 1 |
    |--------|---|---|---|---|---|---|---|---|---|---|---|---|
    | /25 | .1000 0000 | 0.128 | 2 = 2^1 | 126 = 2^7 - 2 | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
    | /26 | .1100 0000 | 0.192 | 4 = 2^2 | 62 = 2^6 - 2 | 1 | 1 | 0 | 0 | 0 | 0 | 0 | 0 |
    | /27 | .1110 0000 | 0.224 | 8 = 2^3 | 30 = 2^5 - 2 | 1 | 1 | 1 | 0 | 0 | 0 | 0 | 0 |
    | /28 | .1111 0000 | 0.24 | 16 = 2^4 | 14 = 2^4 - 2 | 1 | 1 | 1 | 1 | 0 | 0 | 0 | 0 |
    | /29 | .1111 1000 | 0.248 | 32 = 2^5 | 6 = 2^3 - 2 | 1 | 1 | 1 | 1 | 1 | 0 | 0 | 0 |
    | /30 | .1111 1100 | 0.252 | 64 = 2^6 | 2 = 2^2 - 2 | 1 | 1 | 1 | 1 | 1 | 1 | 0 | 0 |
                      
    ### Common Private IP Ranges (Classful)
    
    | Class | Range | CIDR |
    |-------|-------|------|
    | A | 10.0.0.0 — 10.255.255.255 | /8 |
    | B | 172.16.0.0 — 172.31.255.255 | /12 |
    | C | 192.168.0.0 — 192.168.255.255 | /16 |
    
    ### Subnet Mask Reference
    
    | Prefix | Dotted Notation | Host Bits | Total Addresses | Usable Hosts |
    |--------|-----------------|-----------|-----------------|--------------|
    | /8 | 255.0.0.0 | 24 | 16,777,216 | 16,777,214 |
    | /12 | 255.240.0.0 | 20 | 1,048,576 | 1,048,574 |
    | /16 | 255.255.0.0 | 16 | 65,536 | 65,534 |
    | /20 | 255.255.240.0 | 12 | 4,096 | 4,094 |
    | /24 | 255.255.255.0 | 8 | 256 | 254 |
    | /25 | 255.255.255.128 | 7 | 128 | 126 |
    | /26 | 255.255.255.192 | 6 | 64 | 62 |
    | /27 | 255.255.255.224 | 5 | 32 | 30 |
    | /28 | 255.255.255.240 | 4 | 16 | 14 |
    | /29 | 255.255.255.248 | 3 | 8 | 6 |
    | /30 | 255.255.255.252 | 2 | 4 | 2 |
    | /31 | 255.255.255.254 | 1 | 2 | 2 |
    | /32 | 255.255.255.255 | 0 | 1 | 1 |
    
    ### Special Cases
    
    - **/31 (Point-to-Point):** Both addresses are usable (RFC 3021) — used for router links
    - **/32 (Host):** Single IP address, typically used for loopback or specific host routes
    - **/0 (Any):** Matches all IPv4 addresses
    
    ### Example Calculation
    
    IP address `192.168.200.139` with subnet mask `/27`
    
    - Host bits: 32 - 27 = 5
    - Total addresses: 2^5 = 32
    - Usable hosts: 32 - 2 = 30
    - Network address: 192.168.200.128
    - Broadcast address: 192.168.200.159
    - First host: 192.168.200.129
    - Last host: 192.168.200.158
    """)