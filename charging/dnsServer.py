from dnslib import DNSRecord, QTYPE, RR, AAAA, TXT
from dnslib.server import DNSServer, BaseResolver
import itertools
from flask import Flask, request, jsonify
from threading import Thread

# List to store the IP addresses of available servers
server_pool = {}
servers_data = {}

class RoundRobinResolver(BaseResolver):
    def __init__(self):
        self.serversCycle = {}  # Create a round-robin cycle of server data

    def resolve(self, request, handler):
        reply = request.reply()
        qname = request.q.qname
        qtype = QTYPE[request.q.qtype]
        print(f"Received request for: {qname}, type: {qtype}")

        if qtype == 'AAAA' and server_pool:
            if str(qname)[:-1] not in self.serversCycle.keys() and str(qname)[:-1] in server_pool.keys():
                try:
                    self.serversCycle[str(qname)[:-1]] = itertools.cycle(server_pool[str(qname)[:-1]])  
                except Exception as e:
                    print(e)
            if str(qname)[:-1] in server_pool.keys():
                next_server = next(self.serversCycle[str(qname)[:-1]]) 
                server_data_str = str(servers_data[next_server])
                print(f"Routing request to server: {next_server}")
                print(f"Data: {servers_data[next_server]}")
                reply.add_answer(RR(qname, QTYPE.AAAA, rdata=AAAA(next_server), ttl=60))
                reply.add_answer(RR(qname, QTYPE.TXT, rdata=TXT(server_data_str), ttl=60))
                print(f"Adding TXT record: {server_data_str}")

        return reply

def register_server(ip_address, port0, port1, port2, port3, port4, port5, port6, port7, url):
    """Registers a new server with its IP address, ports, and their usage."""
    server_data = {
        'ip_address': ip_address,
        'port0': port0,
        'port1': port1,
        'port2': port2,
        'port3': port3,
        'port4': port4,
        'port5': port5,
        'port6': port6,
        'port7': port7,
    }
    if url not in server_pool.keys():
        server_pool[url] = []
    if ip_address not in server_pool[url]:
        server_pool[url].append(ip_address)
    servers_data[ip_address]= server_data
    print(f"Server {ip_address} registered with ports: {port0}, {port1}, {port2}, {port3}, {port4}, {port5}, {port6}, {port7}")

def start_dns_server():
    resolver = RoundRobinResolver()

    # Create the server, listening on all IPv6 addresses "::" on port 53 for both TCP and UDP
    udp_server = DNSServer(resolver, port=53, address="::", tcp=False)
    tcp_server = DNSServer(resolver, port=53, address="::", tcp=True)

    # Start both servers
    udp_server.start_thread()  # UDP6
    tcp_server.start_thread()  # TCP6

    print("DNS server running with UDP6 and TCP6 support...")

# Flask app to handle server registration
app = Flask(__name__)

@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    ip_address = data.get('ip_address')
    port0 = data.get('port0') 
    port1 = data.get('port1') 
    port2 = data.get('port2') 
    port3 = data.get('port3')
    port4 = data.get('port4') 
    port5 = data.get('port5') 
    port6 = data.get('port6') 
    port7 = data.get('port7')  
    url = data.get('url') 

    if ip_address and port0 and port1 and port2 and port3 and port4 and port5 and port6 and port7:
        register_server(ip_address, port0, port1, port2, port3, port4, port5, port6, port7, url)
        print(f'Registered servers: {server_pool}')
        return jsonify({"message": f"Server {ip_address} registered successfully with ports: {port0}, {port1}, {port2}, {port3}, {port4}, {port5}, {port6}, {port7} and URL: {url}"}), 200
    return jsonify({"error": "Invalid request"}), 400

if __name__ == '__main__':
    # Start the DNS server in a separate thread
    dns_thread = Thread(target=start_dns_server)
    dns_thread.start()

    # Start the Flask app to handle registration
    app.run(host="::", port=5000, debug=True, use_reloader=False)

