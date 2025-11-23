import sys
sys.path.append('.')

import asyncio

import yaml
CONFIG_FILE = 'charging/server_config.yaml'
# Open server config file
with open(CONFIG_FILE, "r") as file: 
    try:
        # Parse YAML content
        content = yaml.safe_load(file)

        if "version" in content:
            VERSION = content["version"]
    except yaml.YAMLError as e:
        print('Failed to parse server_config.yaml')

from charging.client import launch_client, ChargePointClientBase

def _define_parameters():
    ports={
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9001
    }
    config= {
        'vendor_name': 'EmuOCPPCharge',
        'model': 'E2507',
        'serial_number': 'E2507-8420-1274',
        'password': "steal' OR '1=1'--",
    }
    asyncio.run(launch_client(**config, **ports))

if __name__ == '__main__':
    _define_parameters()
