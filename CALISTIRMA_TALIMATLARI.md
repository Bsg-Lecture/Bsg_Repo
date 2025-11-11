# V2G Anomali Test Ortamı - Çalıştırma Talimatları

## 📋 Gereksinimler

Önce paketlerin yüklü olduğundan emin olun:
```powershell
pip install -r requirements.txt
```

## 🚀 Adım Adım Çalıştırma

### Senaryo 1: Normal İşleyiş (MitM Olmadan)

#### Terminal 1: CSMS Sunucusu
```powershell
# Proje klasörüne gidin
cd "C:\Users\emirh\OneDrive\Masaüstü\Anomali_Test"

# CSMS sunucusunu başlatın
python csms_server.py
```

**Beklenen Çıktı:**
```
CSMS WebSocket Sunucusu 9000 portunda çalışıyor...
```

#### Terminal 2: Charge Point İstemcisi
```powershell
# Proje klasörüne gidin (yeni bir terminal açın)
cd "C:\Users\emirh\OneDrive\Masaüstü\Anomali_Test"

# CP istemcisini çalıştırın
python cp_client.py
```

**Beklenen Çıktı:**
```
CP (FİZİKSEL GERÇEKLİK): V2G Satışı
   Gönderilen Değer: -10000 Wh (10 kWh deşarj)
...
CSMS: CP_001 istasyonundan MeterValues alındı.
Gelen Değer: -10000.0 Wh
✓ Normal: -10000.0 Wh V2G satışı kaydedildi.
```

---

### Senaryo 2: Anomali (MitM Saldırısı ile)

#### Terminal 1: CSMS Sunucusu
```powershell
# Proje klasörüne gidin
cd "C:\Users\emirh\OneDrive\Masaüstü\Anomali_Test"

# CSMS sunucusunu başlatın
python csms_server.py
```

**Beklenen Çıktı:**
```
CSMS WebSocket Sunucusu 9000 portunda çalışıyor...
```

#### Terminal 2: MitM Proxy (Saldırı Scripti)
```powershell
# Proje klasörüne gidin (yeni bir terminal açın)
cd "C:\Users\emirh\OneDrive\Masaüstü\Anomali_Test"

# MitM proxy'yi başlatın (8080 portunda dinleyecek)
mitmdump -s attack_script.py --listen-port 8080
```

**Beklenen Çıktı:**
```
Loading script attack_script.py
Proxy server listening at http://*:8080
```

**Not:** MitM proxy çalışırken, CP istemcisinin proxy üzerinden bağlanması için `cp_client.py` dosyasını güncellemeniz gerekebilir. Ancak, WebSocket proxy desteği için ek yapılandırma gerekebilir.

#### Terminal 3: Charge Point İstemcisi
```powershell
# Proje klasörüne gidin (yeni bir terminal açın)
cd "C:\Users\emirh\OneDrive\Masaüstü\Anomali_Test"

# CP istemcisini çalıştırın
python cp_client.py
```

**Beklenen Çıktı (Anomali ile):**
```
CP (FİZİKSEL GERÇEKLİK): V2G Satışı
   Gönderilen Değer: -10000 Wh (10 kWh deşarj)
...
CSMS: CP_001 istasyonundan MeterValues alındı.
Gelen Değer: 10000.0 Wh
⚠️  ANOMALİ TESPİT EDİLDİ!
   Beklenen: Negatif değer (V2G satışı)
   Gelen: Pozitif değer (Enerji alımı)
   CSMS KAYDI (ANOMALİ): Sisteme 10000.0 Wh enerji GİRİŞİ kaydedildi.
```

---

## ⚠️ Önemli Notlar

### MitM Proxy Kullanımı

Mitmproxy'nin WebSocket desteği sınırlı olabilir. Eğer MitM proxy çalışmıyorsa:

1. **Alternatif 1:** Doğrudan test (MitM olmadan)
   - Sadece Terminal 1 ve Terminal 2'yi kullanın
   - Normal işleyişi test edin

2. **Alternatif 2:** Manuel test
   - `cp_client.py` dosyasındaki değeri manuel olarak değiştirin
   - `value=str(-10000)` yerine `value=str(10000)` yapın
   - Anomali senaryosunu simüle edin

### Terminal Sırası

1. **Önce CSMS sunucusunu başlatın** (Terminal 1)
2. **Sonra MitM proxy'yi başlatın** (Terminal 2 - sadece anomali senaryosu için)
3. **En son CP istemcisini çalıştırın** (Terminal 3)

### Çıkış

Herhangi bir terminalde `Ctrl+C` tuşlarına basarak programı durdurabilirsiniz.

---

## 🔧 Sorun Giderme

### Port Zaten Kullanımda
```powershell
# Portu kontrol edin
netstat -ano | findstr :9000
netstat -ano | findstr :8080

# Portu kullanan işlemi sonlandırın (PID'yi değiştirin)
taskkill /PID <PID_NUMARASI> /F
```

### Paket Bulunamadı
```powershell
# Paketleri yeniden yükleyin
pip install --upgrade -r requirements.txt
```

### WebSocket Bağlantı Hatası
- CSMS sunucusunun çalıştığından emin olun
- Port numaralarının doğru olduğunu kontrol edin
- Firewall ayarlarını kontrol edin

---

## 📊 Test Sonuçları

### Normal İşleyiş
- ✅ CP: -10000 Wh gönderir
- ✅ CSMS: -10000 Wh alır ve V2G satışı olarak kaydeder

### Anomali Senaryosu
- ✅ CP: -10000 Wh gönderir (fiziksel gerçeklik)
- ⚠️ MitM: Değeri +10000 Wh'ye çevirir
- ⚠️ CSMS: +10000 Wh alır ve anomali tespit eder

