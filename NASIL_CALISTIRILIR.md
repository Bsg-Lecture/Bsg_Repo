# EmuOCPP Nasıl Çalıştırılır? 🚀

## Hızlı Başlangıç (3 Yöntem)

### ✅ Yöntem 1: Hızlı Demo (EN KOLAY - 30 saniye)

Sadece battery degradation simülasyonunu test et (server gerekmez):

```bash
# En basit
python quick_demo.py

# Veya wrapper ile
python run_attack.py --cycles 10
```

**Ne yapar?**
- 10 şarj döngüsü simüle eder
- Battery degradation hesaplar
- Sonuçları `./output/demo/` klasörüne kaydeder
- CSV ve JSON formatında raporlar oluşturur

**Sonuçlar:**
```
./output/demo/session_demo_YYYYMMDD_HHMMSS/
├── charging_cycles.csv          # Şarj döngüsü verileri
├── degradation_timeline.csv     # SoH zaman çizelgesi
├── summary.json                 # Özet istatistikler
└── config.json                  # Kullanılan konfigürasyon
```

---

### ✅ Yöntem 2: Baseline Karşılaştırma (TAM SİMÜLASYON)

Attack'li ve attack'siz simülasyonları karşılaştır:

#### Adım 1: Baseline (Normal) Simülasyon

```bash
python EmuOCPP/run_baseline_simulation.py --cycles 100
```

**Ne yapar?**
- Attack olmadan 100 şarj döngüsü simüle eder
- Normal battery degradation'ı ölçer
- Sonuçları `./output/baseline/` klasörüne kaydeder

#### Adım 2: Attack Simülasyonu

```bash
python EmuOCPP/attack_simulator.py --config EmuOCPP/attack_simulation/config/attack_config.yaml --cycles 100
```

**Ne yapar?**
- Attack ile 100 şarj döngüsü simüle eder
- Charging profile'ları manipüle eder
- Hızlandırılmış degradation'ı ölçer
- Sonuçları `./output/attack/` klasörüne kaydeder

#### Adım 3: Karşılaştırma

```bash
python EmuOCPP/run_comparison_analysis.py
```

**Ne yapar?**
- Baseline ve attack sonuçlarını karşılaştırır
- Degradation acceleration factor hesaplar
- Karşılaştırma raporu oluşturur: `./output/comparison_report.txt`

**Örnek Çıktı:**
```
Degradation Acceleration Factor: 3.5x
Additional Degradation: 2.5%
Baseline: 80% SoH at 1200 cycles
Attack: 80% SoH at 340 cycles
```

---

### ✅ Yöntem 3: Tam OCPP Simülasyonu (GERÇEK MITM ATTACK)

EmuOCPP server ve client ile gerçek OCPP iletişimi:

#### Terminal 1: Server Başlat

```bash
python EmuOCPP/charging/server.py
```

**Çıktı:**
```
Server listening on ws://127.0.0.1:9000
Waiting for connections...
```

#### Terminal 2: MITM Proxy ile Attack Simulator

```bash
python EmuOCPP/attack_simulator.py --config EmuOCPP/attack_simulation/config/attack_config.yaml --cycles 100 --with-proxy
```

**Ne yapar?**
- MITM proxy başlatır (port 9001)
- OCPP mesajlarını intercept eder
- SetChargingProfile mesajlarını manipüle eder
- Battery degradation simüle eder

#### Terminal 3: Client Başlat

