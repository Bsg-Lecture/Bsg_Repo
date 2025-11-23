from ipmininet.iptopo import IPTopo
from ipmininet.ipnet import IPNet
from topologies.customHosts import Server, Client, name_generator

class CustomTopology(IPTopo):
    def build(self, *args, **kwargs):
        # Add a switch
        s1 = self.addSwitch('s1')
        s2 = self.addSwitch('s2')
        
        # Add server hosts
        server1 = self.addHost('server1', cls=Server, multiple=2)
        server2 = self.addHost('server2', cls=Server, multiple=2)
        
        # Add client hosts with version and profile attributes
        client_SNs = name_generator(model='E2507', quantity = 5) # quantity = Nº of clients you want to add
        client1 = self.addHost('CLI1', cls=Client, version='v2.0.1', profile=[3,2], SN= client_SNs[0])
        client2 = self.addHost('CLI2', cls=Client, version='v2.0', profile=[2,1], SN= client_SNs[1])
        client3 = self.addHost('CLI3', cls=Client, version='v1.6', profile=[3], SN= client_SNs[2])
        client4 = self.addHost('CLI4', cls=Client, version='v2.0', profile=[3,2,1], SN= client_SNs[3])
        client5 = self.addHost('CLI5', cls=Client, version='v2.0.1', profile=[1,0], SN= client_SNs[4])
        
        # Add links between the hosts and the switch
        self.addLink(server1, s1)
        self.addLink(server2, s2)
        self.addLink(client1, s1)
        self.addLink(client2, s1)
        self.addLink(client5, s1)
        self.addLink(client3, s2)
        self.addLink(client4, s2)


        
        super(CustomTopology, self).build(*args, **kwargs)