import os
import subprocess
import time

def get_syn_recv_connections():
    # Get the output of the 'netstat' command and find all connections with status 'SYN_RECV'
    netstat_output = subprocess.check_output(["netstat", "-ant"]).decode()
    syn_recv_lines = [line for line in netstat_output.split("\n") if "SYN_RECV" in line]

    # Create a dictionary where the key is the IP address and the value is the number of 'SYN_RECV' connections
    connections = {}
    for line in syn_recv_lines:
        parts = line.split()
        if len(parts) >= 5:
            ip = parts[4].split(":")[0]
            connections[ip] = connections.get(ip, 0) + 1

    return connections

def block_ip(ip):
    # Create an iptables rule to block the IP address for 3 minutes
    os.system(f"iptables -A INPUT -s {ip} -j DROP")
    time.sleep(180) # Wait for 3 minutes
    os.system(f"iptables -D INPUT -s {ip} -j DROP")

def main():
    # Get all connections with status 'SYN_RECV'
    syn_recv_connections = get_syn_recv_connections()

    # Write the results to a file
    with open("/var/log/ddos-log.txt", "w") as f:
        f.write("IP Address\tSYN_RECV Count\n")
        for ip, count in syn_recv_connections.items():
            f.write(f"{ip}\t{count}\n")

            # Block IP addresses of connections that appear more than N times
            if count >= 10:
                block_ip(ip)

if __name__ == "__main__":
    main()