Client'ı proxy'ye bağla (server'a değil):

```bash
# client_config.yaml'de csms_url'yi değiştir:
# csms_url: ws://127.0.0.1:9001/  (proxy port)

python EmuOCPP/charging/client.py
```

---

## Detaylı Kullanım

### Konfigürasyon Dosyaları

#### Attack Konfigürasyonu

`EmuOCPP/attack_simulation/config/attack_config.yaml`:

```yaml
attack_config:
  enabled: true
  strategy: "aggressive"  # aggressive, subtle, random, targeted
  
  manipulations:
    voltage:
      enabled: true
      deviation_percent: 15  # %15 artır
    current:
      enabled: true
      deviation_percent: 25  # %25 artır
    charging_curve:
      enabled: true
      modification_type: "flatten"

simulation:
  cycles: 1000
  cycle_duration_hours: 2.0
```

#### Strateji Değiştirme

**Aggressive (Agresif):**
```yaml
strategy: "aggressive"
# Maksimum degradation için
```

**Subtle (Gizli):**
```yaml
strategy: "subtle"
# Tespit edilmesi zor, minimal değişiklikler
```

**Random (Rastgele):**
```yaml
strategy: "random"
# Rastgele manipülasyonlar
```

**Targeted (Hedefli):**
```yaml
strategy: "targeted"
# Sadece belirli parametreleri hedefle
```

---

## Komut Satırı Seçenekleri

### attack_simulator.py

```bash
python EmuOCPP/attack_simulator.py [OPTIONS]
```

**Seçenekler:**

| Seçenek | Açıklama | Örnek |
|---------|----------|-------|
| `--config FILE` | Attack konfigürasyon dosyası | `--config attack_config.yaml` |
| `--cycles N` | Şarj döngüsü sayısı | `--cycles 1000` |
| `--output-dir DIR` | Çıktı klasörü | `--output-dir ./results` |
| `--log-level LEVEL` | Log seviyesi | `--log-level DEBUG` |
| `--with-proxy` | MITM proxy ile çalıştır | `--with-proxy` |
| `--dry-run` | Sadece konfigürasyonu test et | `--dry-run` |

**Örnekler:**

```bash
# Basit simülasyon
python EmuOCPP/attack_simulator.py --config attack_config.yaml --cycles 100

# Debug modu ile
python EmuOCPP/attack_simulator.py --config attack_config.yaml --log-level DEBUG

# Özel çıktı klasörü
python EmuOCPP/attack_simulator.py --config attack_config.yaml --output-dir ./my_results

# Konfigürasyon testi (çalıştırmadan)
python EmuOCPP/attack_simulator.py --config attack_config.yaml --dry-run
```

### run_baseline_simulation.py

```bash
python EmuOCPP/run_baseline_simulation.py [OPTIONS]
```

**Seçenekler:**

| Seçenek | Açıklama | Örnek |
|---------|----------|-------|
| `--cycles N` | Şarj döngüsü sayısı | `--cycles 1000` |
| `--output-dir DIR` | Çıktı klasörü | `--output-dir ./baseline` |

---

## Sonuçları İnceleme

### CSV Dosyaları

**charging_cycles.csv:**
```csv
cycle_num,timestamp,duration_hours,energy_kwh,voltage_avg,current_avg,soc_min,soc_max,soh_before,soh_after,degradation_percent
1,2024-11-11T00:00:00,2.0,50.0,4.2,0.5,20.0,80.0,100.0,99.997,0.003
```

**degradation_timeline.csv:**
```csv
timestamp,cycle_num,soh,voltage_stress,current_stress,soc_stress,combined_stress
2024-11-11T00:00:00,1,99.997,1.284,1.0,1.0,1.284
```

### JSON Özet

**summary.json:**
```json
{
  "session_id": "attack_20241111_120000",
  "total_cycles": 1000,
  "initial_soh": 100.0,
  "final_soh": 92.5,
  "total_degradation": 7.5,
  "degradation_rate_per_cycle": 0.0075
}
```

### Karşılaştırma Raporu

**comparison_report.txt:**
```
=== BASELINE VS ATTACK COMPARISON ===

Baseline:
  - Final SoH: 97.5%
  - Total Degradation: 2.5%
  - Cycles to 80% SoH: 1200

Attack:
  - Final SoH: 92.5%
  - Total Degradation: 7.5%
  - Cycles to 80% SoH: 340

Impact:
  - Degradation Acceleration Factor: 3.0x
  - Additional Degradation: 5.0%
  - Cycles Saved (for attacker): 860 cycles
```

---

## Batch Simülasyon (Çoklu Senaryo)

Birden fazla senaryoyu aynı anda çalıştır:

```bash
python EmuOCPP/attack_simulator.py --batch EmuOCPP/attack_simulation/config/batch_config.yaml
```

**batch_config.yaml:**
```yaml
batch_config:
  name: "Comparative Study"
  output_dir: "./results/batch_001"
  
  scenarios:
    - name: "baseline"
      attack_enabled: false
      cycles: 1000
      
    - name: "aggressive_voltage"
      attack_enabled: true
      strategy: "aggressive"
      cycles: 1000
      manipulations:
        voltage:
          enabled: true
        current:
          enabled: false
          
    - name: "aggressive_current"
      attack_enabled: true
      strategy: "aggressive"
      cycles: 1000
      manipulations:
        voltage:
          enabled: false
        current:
          enabled: true
```

**Sonuç:**
```
./results/batch_001/
├── baseline/
│   └── session_baseline_*/
├── aggressive_voltage/
│   └── session_aggressive_voltage_*/
├── aggressive_current/
│   └── session_aggressive_current_*/
└── comparison_report.txt
```

---

## Örnek Scriptler

### Demo Scriptleri

```bash
# Battery model demo
python EmuOCPP/attack_simulation/examples/demo_battery_model.py

# Attack engine demo
python EmuOCPP/attack_simulation/examples/demo_attack_engine.py

# Metrics collector demo
python EmuOCPP/attack_simulation/examples/demo_metrics_collector.py

# Visualization demo
python EmuOCPP/attack_simulation/examples/demo_visualization.py

# Baseline comparison demo
python EmuOCPP/attack_simulation/examples/demo_baseline_comparison.py
```

### Validation Scriptleri

```bash
# Baseline validation
python EmuOCPP/attack_simulation/examples/validation_baseline.py

# Aggressive attack validation
python EmuOCPP/attack_simulation/examples/validation_aggressive.py

# Subtle attack validation
python EmuOCPP/attack_simulation/examples/validation_subtle.py

# Tam validation suite
python EmuOCPP/attack_simulation/examples/run_full_validation.py
```

---

## Sorun Giderme

### Hata: "ModuleNotFoundError"

```bash
# Çözüm: Dependencies'leri yükle
pip install -r EmuOCPP/requirements.txt
```

### Hata: "Connection refused"

```bash
# Çözüm: Server'ın çalıştığından emin ol
python EmuOCPP/charging/server.py
```

### Hata: "FileNotFoundError: config file"

```bash
# Çözüm: Tam path kullan
python EmuOCPP/attack_simulator.py --config EmuOCPP/attack_simulation/config/attack_config.yaml
```

### Hata: "Permission denied: output directory"

```bash
# Çözüm: Output klasörünü manuel oluştur
mkdir output
```

---

## İleri Seviye Kullanım

### Custom Attack Stratejisi

```python
from attack_simulation.core import AttackEngine, AttackConfig

# Custom config
config = AttackConfig(
    enabled=True,
    strategy="targeted",
    voltage_enabled=True,
    voltage_deviation_percent=12.0,
    current_enabled=False
)

engine = AttackEngine(config)
```

### Anomaly Detection

```bash
# Detection ile çalıştır
python EmuOCPP/attack_simulator.py \
    --config EmuOCPP/attack_simulation/config/detection_config.yaml \
    --cycles 1000
```

### Publication Materials

```bash
# Yayın için materyaller oluştur
python EmuOCPP/attack_simulation/examples/generate_publication_materials.py
```

**Oluşturur:**
- High-resolution plots (PNG, PDF)
- LaTeX tables
- Summary statistics
- Comparison reports

---

## Hızlı Referans

| Görev | Komut |
|-------|-------|
| Hızlı demo | `python quick_demo.py` |
| Attack simülasyon (kolay) | `python run_attack.py --cycles 100` |
| Baseline simülasyon | `python run_baseline_simulation.py --cycles 100` |
| Attack simülasyon (tam) | `python attack_simulator.py --config attack_simulation/config/attack_config.yaml --cycles 100` |
| Karşılaştırma | `python run_comparison_analysis.py` |
| Server başlat | `python charging/server.py` |
| Client başlat | `python charging/client.py` |
| Testleri çalıştır | `python run_tests.py` |
| Config doğrula | `python validate_config.py` |

---

## Daha Fazla Bilgi

- **Tam Dokümantasyon**: [ATTACK_SIMULATION_README.md](ATTACK_SIMULATION_README.md)
- **API Referansı**: [attack_simulation/API_REFERENCE.md](attack_simulation/API_REFERENCE.md)
- **Kullanım Kılavuzu**: [attack_simulation/USAGE_GUIDE.md](attack_simulation/USAGE_GUIDE.md)
- **Sorun Giderme**: [attack_simulation/TROUBLESHOOTING_GUIDE.md](attack_simulation/TROUBLESHOOTING_GUIDE.md)
- **Etik Kurallar**: [attack_simulation/ETHICAL_USE_GUIDELINES.md](attack_simulation/ETHICAL_USE_GUIDELINES.md)

---

**İyi Çalışmalar! 🚀**
