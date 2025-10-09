def ip_to_int(ip):
    """Convert IPv4 address to integer"""
    parts = list(map(int, ip.split('.')))
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

def int_to_ip(ip_int):
    """Convert integer to IPv4 address"""
    a = (ip_int >> 24) & 0xFF
    b = (ip_int >> 16) & 0xFF
    c = (ip_int >> 8) & 0xFF
    d = ip_int & 0xFF
    return f"{a}.{b}.{c}.{d}"

def calculate_subnet(ip, mask):
    """Calculate subnet information"""
    ip_int = ip_to_int(ip)
    mask_int = ip_to_int(mask)
    
    # Calculate network address
    network_int = ip_int & mask_int
    
    # Count leading ones in mask (for CIDR)
    leading_ones = 0
    for i in range(32):
        if mask_int & (1 << (31 - i)):
            leading_ones += 1
        else:
            break
    
    host_bits = 32 - leading_ones
    broadcast_int = network_int | ((1 << host_bits) - 1)
    
    # Convert to human-readable format
    network_addr = int_to_ip(network_int)
    broadcast_addr = int_to_ip(broadcast_int)
    first_host = int_to_ip(network_int + 1)
    last_host = int_to_ip(broadcast_int - 1)
    
    return {
        'network': network_addr,
        'broadcast': broadcast_addr,
        'first_host': first_host,
        'last_host': last_host,
        'host_bits': host_bits,
        'cidr': f"{host_bits}/"
    }

def main():
    print("IPv4 Subnet Calculator")
    print("======================")
    
    ip = input("Enter IP address (e.g., 192.168.1.10): ")
    mask = input("Enter subnet mask (e.g., 255.255.255.0): ")
    
    try:
        result = calculate_subnet(ip, mask)
        print("\n" + "="*30)
        print(f"Network Address: {result['network']}")
        print(f"Broadcast Address: {result['broadcast']}")
        print(f"First Host: {result['first_host']}")
        print(f"Last Host: {result['last_host']}")
        print(f"Host Bits: {result['host_bits']}")
        print(f"CIDR: {result['cidr']}")
        print("="*30)
        
        # Short explanation
        print("\nSubnet Explanation:")
        print("- Network Address: IP & Subnet Mask")
        print("- Broadcast Address: Network Address with all host bits set to 1")
        print("- First Host: Network Address + 1")
        print("- Last Host: Broadcast Address - 1")
        print("- Host Bits: Number of bits available for host addresses")
        
    except Exception as e:
        print(f"Error: {e}")
        print("Please enter valid IPv4 addresses with correct format")

if __name__ == "__main__":
    main()
