# ids.py
import asyncio
import logging
from collections import deque
from time import time

log = logging.getLogger("ids")

# Basit eşikler
MAX_CURRENT = 40      # A (örnek)
SLOPE_WINDOW = 5      # son 5 örnek
SLOPE_THRESHOLD = 12  # A / örnek (örnek değer)

class SlopeDetector:
    def __init__(self):
        self.history = {}  # connector_id -> deque[(t, value)]

    def update(self, connector_id: int, value: float):
        dq = self.history.setdefault(connector_id, deque(maxlen=SLOPE_WINDOW))
        dq.append((time(), value))
        if len(dq) >= 2:
            # kaba: son ile ilk arasındaki fark / örnek sayısı
            delta = dq[-1][1] - dq[0][1]
            slope = delta / max(1, (len(dq)-1))
            return slope
        return 0.0

async def run_ids(gw_in_queue: asyncio.Queue, alert_out_queue: asyncio.Queue):
    """
    Gateway’den gelen telemetry’yi dinler, alarm olursa alert_out_queue’ye yazar.
    Alert şeması:
      {'type':'overcurrent'|'slope', 'connector_id':int, 'severity':'warning'|'high', 'details': '...'}
    """
    log.info("[IDS] IDS başlatıldı...")
    slope = SlopeDetector()

    while True:
        msg = await gw_in_queue.get()
        try:
            if msg.get("type") == "telemetry" and msg.get("metric") == "current":
                cid = int(msg.get("connector_id", 1))
                cur = float(msg.get("value", 0))

                # 1) Mutlak eşik
                if cur > MAX_CURRENT:
                    alert = {
                        "type": "overcurrent",
                        "connector_id": cid,
                        "severity": "high" if cur > MAX_CURRENT * 1.25 else "warning",
                        "details": f"current={cur}A > {MAX_CURRENT}A"
                    }
                    await alert_out_queue.put(alert)
                    log.warning(f"[IDS] OVERCURRENT: {alert}")

                # 2) Slope (kademeli artış)
                s = slope.update(cid, cur)
                if s > SLOPE_THRESHOLD:
                    alert = {
                        "type": "slope",
                        "connector_id": cid,
                        "severity": "warning",
                        "details": f"slope≈{s:.1f}A/step > {SLOPE_THRESHOLD}"
                    }
                    await alert_out_queue.put(alert)
                    log.warning(f"[IDS] SLOPE: {alert}")
        finally:
            gw_in_queue.task_done()
