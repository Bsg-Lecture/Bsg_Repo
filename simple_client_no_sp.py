import asyncio
import websockets
import json
from datetime import datetime, timezone

def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

async def main():
    # sondaki slash YOK
    URI = "ws://127.0.0.1:9000"

    print(f"[CLIENT] Connecting: {URI}")
    try:
        # subprotocols parametresi YOK
        async with websockets.connect(URI) as ws:
            boot = {
                "action": "BootNotification",
                "payload": {"model": "Demo", "vendor": "You", "timestamp": now_iso()}
            }
            await ws.send(json.dumps(boot))
            print("[CLIENT] BootNotification sent")
            print("[CLIENT]", await ws.recv())

            start = {
                "action": "StartTransaction",
                "payload": {"idTag": "TEST-123", "timestamp": now_iso()}
            }
            await ws.send(json.dumps(start))
            print("[CLIENT] StartTransaction sent")
            print("[CLIENT]", await ws.recv())

            print("[CLIENT] Simulating 5 seconds...")
            await asyncio.sleep(5)

            stop = {
                "action": "StopTransaction",
                "payload": {"meterStop": 999, "timestamp": now_iso(), "reason": "Anomaly"}
            }
            await ws.send(json.dumps(stop))
            print("[CLIENT] StopTransaction sent")
            print("[CLIENT]", await ws.recv())

            print("[CLIENT] ✅ Done")
    except Exception as e:
        print("[CLIENT ERROR]:", e)

if __name__ == "__main__":
    asyncio.run(main())

