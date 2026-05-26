# Performans Test Raporu — URL Shortener Service

**Bulut Mimarilerinde Test Mühendisliği — MTH2526-B25**  
**Tarih:** *[Test tarihi]*  
**Test Aracı:** k6

---

## Test Senaryosu

**Dosya:** `perf/load-test.js`

```
Yük Profili:
  0-30s:   0 → 10 kullanıcı  (ısınma)
  30s-90s: 10 → 50 kullanıcı (normal yük)
  90s-2m:  50 → 100 kullanıcı (pik yük)
  2m-2.5m: 100 → 0 kullanıcı  (soğuma)
```

**Test Karışımı:**
- %40 URL kısaltma (POST /shorten)
- %30 Redirect (GET /{short_code})
- %20 İstatistik görüntüleme (GET /stats/{short_code})
- %10 Listeleme (GET /urls/list)

---

## Başarı Kriterleri

| Kriter | Hedef | Gerçekleşen |
|--------|-------|------------|
| p95 Latency | < 500ms | *[doldur]* ms |
| p99 Latency | — | *[doldur]* ms |
| Hata Oranı | < %5 | *[doldur]* % |
| Toplam İstek | — | *[doldur]* |
| RPS (Saniyedeki İstek) | — | *[doldur]* |

---

## Test Sonuçları

> Bu bölümü k6 çıktısıyla doldurun:
> ```bash
> k6 run perf/load-test.js
> ```

```
          /\      |‾‾| /‾‾/   /‾‾/   
     /\  /  \     |  |/  /   /  /    
    /  \/    \    |     (   /   ‾‾\  
   /          \   |  |\  \ |  (‾)  | 
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: perf/load-test.js

  scenarios: (100.00%) 1 scenario, 100 max VUs

[Buraya k6 çıktısını yapıştırın]
```

---

## p95 Latency Sonuçları (Endpoint Bazlı)

| Endpoint | p50 | p95 | p99 | Başarı Oranı |
|----------|-----|-----|-----|--------------|
| POST /shorten | *?* ms | *?* ms | *?* ms | *?* % |
| GET /{short_code} (redirect) | *?* ms | *?* ms | *?* ms | *?* % |
| GET /stats/{short_code} | *?* ms | *?* ms | *?* ms | *?* % |
| GET /urls/list | *?* ms | *?* ms | *?* ms | *?* % |

---

## Yorum & Analiz

### Güçlü Yönler
- *[Örnek: SQLite veritabanı okuma işlemleri çok hızlı (~5ms)]*
- *[Örnek: /health endpoint her zaman <10ms yanıt veriyor]*

### Zayıf Yönler / Darboğazlar
- *[Örnek: POST /shorten 100 kullanıcıda zaman zaman yavaşlıyor]*

### İyileştirme Önerileri
- *[Örnek: Redis cache eklenebilir — aynı URL'yi tekrar kısaltmak için DB'ye gitmeden cache'den yanıt ver]*
- *[Örnek: SQLite yerine PostgreSQL ile daha yüksek eşzamanlılık sağlanabilir]*

---

## Grafana Dashboard Ekran Görüntüsü

> Buraya Grafana'dan alınan ekran görüntüsü eklenecek.

![Grafana Dashboard](../docs/grafana-screenshot.png)

---

## Çalıştırma Komutu

```bash
# k6 kurulu değilse: https://k6.io/docs/get-started/installation/

# Uygulama çalışırken test et
k6 run perf/load-test.js

# Detaylı JSON çıktısı
k6 run perf/load-test.js --out json=perf/results.json

# HTML raporu
k6 run perf/load-test.js --out web-dashboard
```
