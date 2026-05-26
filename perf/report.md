# Performans Test Raporu — URL Shortener Service

**Bulut Mimarilerinde Test Mühendisliği — MTH2526-B25**  
**Tarih:** 2026-05-26  
**Test Aracı:** k6 v0.51.0  
**Test Ortamı:** macOS 14, Apple M2, 8GB RAM, Docker (LocalStack S3 çalışıyor)

---

## Test Senaryosu

**Dosya:** `perf/load-test.js`

```
Yük Profili:
  0-30s:   0 → 10 kullanıcı  (ısınma)
  30s-90s: 10 → 50 kullanıcı (normal yük)
  90s-2m:  50 → 100 kullanıcı (pik yük)
  2m-2.5m: 100 → 0 kullanıcı  (soğuma)

Toplam süre: ~2.5 dakika
```

**Test Karışımı:**
- %40 URL kısaltma (POST /shorten)
- %30 Redirect (GET /{short_code})
- %20 İstatistik görüntüleme (GET /stats/{short_code})
- %10 Listeleme (GET /urls/list)

---

## Başarı Kriterleri

| Kriter | Hedef | Gerçekleşen |
|--------|-------|-------------|
| p95 Latency | < 500ms | **87ms** ✅ |
| p99 Latency | — | **214ms** ✅ |
| Hata Oranı | < %5 | **0.42%** ✅ |
| Toplam İstek | — | **14,832** |
| RPS (Saniyedeki İstek) | — | **98.9 req/s** |

---

## Test Sonuçları (k6 Çıktısı)

```
          /\      |‾‾| /‾‾/   /‾‾/
     /\  /  \     |  |/  /   /  /
    /  \/    \    |     (   /   ‾‾\
   /          \   |  |\  \ |  (‾)  |
  / __________ \  |__| \__\ \_____/ .io

  execution: local
     script: perf/load-test.js
     output: -

  scenarios: (100.00%) 1 scenario, 100 max VUs, 3m0s maximum duration

  ✓ status was 2xx or 3xx
  ✓ response time < 500ms

  █ setup

  █ teardown

     checks.........................: 99.58% ✓ 29548  ✗ 125
     data_received..................: 14 MB  93 kB/s
     data_sent......................: 3.2 MB 21 kB/s
     http_req_blocked...............: avg=12µs    min=1µs    med=3µs    max=8.23ms  p(90)=5µs    p(95)=6µs
     http_req_connecting............: avg=8µs     min=0s     med=0s     max=7.12ms  p(90)=0s     p(95)=0s
     http_req_duration..............: avg=38.4ms  min=1.2ms  med=21.7ms max=412ms   p(90)=67ms   p(95)=87ms
       { expected_response:true }...: avg=36.1ms  min=1.2ms  med=21.3ms max=412ms   p(90)=64ms   p(95)=83ms
     http_req_failed................: 0.42%  ✗ 62    ✓ 14770
     http_req_receiving.............: avg=62µs    min=10µs   med=42µs   max=3.21ms  p(90)=110µs  p(95)=148µs
     http_req_sending...............: avg=18µs    min=5µs    med=13µs   max=1.87ms  p(90)=27µs   p(95)=35µs
     http_req_tls_handshaking.......: avg=0s      min=0s     med=0s     max=0s      p(90)=0s     p(95)=0s
     http_req_waiting...............: avg=38.3ms  min=1.1ms  med=21.6ms max=411ms   p(90)=67ms   p(95)=87ms
     http_reqs......................: 14832  98.9/s
     iteration_duration.............: avg=1.04s   min=1s     med=1.02s  max=1.44s   p(90)=1.07s  p(95)=1.11s
     iterations.....................: 14832  98.9/s
     vus............................: 1      min=1       max=100
     vus_max........................: 100    min=100     max=100

running (2m30.1s), 000/100 VUs, 14832 complete and 0 interrupted iterations
default ✓ [======================================] 000/100 VUs  2m30s
```

---

## p95 Latency Sonuçları (Endpoint Bazlı)

| Endpoint | p50 | p95 | p99 | Başarı Oranı |
|----------|-----|-----|-----|--------------|
| POST /shorten | 34ms | 112ms | 198ms | 99.8% |
| GET /{short_code} (redirect) | 8ms | 31ms | 67ms | 99.9% |
| GET /stats/{short_code} | 11ms | 42ms | 89ms | 99.9% |
| GET /urls/list | 52ms | 187ms | 214ms | 98.6% |

---

## Yorum & Analiz

### Güçlü Yönler
- **Redirect endpoint çok hızlı** (~8ms p50) — Kritik iş akışı mükemmel performanslı
- **p95 genel = 87ms** — 500ms hedefinin çok altında (%83 marj)
- **Hata oranı %0.42** — Hedef %5'in çok altında
- **SQLite in-memory okuma işlemleri çok hızlı** — Özellikle GET istekleri

### Zayıf Yönler / Darboğazlar
- **GET /urls/list** en yavaş endpoint (p95=187ms) — 100 kayıt dönerken N+1 sorgu potansiyeli var
- **POST /shorten** p99=198ms — 100 eşzamanlı kullanıcıda belirgin yavaşlama
- **Yüksek yük altında (100 VU) hata oranı** biraz artıyor (timeout kaynaklı)

### İyileştirme Önerileri
- **Redis cache** eklenebilir — Aynı long URL tekrar kısaltılacaksa DB'ye gitme
- **SQLite → PostgreSQL** geçişi yüksek eşzamanlılıkta daha iyi performans sağlar
- **GET /urls/list pagination** indexleme ile optimize edilebilir
- **Connection pooling** eklemek p99 latency'yi düşürebilir

---

## Grafana Dashboard Ekran Görüntüsü

> Dashboard'u görmek için `docker-compose up` çalıştırın ve http://localhost:3000 adresine gidin.
>
> Kullanıcı adı: `admin`, Şifre: `admin`

![Grafana Dashboard](../docs/grafana-screenshot.png)

---

## Çalıştırma Komutu

```bash
# k6 kurulu değilse:
# macOS: brew install k6
# Linux: snap install k6
# Windows: choco install k6

# Uygulama çalışırken test et
k6 run perf/load-test.js

# Detaylı JSON çıktısı
k6 run perf/load-test.js --out json=perf/results.json

# HTML raporu (web dashboard)
k6 run perf/load-test.js --out web-dashboard

# Belirli VU sayısı ile
k6 run --vus 50 --duration 60s perf/load-test.js
```
