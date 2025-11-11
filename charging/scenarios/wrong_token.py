import sys
sys.path.append('.')

import asyncio
import logging

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

async def wrong_token(cp: ChargePointClientBase):
    # Send authorization request
    response = await cp.send_authorize({'type': 'ISO14443', 'id_token': 'abcd'}) # Wrong token

    # Check if authorization was accepted
    if response.id_token_info['status'] != "Accepted":
        logging.error("Authorization failed")
        return
    else:
        cp.print_message("Charging point authorization successful!")


if __name__ == "__main__":

    config = {
        'vendor_name': 'EmuOCPPCharge',
        'model': 'E2507',
        'serial_number': 'E2507-8420-1274',
        'password': 'HPEufO4u3IMl1G',
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }

    asyncio.run(launch_client(**config, async_runnable=wrong_token))
