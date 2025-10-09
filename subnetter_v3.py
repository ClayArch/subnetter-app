def ip_to_int(ip):
    # Convert IPv4 address to integer.
    parts = list(map(int, ip.split('.')))
    return (parts[0] << 24) | (parts[1] << 16) | (parts[2] << 8) | parts[3]

def int_to_ip(ip_int):
    # Convert integer to IPv4 address.
    return ".".join(str((ip_int >> (8 * i)) & 0xFF) for i in reversed(range(4)))

def calculate_subnet(ip, mask):
    # Calculate subnet details from IP and subnet mask.
    ip_int = ip_to_int(ip)
    mask_int = ip_to_int(mask)

    # Network address
    network_int = ip_int & mask_int

    # Count leading ones in mask to determine CIDR
    leading_ones = bin(mask_int).count('1')
    host_bits = 32 - leading_ones

    # Broadcast address
    broadcast_int = network_int | ((1 << host_bits) - 1)

    return {
        'network': int_to_ip(network_int),
        'broadcast': int_to_ip(broadcast_int),
        'first_host': int_to_ip(network_int + 1),
        'last_host': int_to_ip(broadcast_int - 1),
        'host_bits': host_bits,
        'cidr': f"{leading_ones}"
    }

def main():
    print("IPv4 Subnet Calculator")
    print("======================")

    ip = input("Enter IP address (e.g., 192.168.0.10): ")
    mask = input("Enter subnet mask (e.g., 255.255.255.0): ")

    try:
        result = calculate_subnet(ip, mask)

        print("\n" + "=" * 30)
        print(f"Network Address : {result['network']}")
        print(f"Broadcast Address: {result['broadcast']}")
        print(f"First Host      : {result['first_host']}")
        print(f"Last Host       : {result['last_host']}")
        print(f"Host Bits       : {result['host_bits']}")
        print(f"CIDR Notation   : /{result['cidr']}")
        print("=" * 30)

        print("\nSubnet Explanation:")
        print("- Network Address: IP & Subnet Mask")
        print("- Broadcast Address: Network Address with all host bits set to 1")
        print("- First Host: Network Address + 1")
        print("- Last Host: Broadcast Address - 1")
        print("- Host Bits: Number of bits available for host addresses")

    except Exception as e:
        print(f"\nError: {e}")
        print("Please enter valid IPv4 addresses in correct format.")

if __name__ == "__main__":
    main()