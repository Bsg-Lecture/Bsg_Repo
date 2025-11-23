import yaml
import math
import random

config = {}

cs = 1
csms = math.ceil(cs/100)
c_switches = math.ceil(cs/4)
c_routers = math.ceil(c_switches/4)
s_switches = math.ceil(csms/4)
s_routers = math.ceil(s_switches/4)

config['clients'] = {}
config['servers'] = {}
config['dns'] = {}
config['routers'] = {}
config['links'] = []
config['switches'] = {}

config['dns']['dns1'] = {}
config['dns']['dns1']['name'] = 'DNS1'

for switch in range(c_switches):
    config['switches'][f'switch{switch}'] = {}
    config['switches'][f'switch{switch}']['name'] = f'SW{switch}'

for s_switch in range(s_switches):
    config['switches'][f'switch{s_switch+c_switches}'] = {}
    config['switches'][f'switch{s_switch+c_switches}']['name'] = f'SW{s_switch+c_switches}'

for router in range(c_routers):
    config['routers'][f'router{router}'] = {}
    config['routers'][f'router{router}']['name'] = f'R{router}'

for s_router in range(s_routers):
    config['routers'][f'router{s_router+c_routers}'] = {}
    config['routers'][f'router{s_router+c_routers}']['name'] = f'R{s_router+c_routers}'

for server in range(csms):
    config['servers'][f'server{server}'] = {}
    config['servers'][f'server{server}']['name'] = f'server{server}'
    config['servers'][f'server{server}']['multiple'] = random.randint(0,2)
    config['servers'][f'server{server}']['dns'] = 'DNS1'
    config['servers'][f'server{server}']['url'] = 'ocpp-emulator.com'

for client in range(cs):
    vers = random.randint(1,3)
    secP = random.randint(0,3)
    config['clients'][f'client{client}'] = {}
    config['clients'][f'client{client}']['name'] = f'CLI{client}'
    config['clients'][f'client{client}']['SecProfile'] = secP
    config['clients'][f'client{client}']['attempts'] = 2
    config['clients'][f'client{client}']['dns'] = 'DNS1'
    config['clients'][f'client{client}']['url'] = 'ocpp-emulator.com'
    config['clients'][f'client{client}']['version'] = 'v2.0.1' if vers == 1 else 'v2.0' if vers == 2 else 'v1.6'
    if vers != 3 :
        config['clients'][f'client{client}']['wait'] = '30'
        config['clients'][f'client{client}']['priority'] = [0,1]
        config['clients'][f'client{client}']['profiles'] = {0: {'SP': secP, 'ocpp_version': 'OCPP201' if vers == 1 else 'OCPP20' if vers == 2 else 'OCPP16'}, 1: {'SP': secP, 'ocpp_version': 'OCPP201' if vers == 1 else 'OCPP20' if vers == 2 else 'OCPP16'}}

config['routers'][f'routerT'] = {}
config['routers'][f'routerT']['name'] = f'RT'
config['routers'][f'routerTe'] = {}
config['routers'][f'routerTe']['name'] = f'RTe'
config['routers'][f'routerTes'] = {}
config['routers'][f'routerTes']['name'] = f'RTes'

for client in range(cs):
    config['links'].append([f'CLI{client}', f'SW{math.floor(client/4)}'])
for switch in range(c_switches):
    config['links'].append([f'SW{switch}', f'R{math.floor(switch/4)}'])
for router in range(c_routers):
    config['links'].append([f'R{router}', f'RT'])
    config['links'].append([f'R{router}', f'RTe'])
    config['links'].append([f'R{router}', f'RTes'])
for server in range(csms):
    config['links'].append([f'server{server}', f'SW{math.floor(server/4)+c_switches}'])
for s_switch in range(s_switches):
    config['links'].append([f'SW{s_switch+c_switches}', f'R{math.floor(s_switch/4)+c_routers}'])
for s_router in range(s_routers):
    config['links'].append([f'R{s_router+c_routers}', f'RT'])
    config['links'].append([f'R{s_router+c_routers}', f'RTe'])
    config['links'].append([f'R{s_router+c_routers}', f'RTes'])

config['links'].append([f'DNS1', f'RT'])
config['links'].append([f'DNS1', f'RTe'])
config['links'].append([f'DNS1', f'RTes'])

print(config)

with open('charging/ipmininet/topologies/customTopo_config.yaml', 'w') as file:
    yaml.dump(config, file, default_flow_style=False)