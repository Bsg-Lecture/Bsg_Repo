from ipmininet.iptopo import IPTopo
from ipmininet.host import IPHost
from topologies.customHosts import Server, Client, DNS, name_generator

import yaml

class CustomTopology(IPTopo):
    def build(self, *args, **kwargs):

        routers = {}
        switches = {}
        servers = {}
        clients = {}
        hosts = {}
        dns = {}

        with open(f'charging/ipmininet/topologies/customTopo_config.yaml', 'r') as file:
            config = yaml.safe_load(file)
        
        if config['switches'] != None:
            # Add a switches
            for switch in config['switches']:
                S = {}
                for element in config['switches'][switch]:
                    S[element] = config["switches"][switch][element]
                switches[S['name']] = self.addSwitch(S['name'])
        
        if config['routers'] != None:
            # Add a routers
            for router in config['routers']:
                R = {}
                for element in config['routers'][router]:
                    R[element] = config['routers'][router][element]
                routers[R['name']] = self.addRouter(R['name'])
            
        if config['hosts'] != None:
            # Add a hosts
            for host in config['hosts']:
                H = {}
                for element in config['hosts'][host]:
                    H[element] = config['hosts'][host][element]
                hosts[H['name']] = self.addHost(H['name'])
        
        if config['servers'] != None:
            # Add server hosts
            for server in config['servers']:
                SE = {}
                for element in config['servers'][server]:
                    SE[element] = config["servers"][server][element]
                if 'url' not in SE.keys():
                    servers[SE['name']] = self.addHost(SE['name'], cls=Server, multiple=SE['multiple'])
                else:
                    servers[SE['name']] = self.addHost(SE['name'], cls=Server, multiple=SE['multiple'], url=SE['url'], dns=SE['dns'])

        if config['clients'] != None:
            # Add client hosts with version and profile attributes
            client_SNs = name_generator(model='E2507', quantity = len(config["clients"])) # quantity = Nº of clients you want to add
            i=0
            for client in config['clients']:
                C = {}
                C['SN']=client_SNs[i]
                i += 1
                for element in config['clients'][client]:
                    C[element] = config["clients"][client][element]
                if 'url' not in C.keys():
                    clients[C['name']] = self.addHost(C['name'], cls=Client, version=C['version'], profile=C['SecProfile'], SN= C['SN'])
                else:
                    clients[C['name']] = self.addHost(C['name'], cls=Client, version=C['version'], profile=C['SecProfile'], SN= C['SN'], url=C['url'], dns=C['dns'])
        
        if config['dns'] != None:
            # Add DNS hosts with proper url
            for dnsServer in config['dns']:
                D = {}
                for element in config['dns'][dnsServer]:
                    D[element] = config["dns"][dnsServer][element]
                dns[D['name']] = self.addHost(D['name'], cls=DNS)
                    
             
        # Add links between the hosts and the switch
        node_map = {**switches, **routers, **servers, **clients, **dns, **hosts}

        if config['links'] != None:
            for link in config['links']:
                start, end = link
                startN = node_map.get(start)
                endN = node_map.get(end)
                self.addLink(startN, endN)
        
        super(CustomTopology, self).build(*args, **kwargs)