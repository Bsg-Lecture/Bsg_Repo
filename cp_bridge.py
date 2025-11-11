import asyncio
import logging
import can
import websockets
from datetime import datetime

# ---------------------------------------------------------------------
# OCPP importlarını farklı sürümlere dayanıklı yap
# ---------------------------------------------------------------------
def _pick(mod, *names):
    for n in names:
        if hasattr(mod, n):
            return getattr(mod, n)
    return None

try:
    from ocpp.v16 import ChargePoint as BaseChargePoint, call, call_result
except Exception:
    from ocpp.charge_point import ChargePoint as BaseChargePoint
    from ocpp.v16 import call, call_result

from ocpp.routing import on

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
log = logging.getLogger("cp-bridge")

# ---------------------------------------------------------------------
# OCPP çağrı/yanıt sınıflarını güvenli biçimde topla
# ---------------------------------------------------------------------
BootNotificationCall = _pick(call, 'BootNotification', 'BootNotificationPayload')
HeartbeatCall        = _pick(call, 'Heartbeat', 'HeartbeatPayload')
StatusNotification   = _pick(call, 'StatusNotification', 'StatusNotificationPayload')
DataTransfer         = _pick(call, 'DataTransfer', 'DataTransferPayload')

RemoteStartResult    = _pick(call_result, 'RemoteStartTransaction', 'RemoteStartTransactionPayload')
RemoteStopResult     = _pick(call_result, 'RemoteStopTransaction', 'RemoteStopTransactionPayload')

# ---------------------------------------------------------------------
# CP BRIDGE SINIFI
# ---------------------------------------------------------------------
class ChargeStationBridge(BaseChargePoint):
    """
    Sanal şarj istasyonu (OCPP 1.6C client) + IDS alert’lerini OCPP’ye taşır.
    - CAN bus: socketcan (vcan0)
    - IDS alert kuyruğu: asyncio.Queue(dict)
    """
    def __init__(self, id, connection, bus, alert_queue: asyncio.Queue):
        super().__init__(id, connection)
        self.bus = bus
        self.alert_queue = alert_queue
        if not hasattr(self, "_call_result"):  # bazı sürümlerde yok
            self._call_result = lambda *a, **k: None

    # -------------------------
    # CSMS -> CP yönü
    # -------------------------
    @on('RemoteStartTransaction')
    async def on_remote_start(self, id_tag=None, connector_id=None, **kwargs):
        log.info(f"[CP-Bridge][OCPP ->] RemoteStartTransaction: connector={connector_id}, id_tag={id_tag}")
        try:
            msg = can.Message(arbitration_id=0x200,
                              data=[1, int(connector_id or 0), 0,0,0,0,0,0],
                              is_extended_id=False)
            self.bus.send(msg)
            log.info("[CP-Bridge][-> CAN] 0x200 (Start Charging) gönderildi")
            if RemoteStartResult:
                try:
                    return RemoteStartResult(status="Accepted")
                except Exception:
                    return {"status": "Accepted"}
            return {"status": "Accepted"}
        except Exception as e:
            log.error(f"[CP-Bridge] CAN gönderim hatası: {e}")
            if RemoteStartResult:
                try:
                    return RemoteStartResult(status="Rejected")
                except Exception:
                    return {"status": "Rejected"}
            return {"status": "Rejected"}

    @on('RemoteStopTransaction')
    async def on_remote_stop(self, transaction_id=None, **kwargs):
        log.info(f"[CP-Bridge][OCPP ->] RemoteStopTransaction: tx_id={transaction_id}")
        try:
            msg = can.Message(arbitration_id=0x201,
                              data=[0, int(transaction_id or 0) & 0xFF, 0,0,0,0,0,0],
                              is_extended_id=False)
            self.bus.send(msg)
            log.info("[CP-Bridge][-> CAN] 0x201 (Stop Charging) gönderildi")
            if RemoteStopResult:
                try:
                    return RemoteStopResult(status="Accepted")
                except Exception:
                    return {"status": "Accepted"}
            return {"status": "Accepted"}
        except Exception as e:
            log.error(f"[CP-Bridge] CAN gönderim hatası: {e}")
            if RemoteStopResult:
                try:
                    return RemoteStopResult(status="Rejected")
                except Exception:
                    return {"status": "Rejected"}
            return {"status": "Rejected"}

    # -------------------------
    # CP -> CSMS yönü (IDS alert’leri, fault durumu)
    # -------------------------
    async def send_status_faulted(self, connector_id: int, error_code: str, info: str = ""):
        payload = {
            "connector_id": int(connector_id),
            "error_code": error_code,
            "status": "Faulted",
            "timestamp": datetime.utcnow().isoformat(),
            "info": info[:50] if info else "",
            "vendor_id": "FarukSim",
            "vendor_error_code": "IDS"
        }
        try:
            req = StatusNotification(**payload) if StatusNotification else payload
            await self.call(req)
            log.info(f"[CP-Bridge -> OCPP] StatusNotification(Faulted) gönderildi: {error_code} | {info}")
        except Exception as e:
            log.warning(f"[CP-Bridge] StatusNotification gönderilemedi: {e}")

    async def send_datatransfer_alert(self, vendor: str, message_id: str, data: str):
        payload = {"vendor_id": vendor, "message_id": message_id, "data": data}
        try:
            req = DataTransfer(**payload) if DataTransfer else payload
            resp = await self.call(req)
            log.info(f"[CP-Bridge -> OCPP] DataTransfer IDS alert gönderildi. Yanıt: {resp}")
        except Exception as e:
            log.warning(f"[CP-Bridge] DataTransfer gönderilemedi: {e}")

    async def pump_ids_alerts(self):
        """
        IDS kuyruğundan gelen uyarıları OCPP’ye taşır.
        Alert formatı (ids.py):
        {
          'type': 'overcurrent'|'slope'|...,
          'connector_id': int,
          'severity': 'warning'|'high',
          'details': '...'
        }
        """
        while True:
            alert = await self.alert_queue.get()
            try:
                typ = alert.get("type", "unknown")
                cid = int(alert.get("connector_id", 1))
                sev = alert.get("severity", "warning")
                det = alert.get("details", "")

                err_code = "HighTemperature" if typ == "overcurrent" else "OtherError"
                await self.send_status_faulted(connector_id=cid, error_code=err_code, info=f"{typ}:{sev}")
                await self.send_datatransfer_alert(vendor="FarukSim", message_id=f"IDS.{typ.upper()}", data=det)
            finally:
                self.alert_queue.task_done()

