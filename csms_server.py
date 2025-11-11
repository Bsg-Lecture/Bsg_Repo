import asyncio
import logging
import websockets
from datetime import datetime, UTC

# -------- KANIT SATIRI --------
print(">>> EMIRHAN UZEN: VIICIN KODUN SON HALI (on_connect DUZELTILDI V2) CALISTI.")
# -----------------------------DEO TESTI

from ocpp.v201 import ChargePoint as cp
from ocpp.routing import on
from ocpp.v201.enums import Action
from ocpp.v201.call_result import BootNotification, MeterValues

logging.basicConfig(level=logging.INFO)


class SimpleCSMS(cp):
    @on(Action.boot_notification)
    async def on_boot_notification(self, charge_point_vendor, charge_point_model, **kwargs):
        print(f"CSMS: {self.id} (BootNotification alındı).")
        return BootNotification(
            current_time=datetime.now(UTC).isoformat(),
            interval=10,
            status="Accepted"
        )

    @on(Action.meter_values)
    async def on_meter_values(self, evse_id, meter_value, **kwargs):
        gelen_deger = meter_value[0].sampled_value[0].value
        gelen_measurand = meter_value[0].sampled_value[0].measurand

        print("\n" + "=" * 30)
        print(f"CSMS: {self.id} istasyonundan MeterValues alındı.")
        print(f"CSMS KAYDI (ANOMALİ): Sisteme {gelen_deger} Wh ({gelen_measurand}) kaydedildi.")
        print("=" * 30 + "\n")

        return MeterValues(status="Accepted")


#
# 2 SAATLİK HATA BURADAYDI. FONKSİYON SADECE 'websocket' ARGÜMANINI ALIR.
#
async def on_connect(websocket):
    """
    Yeni bir şarj istasyonu (CP) bağlandığında, bu fonksiyon tetiklenir.
    'path' (yol) artık 'websocket.path' içinden alınır.
    """
    try:
        # 'path' ARTIK 'websocket.path' OLARAK BURADAN OKUNUYOR
        path = websocket.path

        charge_point_id = path.strip('/')
        charge_point = SimpleCSMS(charge_point_id, websocket)
        print(f"CSMS: {charge_point_id} bağlandı (WebSocket).")
        await charge_point.start()
    except Exception as e:
        if "1000" in str(e) or "1011" in str(e) or "1006" in str(e):
            print(f"CSMS: Bağlantı kapandı.")
        else:
            print(f"!!! CSMS HATA (on_connect): {e}")


async def main():
    server = await websockets.serve(
        on_connect,  # <-- Artık doğru fonksiyon imzasıyla eşleşiyor
        '0.0.0.0',
        9000,
        subprotocols=['ocpp2.0.1']
    )
    print("CSMS WebSocket Sunucusu 9000 portunda çalışıyor...")
    await server.wait_closed()


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("CSMS Sunucusu kapatıldı.")