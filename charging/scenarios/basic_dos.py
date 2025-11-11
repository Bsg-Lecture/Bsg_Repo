import sys
sys.path.append('.')

import asyncio
import random
import time

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

N_INSTANCES = 10_000

def _get_random_config() -> dict[str, str]:
    return {
        'vendor_name': 'EmuOCPPCharge',
        'model': 'E2507',
        'serial_number': f'E2507-{random.randint(0, 9999):04}-{random.randint(0, 9999):04}',
        'password': 'HPEufO4u3IMl1G',
        'server': "[fe80::e3a6:46e4:bff9:fb8e%ens33]",
        'port': 9000
    }


async def _no_action(_: ChargePointClientBase):
    pass


async def main():
    tasks = []

    print(f"Launching {N_INSTANCES} clients...")

    start = time.time()

    for i in range(N_INSTANCES):
        # Launch client
        tasks.append(asyncio.create_task(launch_client(**_get_random_config(), async_runnable=_no_action)))
        # Sleep for some time to distribute clients over 10 seconds
        await asyncio.sleep(10/N_INSTANCES)

    print(f"All clients launched in {time.time() - start} seconds")

    # Await all clients
    for i in range(N_INSTANCES):
        await tasks[i]


if __name__ == "__main__":
    asyncio.run(main())
