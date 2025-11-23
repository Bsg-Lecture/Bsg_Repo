import asyncio
import websockets
import json
from datetime import datetime, timezone

# ISO8601 zaman damgası
def now_iso():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

async def main():
    URI = "ws://127.0.0.1:9000"
    print(f"[CLIENT] Connecting: {URI}")

    try:
        # ÖNEMLİ: OCPP alt protokolünü bildir
        async with websockets.connect(URI, subprotocols=["ocpp2.0.1"]) as ws:
            # 1) Boot
            boot = {
                "action": "BootNotification",
                "payload": {
                    "model": "Demo",
                    "vendor": "You",
                    "timestamp": now_iso()
                }
            }
            await ws.send(json.dumps(boot))
            print("[CLIENT] Boot sent")
            print("[CLIENT]", await ws.recv())

            # 2) StartTransaction (normal akış başlat)
            start_tx = {
                "action": "StartTransaction",
                "payload": {
                    "idTag": "TEST-123",
                    "timestamp": now_iso()
                }
            }
            await ws.send(json.dumps(start_tx))
            print("[CLIENT] StartTransaction sent")
            print("[CLIENT]", await ws.recv())

            # 3) Anomali: Rejeneratif tork sapması
            # - expected_torque: beklenen rejeneratif tork (Nm)
            # - observed_torque: ölçülen tork (Nm)  → bariz düşük = sapma
            # - delta: sapma miktarı (Nm) ve yüzdesi
            expected = 120.0
            observed = 75.5
            delta = observed - expected
            delta_pct = (delta / expected) * 100.0

            torque_anomaly = {
                "action": "TorqueData",
                "payload": {
                    "timestamp": now_iso(),
                    "units": "Nm",
                    "expected_torque": expected,
                    "observed_torque": observed,
                    "delta": round(delta, 2),
                    "delta_percent": round(delta_pct, 2),
                    # basit sınıflandırma: eşiğe göre severity
                    "severity": "high" if abs(delta_pct) >= 20 else "medium"
                }
            }

            await ws.send(json.dumps(torque_anomaly))
            print("[CLIENT] Torque Anomaly sent")
            print("[CLIENT]", await ws.recv())

            # 4) (opsiyonel) Kısa bekleme
            print("[CLIENT] Simulating 3 seconds...")
            await asyncio.sleep(3)

            # 5) StopTransaction (akışı kapat)
            stop_tx = {
                "action": "StopTransaction",
                "payload": {
                    "meterStop": 999,
                    "timestamp": now_iso(),
                    "reason": "Anomaly"
                }
            }
            await ws.send(json.dumps(stop_tx))
            print("[CLIENT] StopTransaction sent")
            print("[CLIENT]", await ws.recv())

            print("[CLIENT] ✅ Done")

    except Exception as e:
        print("[CLIENT ERROR]:", e)

if __name__ == "__main__":
    asyncio.run(main())




