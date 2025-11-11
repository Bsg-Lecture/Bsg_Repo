import asyncio
import logging
from datetime import datetime, UTC
import websockets

from ocpp.v201 import ChargePoint as cp
from ocpp.v201.call import MeterValues
from ocpp.v201.datatypes import MeterValueType, SampledValueType

logging.basicConfig(level=logging.INFO)


class V2GChargePoint(cp):
    async def send_v2g_meter_values(self):
        guncel_zaman = datetime.now(UTC).isoformat()

        sampled_value = SampledValueType(
            value=-10000,  # FİZİKSEL GERÇEKLİK
            context="Sample.Periodic",
            measurand="Energy.Active.Export.Register"
        )

        meter_value = MeterValueType(
            timestamp=guncel_zaman,
            sampled_value=[sampled_value]
        )

        request = MeterValues(
            evse_id=1,
            meter_value=[meter_value]
        )

        print("\n" + "=" * 30)
        print(f"CP (FİZİKSEL GERÇEKLİK): -10000 Wh V2G satışı gönderiliyor...")
        print("=" * 30 + "\n")

        response = await self.call(request)
        print(f"CP: MeterValues onayı alındı: {response}")


async def main():
    async with websockets.connect(
            'ws://127.0.0.1:8080/CP_001',
            subprotocols=['ocpp2.0.1']
    ) as ws:
        charge_point = V2GChargePoint('CP_001', ws)

        boot_task = asyncio.create_task(charge_point.start())

        await asyncio.sleep(10)  # Başarılı bir BootNotification için zaman tanı

        await charge_point.send_v2g_meter_values()

        await charge_point.stop()
        await boot_task


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except Exception as e:
        # Bağlantı kapanma hatalarını daha net göster
        if "1011" in str(e):
            print(
                "\n!!! CP HATASI: Sunucu (mitmproxy veya CSMS) '1011 (Internal Error)' ile bağlantıyı kapattı. Terminal 1 ve 2'yi kontrol edin.")
        else:
            print(f"CP İstemcisi hata verdi: {e}")