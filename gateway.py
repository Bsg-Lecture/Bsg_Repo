# gateway.py
import asyncio
import logging
import can

log = logging.getLogger("gateway")

# Basit bir parser: örnek olarak 0x180 -> akım (A) veri[0]’da
def parse_frame(frame: can.Message):
    try:
        if frame.arbitration_id == 0x180 and len(frame.data) >= 2:
            current = int(frame.data[0])   # örnek: 0..255 A
            connector_id = int(frame.data[1]) if len(frame.data) > 1 else 1
            return {"type": "telemetry", "metric": "current", "value": current, "connector_id": connector_id}
        # başka ID’ler/metrikler eklenebilir
    except Exception as e:
        log.warning(f"[GW] frame parse error: {e}")
    return None

async def run_gateway(bus: can.BusABC, out_queue: asyncio.Queue):
    """
    CAN’dan mesajları okuyup parse ederek out_queue’ye atar.
    """
    log.info("[GW] Gateway başlatıldı (CAN dinliyor)...")
    reader = can.AsyncBufferedReader()
    loop = asyncio.get_event_loop()
    notifier = can.Notifier(bus, [reader], loop=loop)

    try:
        while True:
            frame = await reader.get_message()  # bloklar
            parsed = parse_frame(frame)
            if parsed:
                await out_queue.put(parsed)
                log.info(f"[GW] -> IDS kuyruğu: {parsed}")
    finally:
        notifier.stop()
        log.info("[GW] Gateway durduruldu")
