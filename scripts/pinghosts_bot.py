import subprocess
import re
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from colorama import init, Fore, Style

# Initialize colorama
init()

def read_hosts_file():
    """Read the /etc/hosts file and return a list of valid hostnames or IP addresses."""
    hosts = []
    with open('/etc/hosts', 'r') as file:
        for line in file:
            line = line.strip()
            # Skip comments and empty lines
            if line and not line.startswith('#'):
                # Split line by whitespace and take the first element (IP address)
                parts = re.split(r'\s+', line)
                if len(parts) > 1:
                    ip_address = parts[0]
                    # Skip local and IPv6 addresses
                    if ip_address.startswith("127.") or ip_address == "::1" or ip_address.startswith("fe00::") or ip_address.startswith("ff"):
                        continue
                    hosts.append(parts[1])
    return hosts

def ping_host(hostname):
    """Ping a host for 5 seconds and return ping details."""
    try:
        result = subprocess.run(
            ['ping', '-c', '5', '-W', '1', hostname],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        output = result.stdout.decode('utf-8')
        
        # Check if ping was successful
        if result.returncode == 0:
            # Extract average time and packet loss
            avg_time_match = re.search(r'rtt min/avg/max/mdev = [^/]+/([^/]+)/', output)
            avg_time = avg_time_match.group(1) if avg_time_match else "N/A"

            packet_loss_match = re.search(r'(\d+)% packet loss', output)
            packet_loss = packet_loss_match.group(1) if packet_loss_match else "N/A"
            
            return hostname, True, avg_time, packet_loss
        else:
            return hostname, False, "N/A", "N/A"
    except Exception as e:
        print(f"Error pinging {hostname}: {e}")
        return hostname, False, "N/A", "N/A"

def send_telegram_message(bot_token, chat_id, message):
    """Send a message to a Telegram chat via bot."""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "HTML"
    }
    response = requests.post(url, json=payload)
    return response.json()

def notify_results_via_telegram(results):
    bot_token = '你的bot token'
    chat_id = '你的chat id'
    message = "<b>Ping Test Results:</b>\n"
    for host, result in results.items():
        status = "Reachable" if result["status"] == "Reachable" else "Unreachable"
        message += f"{host}: {status} - time: {result['time']} ms, packet loss: {result['packet_loss']}%\n"
    send_telegram_message(bot_token, chat_id, message)

def main():
    hosts = read_hosts_file()
    results = {}
    
    with ThreadPoolExecutor(max_workers=len(hosts)) as executor:
        futures = {executor.submit(ping_host, host): host for host in hosts}
        for future in as_completed(futures):
            host, reachable, avg_time, packet_loss = future.result()
            results[host] = {
                "status": "Reachable" if reachable else "Unreachable",
                "time": avg_time,
                "packet_loss": packet_loss
            }
    
    print("Ping Test Results:")
    for host, result in results.items():
        status_color = Fore.GREEN if result["status"] == "Reachable" else Fore.RED
        print(f"{Fore.YELLOW}{host}: {status_color}{result['status']} - time: {result['time']} ms, packet loss: {result['packet_loss']}%{Style.RESET_ALL}")
    
    notify_results_via_telegram(results)

if __name__ == "__main__":
    main()
