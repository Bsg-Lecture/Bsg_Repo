import ast
import os
import sys
import time
import yaml
import asyncio
import logging
from datetime import datetime, timezone
from typing import List, Optional, Callable, Awaitable, Dict, Any
import base64

import aioconsole
import websockets
from ocpp.routing import on, after
from ocpp.v201 import ChargePoint as Cp201, call as call201, call_result as call_result201
from ocpp.v20 import ChargePoint as Cp20, call as call20, call_result as call_result20
from ocpp.v16 import ChargePoint as Cp16, call as call16, call_result as call_result16
from ocpp.v201 import enums as enums201, datatypes as data201
from ocpp.v16 import enums as enums16, datatypes as data16

from websockets import Headers, Subprotocol

import ssl
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID
from dns.resolver import resolve, NoAnswer
from dns import rdatatype
import argparse

logging.basicConfig(level=logging.ERROR)

# --- GLOBALS ---
CONNECTION_PROFILES = []
COMM_CTRL = None
SECURITY_CTRL = None
CONFIG_FILE = "charging/client_config.yaml"
VERSION = "v2.0.1"
RECONNECT_TIMES = 2
IP = "127.0.0.1"
PORT0 = 9101
SERIAL_NUMBER = "CP-01"
VENDOR_NAME = "EmuOCPPCharge"
MODEL = "E2507"

# --- FUNCTIONS ---
def _get_current_time() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def load_config():
    global COMM_CTRL, CONNECTION_PROFILES, SECURITY_CTRL, VERSION
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as file:
            content = yaml.safe_load(file)
    except Exception:
        content = {}

    # --- SAFE FALLBACK CONFIG ---
    if not content:
        content = {}

    if "comm" in content and content["comm"] is not None:
        COMM_CTRL = {
            enums201.OCPPCommCtrlrVariableName.network_profile_connection_attempts.value: content["comm"].get("NetworkProfileConnectionAttempts", 2),
            enums201.OCPPCommCtrlrVariableName.network_configuration_priority.value: content["comm"].get("NetworkConfigurationPriority", [0]),
            enums201.OCPPCommCtrlrVariableName.message_timeout.value: content["comm"].get("MessageTimeout", 30),
            enums201.OCPPCommCtrlrVariableName.heartbeat_interval.value: content["comm"].get("HeartbeatInterval", 10),
        }
    else:
        COMM_CTRL = {
            enums201.OCPPCommCtrlrVariableName.network_profile_connection_attempts.value: 2,
            enums201.OCPPCommCtrlrVariableName.network_configuration_priority.value: [0],
            enums201.OCPPCommCtrlrVariableName.message_timeout.value: 30,
            enums201.OCPPCommCtrlrVariableName.heartbeat_interval.value: 10,
        }

    if "profiles" in content and content["profiles"]:
        CONNECTION_PROFILES = []
        for element in content["profiles"]:
            CONNECTION_PROFILES.append(
                data201.NetworkConnectionProfileType(
                    ocpp_version="OCPP201",
                    ocpp_transport=enums201.OCPPTransportType.json,
                    ocpp_csms_url="ws://127.0.0.1:9000/",
                    message_timeout=30,
                    security_profile=0,
                    ocpp_interface=enums201.OCPPInterfaceType.wireless0,
                )
            )
    else:
        CONNECTION_PROFILES = [
            data201.NetworkConnectionProfileType(
                ocpp_version="OCPP201",
                ocpp_transport=enums201.OCPPTransportType.json,
                ocpp_csms_url="ws://127.0.0.1:9000/",
                message_timeout=30,
                security_profile=0,
                ocpp_interface=enums201.OCPPInterfaceType.wireless0,
            )
        ]
    return True

# --- CLIENT LOGIC ---
async def launch_client(vendor_name="Vendor", model="Model", index=None):
    global VERSION
    VERSION = "v2.0.1"
    secProf = 0
    addr = "ws://127.0.0.1:9100/"
    headers = None

    async with websockets.connect(addr, subprotocols=[Subprotocol("ocpp2.0.1")], extra_headers=headers) as ws:
        class ChargePointClient(Cp201):
            async def send_boot(self):
                req = call201.BootNotificationPayload(
                    charging_station={"model": model, "vendor_name": vendor_name},
                    reason="PowerUp"
                )
                res = await self.call(req)
                print("BootNotification sent, status:", res.status)
        cp = ChargePointClient("CP-01", ws)
        await asyncio.gather(cp.start(), cp.send_boot())

def main():
    if not load_config():
        print("Config yüklenemedi.")
        sys.exit(1)

    tries = COMM_CTRL[enums201.OCPPCommCtrlrVariableName.network_profile_connection_attempts.value]
    for profile in COMM_CTRL[enums201.OCPPCommCtrlrVariableName.network_configuration_priority.value]:
        while True:
            try:
                asyncio.run(launch_client(vendor_name=VENDOR_NAME, model=MODEL))
            except Exception as e:
                print(f"An unexpected error occurred with security profile {CONNECTION_PROFILES[profile].security_profile}: {e}")
                if tries > 0:
                    tries -= 1
                    print("Reconnecting in 5 seconds...")
                    time.sleep(5)
                    continue
                else:
                    break
            break

if __name__ == "__main__":
    main()
