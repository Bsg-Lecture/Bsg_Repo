import random
from ipmininet.host import IPHost

# Define a Server host class
class Server(IPHost):
    def __init__(self, name, multiple = 2, url = None, dns = None, **params):
        super(Server, self).__init__(name, **params)
        self.type = 'server'
        self.multiple = multiple
        self.url = url
        self.dns = dns

# Define a DNS host class
class DNS(IPHost):
    def __init__(self, name, **params):
        super(DNS, self).__init__(name, **params)
        self.type = 'dns'

# Define a Client host class
class Client(IPHost):
    def __init__(self, name, version, profile, SN, url = None, dns = None, **params):
        super(Client, self).__init__(name, **params)
        self.type = 'client'
        self.SN = SN # Serial number of the charge point
        self.version = version # 'v1.6' | 'v2.0' | 'v2.0.1'
        self.profile = profile # Profile of the client.
        self.url = url
        self.dns = dns

def name_generator(model: str = 'E2507', quantity: int = 1):
    names = []
    for i in range (quantity):
        name = model + '-' + format(random.randint(0,9999),'04d') + '-' +  format(random.randint(0,9999),'04d')
        if name in names:
            while name in names:
                name = model + '-' + format(random.randint(0,9999),'04d') + '-' +  format(random.randint(0,9999),'04d')
        names.append(name)
    return names
