#!/usr/bin/env python3
"""
Minimal OCPP Central System stub using websockets + ocpp (educational).
Requires: pip install ocpp websockets asyncio
"""
import asyncio
from websockets.server import serve
from ocpp.v16 import ChargePoint as cp
from datetime import datetime, timezone

CONNECTED = set()

class CentralProtocol(cp):
    async def send_price_signal(self, price, seq=0):
        payload = {"price": price, "seq": seq, "ts": datetime.now(timezone.utc).isoformat()}
        await self.call('PriceSignal', payload)

async def handler(websocket, path):
    cp_id = path.strip('/')
    cp_obj = CentralProtocol(cp_id, websocket)
    try:
        await cp_obj.start()
    except Exception as e:
        print("Connection error:", e)

async def periodic_price_broadcast(price=0.01, duration=60, interval=5):
    seq = 0
    end = asyncio.get_event_loop().time() + duration
    while asyncio.get_event_loop().time() < end:
        print(f"[CENTRAL] broadcasting price={price} seq={seq}")
        # iterate over connected (this is illustrative; real code needs proper tracking)
        for cp_obj in list(CONNECTED):
            try:
                await cp_obj.send_price_signal(price, seq)
            except Exception as e:
                print("send error", e)
        seq += 1
        await asyncio.sleep(interval)

async def main(host='0.0.0.0', port=9000):
    async with serve(handler, host, port):
        print(f"[CENTRAL] listening ws://{host}:{port}/<charge_point_id>")
        await periodic_price_broadcast()

if __name__ == "__main__":
    asyncio.run(main())
