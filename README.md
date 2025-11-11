# V2G Fiyat Arbitrajı Manipülasyonu - Anomali Test Ortamı

## Proje Açıklaması

Bu proje, **V2G (Vehicle-to-Grid) Fiyat Arbitrajı Manipülasyonu** anomali senaryosunu test etmek için bir laboratuvar ortamı sağlar. Senaryo, Man-in-the-Middle (MitM) saldırısı ile OCPP 2.0.1 protokolü üzerinden gönderilen MeterValues mesajlarının manipüle edilmesini simüle eder.

## Senaryo Özeti

**Normal İşleyiş:**
- V2G uyumlu bir araç, şebekeye 10 kWh enerji satar (deşarj)
- Charge Point (CP), CSMS'e negatif değer (-10000 Wh) gönderir
- CSMS, kullanıcının enerji sattığını kaydeder ve ödeme yapar

**Anomali (Saldırı):**
- Saldırgan, CP ve CSMS arasındaki iletişimi dinler (MitM)
- MeterValues mesajını yakalar ve negatif değeri pozitife çevirir
- CSMS, kullanıcının enerji satın aldığını kaydeder (anomali)
- Sonuç: Saldırgan hem enerji satışı geliri elde eder hem de enerji alım borcu yaratır

## Dosya Yapısı

- `cp_client.py`: Charge Point (CP) simülatörü - V2G satışını simüle eder
- `csms_server.py`: CSMS (Central System Management System) sunucusu - MeterValues mesajlarını alır ve kaydeder
- `attack_script.py`: MitM saldırı scripti - OCPP mesajlarını yakalar ve manipüle eder
- `main.py`: Ana dosya (şu an boş)

## Kurulum

1. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

2. **Paketler:**
- `ocpp>=0.20.0`: OCPP 2.0.1 protokol desteği
- `websockets>=12.0`: WebSocket bağlantıları için
- `mitmproxy>=10.0.0`: Man-in-the-Middle saldırı simülasyonu için

## Kullanım

### 1. CSMS Sunucusunu Başlatın

```bash
python csms_server.py
```

Sunucu, `9000` portunda çalışacaktır.

### 2. (Opsiyonel) MitM Saldırısını Başlatın

Başka bir terminalde:
```bash
mitmdump -s attack_script.py --listen-port 8080
```

### 3. Charge Point İstemcisini Çalıştırın

Başka bir terminalde:
```bash
python cp_client.py
```

**Not:** MitM saldırısı kullanıyorsanız, `cp_client.py` dosyasındaki bağlantı adresini proxy'ye yönlendirmeniz gerekebilir.

## Test Senaryoları

### Senaryo 1: Normal İşleyiş (MitM Olmadan)
1. CSMS sunucusunu başlatın
2. CP istemcisini çalıştırın
3. CSMS, negatif değeri (-10000 Wh) alır ve V2G satışı olarak kaydeder

### Senaryo 2: Anomali (MitM ile)
1. CSMS sunucusunu başlatın
2. MitM proxy'yi başlatın
3. CP istemcisini proxy üzerinden çalıştırın
4. CSMS, pozitif değer (+10000 Wh) alır ve enerji alımı olarak kaydeder (ANOMALİ)

## Beklenen Çıktılar

### Normal İşleyiş:
```
CSMS: CP_001 istasyonundan MeterValues alındı.
Gelen Değer: -10000.0 Wh
✓ Normal: -10000.0 Wh V2G satışı kaydedildi.
```

### Anomali:
```
CSMS: CP_001 istasyonundan MeterValues alındı.
Gelen Değer: 10000.0 Wh
⚠️  ANOMALİ TESPİT EDİLDİ!
   Beklenen: Negatif değer (V2G satışı)
   Gelen: Pozitif değer (Enerji alımı)
   CSMS KAYDI (ANOMALİ): Sisteme 10000.0 Wh enerji GİRİŞİ kaydedildi.
```

## Teknik Detaylar

- **Protokol:** OCPP 2.0.1 (OCPP-J)
- **Mesaj Formatı:** JSON array: `[MessageTypeId, MessageId, Action, Payload]`
- **Mesaj Tipi:** MeterValues (CALL)
- **Port:** 9000 (CSMS), 8080 (MitM proxy)

## STRIDE Kategorisi

- **Kategori:** Tampering (Manipülasyon)
- **Hedef Protokoller:** OCPP 2.0.1 (UC J02 "MeterValues") ve ISO 15118 (V2G İletişimi)

## İlişkili Proje Hedefleri

- **Hedef 3:** Enerji Hırsızlığı ve Sahte Veri Enjeksiyonu Algoritması Geliştirilmesi
- **Hedef 5:** Standartlara Uygunluk (ISO 15118 V2G standardı)

## Notlar

- Bu proje, araştırma ve eğitim amaçlıdır
- Gerçek sistemlerde kullanmadan önce güvenlik önlemleri alınmalıdır
- OCPP kütüphanesi, mesajları otomatik olarak serialize/deserialize eder

## Sorun Giderme

### Port Zaten Kullanımda
```bash
# Windows'ta portu kontrol edin
netstat -ano | findstr :9000
```

### Paket Hataları
```bash
# Paketleri yeniden yükleyin
pip install --upgrade -r requirements.txt
```

### WebSocket Bağlantı Hataları
- CSMS sunucusunun çalıştığından emin olun
- Port numaralarının doğru olduğunu kontrol edin
- Firewall ayarlarını kontrol edin

## Lisans

Bu proje, araştırma ve eğitim amaçlıdır.