# ---------------------------------------------------------------------
# ANA ASENKRON FONKSİYON
# ---------------------------------------------------------------------
async def main():
    uri = "ws://localhost:9000/CP_1"
    can_interface = "vcan0"

    # CAN başlat
    bus = can.interface.Bus(channel=can_interface, interface="socketcan")
    log.info(f"[CP-Bridge] Sanal CAN arayüzü ({can_interface}) başarıyla bağlandı.")

    alert_q = asyncio.Queue()  # IDS uyarı kuyruğu

    # WebSocket bağlantısı
    async with websockets.connect(uri, subprotocols=["ocpp1.6"]) as ws:
        cp = ChargeStationBridge("CP_1", ws, bus, alert_q)
        cp._ocpp_version = "1.6"
        log.info(f"[CP-Bridge] CSMS'e bağlanıldı: {uri}")

        ocpp_task = asyncio.create_task(cp.start())
        alert_task = asyncio.create_task(cp.pump_ids_alerts())

        # BootNotification (snake_case parametrelerle)
        try:
            if BootNotificationCall:
                req = BootNotificationCall(
                    charge_point_model="CP-Bridge",
                    charge_point_vendor="FarukSim"
                )
            else:
                req = {"charge_point_model": "CP-Bridge", "charge_point_vendor": "FarukSim"}
            log.info(f"[CP-Bridge ->] BootNotification gönderildi: {req}")
            resp = await cp.call(req)
            log.info(f"[CP-Bridge <-] BootNotification yanıtı: {resp}")
        except Exception as e:
            log.error(f"[CP-Bridge] BootNotification gönderilemedi: {e}")

        # Heartbeat döngüsü
        async def heartbeats():
            while True:
                await asyncio.sleep(10)
                try:
                    req = HeartbeatCall() if HeartbeatCall else {}
                    log.info("[CP-Bridge ->] Heartbeat gönderildi")
                    resp = await cp.call(req)
                    log.info(f"[CP-Bridge <-] Heartbeat yanıtı: {resp}")
                except Exception as e:
                    log.warning(f"[CP-Bridge] Heartbeat hatası: {e}")
        hb_task = asyncio.create_task(heartbeats())

        # Gateway + IDS başlat
        from gateway import run_gateway
        from ids import run_ids

        gw_out_q = asyncio.Queue()  # gateway -> ids
        ids_out_q = alert_q         # ids -> cp_bridge

        gw_task  = asyncio.create_task(run_gateway(bus, gw_out_q))
        ids_task = asyncio.create_task(run_ids(gw_out_q, ids_out_q))

        await asyncio.gather(ocpp_task, alert_task, hb_task, gw_task, ids_task)

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
if __name__ == "__main__":
    asyncio.run(main())
