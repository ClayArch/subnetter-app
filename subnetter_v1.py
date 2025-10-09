def calculate_subnet(ip, mask):
    ip_parts = list(map(int, ip.split('.')))
    mask_parts = list(map(int, mask.split('.')))
    
    # Calculate network address
    network_parts = [ip_parts[i] & mask_parts[i] for i in range(4)]
    network_address = ".".join(str(x) for x in network_parts)
    
    # Calculate broadcast address
    broadcast_parts = network_parts.copy()
    broadcast_parts[-1] = 255
    broadcast_address = ".".join(str(x) for x in broadcast_parts)
    
    # Calculate number of hosts
    # Convert mask to 32-bit integer
    mask_int = (mask_parts[0] << 24) | (mask_parts[1] << 16) | (mask_parts[2] << 8) | mask_parts[3]
    
    # Count leading 1s
    leading_ones = 0
    for bit in bin(mask_int)[2:].zfill(32):
        if bit == '1':
            leading_ones += 1
        else:
            break
    
    host_bits = 32 - leading_ones
    num_hosts = (2 ** host_bits) - 2
    return network_address, broadcast_address, num_hosts

def main():
    print("Subnet Calculator")
    ip = input("Enter IP address: ")
    mask = input("Enter subnet mask (e.g., 255.255.255.0): ")
    
    network_address, broadcast_address, num_hosts = calculate_subnet(ip, mask)
    
    print(f"\nNetwork Address: {network_address}")
    print(f"Broadcast Address: {broadcast_address}")
    print(f"Number of Hosts: {num_hosts}")

if __name__ == "__main__":
    main()
