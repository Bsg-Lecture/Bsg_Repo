# server.py
import asyncio
import logging
from datetime import datetime
import websockets

# --- Güvenli import (sürüm farkı için) ---
try:
    from ocpp.v16 import ChargePoint as BaseChargePoint, call, call_result
except Exception:
    from ocpp.charge_point import ChargePoint as BaseChargePoint
    from ocpp.v16 import call, call_result

from ocpp.routing import on
from ocpp.v16.enums import RegistrationStatus

# --- Log ayarları ---
logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
log = logging.getLogger("csms")

connected_cps = {}

# ============================================================
#  CHARGE POINT SINIFI
# ============================================================
class ChargePoint(BaseChargePoint):
    def __init__(self, id, connection):
        super().__init__(id, connection)
        if not hasattr(self, "_call_result"):
            self._call_result = lambda *a, **k: None

    # ---- BootNotification ----
    @on('BootNotification')
    async def on_boot_notification(self, charge_point_model, charge_point_vendor, **kwargs):
        log.info(f"[BootNotification] {self.id}: model={charge_point_model}, vendor={charge_point_vendor}")
        return call_result.BootNotificationPayload(
            current_time=datetime.utcnow().isoformat(),
            interval=10,
            status="Accepted"
        )

    # ---- Heartbeat ----
    @on('Heartbeat')
    async def on_heartbeat(self):
        log.info(f"[Heartbeat] {self.id}")
        return call_result.HeartbeatPayload(current_time=datetime.utcnow().isoformat())

    # ---- StatusNotification (IDS Faults) ----
    @on('StatusNotification')
    async def on_status_notification(self, connector_id, error_code, status, **kwargs):
        info = kwargs.get("info") or ""
        vendor = kwargs.get("vendorId") or kwargs.get("vendor_id") or ""
        verr = kwargs.get("vendorErrorCode") or kwargs.get("vendor_error_code") or ""
        log.warning(f"[StatusNotification] {self.id} | conn={connector_id} | status={status} | "
                    f"error={error_code} | info='{info}' | vendor={vendor}/{verr}")
        try:
            return call_result.StatusNotificationPayload()
        except Exception:
            return {}

    # ---- DataTransfer (IDS detayları) ----
    @on('DataTransfer')
    async def on_data_transfer(self, vendor_id, **kwargs):
        msg_id = kwargs.get("messageId") or kwargs.get("message_id")
        data = kwargs.get("data")
        log.warning(f"[DataTransfer] {self.id} | vendor={vendor_id} | msg={msg_id} | data={data}")
        try:
            return call_result.DataTransferPayload(status="Accepted", data="ok")
        except Exception:
            return {"status": "Accepted", "data": "ok"}


# ============================================================
#  BAĞLANTI VE KOMUT YÖNETİMİ
# ============================================================
async def on_connect(websocket, path):
    cp_id = path.strip('/')
    log.info(f"🔌 Yeni bağlantı: {cp_id}")

    cp = ChargePoint(cp_id, websocket)
    try:
        cp._ocpp_version = '1.6'
    except Exception:
        pass

    connected_cps[cp_id] = cp
    log.info(f"📋 Bağlı CP'ler: {list(connected_cps.keys())}")

    try:
        await cp.start()
    except websockets.exceptions.ConnectionClosed:
        log.warning(f"⚠️ {cp_id} bağlantısı kapandı.")
    finally:
        connected_cps.pop(cp_id, None)
        log.info(f"📋 Güncel CP listesi: {list(connected_cps.keys())}")


# ============================================================
#  KOMUT GİRİŞ DÖNGÜSÜ
# ============================================================
async def command_input_handler():
    while True:
        try:
            loop = asyncio.get_event_loop()
            cmd_line = await loop.run_in_executor(None, input,
                "\n[SERVER KOMUT] 'start <CP_ID> <Connector_ID>' veya 'stop <CP_ID> <TX_ID>' girin:\n> ")
            parts = cmd_line.strip().split()
            if len(parts) != 3:
                log.error("[HATA] Geçersiz format. Örnek: start CP_1 1")
                continue

            cmd, cp_id, value = parts
            if cp_id not in connected_cps:
                log.error(f"[HATA] {cp_id} bağlı değil. Aktifler: {list(connected_cps.keys())}")
                continue

            cp = connected_cps[cp_id]
            if cmd.lower() == "start":
                log.info(f"[SERVER] {cp_id}'e RemoteStartTransaction gönderiliyor...")
                req = call.RemoteStartTransactionPayload(connector_id=int(value), id_tag="TAG123")
                resp = await cp.call(req)
                log.info(f"[YANIT] {cp_id}: {resp}")

            elif cmd.lower() == "stop":
                log.info(f"[SERVER] {cp_id}'e RemoteStopTransaction gönderiliyor...")
                req = call.RemoteStopTransactionPayload(transaction_id=int(value))
                resp = await cp.call(req)
                log.info(f"[YANIT] {cp_id}: {resp}")

            else:
                log.error(f"[HATA] Bilinmeyen komut: {cmd}")

        except Exception as e:
            log.error(f"[HATA] Komut işlenemedi: {e}")


# ============================================================
#  ANA FONKSİYON
# ============================================================
async def main():
    log.info("🚀 OCPP 1.6 Central System başlatılıyor (port: 9000)...")
    server = await websockets.serve(on_connect, "0.0.0.0", 9000, subprotocols=["ocpp1.6"])
    log.info("✅ Server listening on 0.0.0.0:9000")
    await asyncio.gather(command_input_handler(), server.wait_closed())


if __name__ == "__main__":
    asyncio.run(main())
