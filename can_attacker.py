# can_attacker.py (Yeni Mimari İçin Güncellendi)
import asyncio
import logging
import can
import time

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] - ATK - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
log = logging.getLogger("Attacker")

try:
    bus = can.interface.Bus('vcan0', interface='socketcan')
    log.info("Saldırgan vcan0 (Kirli Ağ) arayüzüne başarıyla bağlandı.")
except Exception as e: exit(f"Saldırgan vcan0'a bağlanılamadı: {e}")

async def send_can_message(can_id, data):
    try:
        msg = can.Message(arbitration_id=can_id, data=data, is_extended_id=False)
        bus.send(msg)
        log.info(f"CAN Mesajı Gönderildi: ID={hex(can_id)}, Data={data}")
        return True
    except Exception as e: 
        log.error(f"CAN Mesajı gönderilemedi: {e}")
        return False

async def main():
    log.info("Yeni IDS'i (Aşırı Akım ve Hızlı Artış) test etme başlıyor...")
    
    can_id_current = 0x180 # gateway.py'nin dinlediği ID
    
    # --- Test 1: Normal Akım (Sorun yok) ---
    log.info("Test 1: Normal Akım (20A) gönderiliyor...")
    # Veri formatı (gateway.py'den): [current, connector_id]
    await send_can_message(can_id_current, data=[20, 1, 0, 0, 0, 0, 0, 0])
    await asyncio.sleep(2)
    
    # --- Test 2: Aşırı Akım Saldırısı (IDS 'overcurrent' kuralı) ---
    log.warning("Test 2: Aşırı Akım Saldırısı (50A) gönderiliyor...")
    # ids.py'deki MAX_CURRENT (40A) limitini aşacak
    await send_can_message(can_id_current, data=[50, 1, 0, 0, 0, 0, 0, 0])
    await asyncio.sleep(2)
    
    # --- Test 3: Hızlı Artış (Slope) Saldırısı (IDS 'slope' kuralı) ---
    log.warning("Test 3: Hızlı Artış (Slope) Saldırısı başlıyor...")
    # ids.py'deki SLOPE_THRESHOLD (12A/step) limitini aşacak
    await send_can_message(can_id_current, data=[10, 1, 0, 0, 0, 0, 0, 0]) # 10A
    await asyncio.sleep(0.5)
    await send_can_message(can_id_current, data=[25, 1, 0, 0, 0, 0, 0, 0]) # +15A artış (Limit < 12)
    await asyncio.sleep(0.5)
    await send_can_message(can_id_current, data=[40, 1, 0, 0, 0, 0, 0, 0]) # +15A artış (Limit < 12)

    log.info("Saldırı tamamlandı.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("\nSaldırgan durduruldu.")