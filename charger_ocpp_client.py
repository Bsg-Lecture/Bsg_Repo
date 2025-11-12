#!/usr/bin/env python3
"""
Minimal Charge Point client using ocpp.
Requires: pip install ocpp websockets asyncio
"""
import asyncio, socket, json, time
from websockets import connect
from ocpp.v16 import ChargePoint as cp

IDS_HOST = '127.0.0.1'
IDS_PORT = 5010

class ChargePointClient(cp):
    async def handle_price_signal(self, payload):
        price = payload.get('price', 9999)
        if price < 0.05:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            start = {'type':'StartTransaction','charger_id':self.id,'ts':time.time()}
            s.sendto(json.dumps(start).encode(), (IDS_HOST, IDS_PORT))
            s.close()
            print(f"[{self.id}] Notified IDS of StartTransaction")

async def run(cp_id, central_url):
    async with connect(central_url) as ws:
        client = ChargePointClient(cp_id, ws)
        await client.start()

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--id", default="CP1")
    ap.add_argument("--central", default="ws://localhost:9000/CP1")
    args = ap.parse_args()
    asyncio.run(run(args.id, args.central))
