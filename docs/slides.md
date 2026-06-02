# URL Shortener Service - Sunum Slaytlari
*Bulut Mimarilerinde Test Muhendisligi (MTH2526-B25) - Donem Projesi*

---

## Slayt 1: Kapak

**URL Shortener Service**
Bulut Mimarilerinde Test Muhendisligi (MTH2526-B25) Donem Projesi

*Grup Uyeleri:* Talha Ergelen, Osman Cingoz
*Egitmen:* Busra Ayaksiz
*Tarih:* Haziran 2026

---

## Slayt 2: Problem ve Cozum

**Problem:** Uzun ve karmasik URL'lerin paylasim zorlugu, tiklama verisinin takip edilememesi.

**Cozum:** Mikro servis tabanli, bulut teknolojileri ile izlenebilir bir link kisaltma servisi.

**Temel Ozellikler:**
- Orijinal URL'yi `http://host/abc123` formuna cevirme
- Yonlendirme (HTTP 301) ve Tiklama Analizi
- 8 REST API endpoint, Swagger Docs ve HTML UI
- Docker, K8s, Prometheus, Grafana ve OpenTelemetry entegrasyonu
- LocalStack S3 ile bulut depolama

---

## Slayt 3: Mimari Diyagram

```
  KULLANICI (Tarayici / cURL / Playwright / Newman)
                      |
                      v
  +---------------------------------------------+
  |      FastAPI  (Python 3.11) - Port 8000      |
  |  main.py | crud.py | schemas.py | models.py  |
  |  shortener.py | metrics.py | aws_client.py   |
  |  tracing.py (OpenTelemetry - Bonus)          |
  +------+----------+-----------+-------+--------+
         |          |           |       |
         v          v           v       v
    SQLite DB   LocalStack   Prometheus  Jaeger
    (URL,Click)  S3 :4566    :9090       :16686
                                |
                                v
                          Grafana :3000
                          (6 Panel Dashboard)
```

**Teknoloji Yigini:** FastAPI, SQLAlchemy, Pydantic, Docker, Minikube, Helm

---

## Slayt 4: Test Stratejisi ve Test Piramidi

```
          /\           E2E (Playwright)       -->  5 senaryo
         /  \          Postman / Newman        -->  8 istek
        /----\         Integration (API + DB)  --> 39 test
       /      \        Unit (is mantigi)       --> 42 test
      /--------\       ________________________________
     /  TOPLAM:  \     87 test + 8 Postman = 95 kontrol
    /--------------\   Coverage: >= %90
```

| Katman | Arac | Test Sayisi |
|--------|------|-------------|
| Unit | Pytest, Factory Boy, Faker | 42 |
| Integration | TestClient, Testcontainers (PostgreSQL) | 39 |
| E2E | Playwright (Chromium headless) | 5 senaryo |
| API | Postman/Newman | 8 istek |
| Performans | k6 | 1 senaryo (100 VU) |

---

## Slayt 5: CI/CD Pipeline (GitHub Actions)

**7 Job'lik Pipeline - Tek workflow, her push/PR'da otomatik:**

```
  PUSH/PR --> [1.Lint] --> [2.Pytest+Cov] --> [3.Postman]
                                   |
                          [4.Docker Build]
                                   |
                          [5.K8s Deploy (Minikube)]
                                   |
                       +-----------+-----------+
                       |                       |
                [6.Smoke Test]        [7.E2E Playwright]
```

| Job | Icerik | Sure |
|-----|--------|------|
| 1. Lint | Flake8 - PEP 8 kontrolu | ~5s |
| 2. Test | Pytest + Coverage >= %70 | ~25s |
| 3. Postman | Newman ile 8 API testi | ~15s |
| 4. Docker | Multi-stage build + Healthcheck | ~30s |
| 5. K8s | Minikube deploy + rollout | ~60s |
| 6. Smoke | /health ve /shorten kontrolu | ~10s |
| 7. E2E | Playwright 5 senaryo | ~30s |

---

## Slayt 6: Performans Testi (k6)

**Arac:** k6 v0.51.0
**Senaryo:** 4 fazli ramping (Isinma -> Normal -> Pik -> Soguma), max 100 VU
**Karisim:** %40 Shorten, %30 Redirect, %20 Stats, %10 List

| Metrik | Hedef | Sonuc |
|--------|-------|-------|
| p95 Latency | < 500 ms | **87 ms** |
| p99 Latency | - | **214 ms** |
| Hata Orani | < %5 | **%0.42** |
| Toplam Istek | - | **14.832** |
| RPS | - | **98.9 req/s** |

**Endpoint Bazli p95:** POST /shorten 112ms, GET redirect 31ms, GET stats 42ms

---

## Slayt 7: Monitoring ve Metrikler

**Prometheus + Grafana (6 Panel Dashboard):**

| # | Panel | Sorgu |
|---|-------|-------|
| 1 | Toplam URL | url_shortener_urls_created_total |
| 2 | Toplam Redirect | url_shortener_redirects_total |
| 3 | Aktif URL | url_shortener_active_urls |
| 4 | Hata Orani | rate(url_shortener_errors_total[5m]) |
| 5 | p95 Gecikme | histogram_quantile(0.95, ...) |
| 6 | RPS | rate(http_requests_total[1m]) |

**LocalStack S3:** Istatistik verileri periyodik olarak S3 bucket'ina JSON olarak yuklenir.
**OpenTelemetry + Jaeger (Bonus):** Dagitik izleme, her istegin span bazli takibi.

---

## Slayt 8: Sayilarla Proje Ozeti

| Metrik | Deger |
|--------|-------|
| Kaynak kodu | ~4.500 satir |
| Test sayisi | 87 fonksiyon + 8 Postman |
| Coverage | %90 |
| CI/CD job sayisi | 7 |
| Grafana panel | 6 |
| Docker imaj | ~150 MB |
| k6 p95 | 87 ms |
| Bonus | 4 ozellik (+15 puan tavan) |

**Bonus Ozellikler:**
- Helm Chart paketleme (+5)
- KEDA event-driven autoscaling (+5)
- ArgoCD GitOps (+5)
- OpenTelemetry distributed tracing (+5)

---

## Slayt 9: Zorluklar ve Ogrendiklerimiz

**Karsilasilan Zorluklar:**
1. CI/CD ortam farkliliklari (ModuleNotFoundError - PYTHONPATH cozumu)
2. Testcontainers Docker-in-Docker izin sorunlari
3. Playwright selektor uyumsuzlugu (UI degisikligi sonrasi)

**Ogrenilen Dersler:**
- Test piramidi katmanlari birbirini tamamliyor
- Multi-stage Docker ile %80 imaj kucultme
- Observability ucgeni: Metrik + Log + Trace = hizli hata tespiti

**Ileride Yapilabilecekler:**
- Redis cache, PostgreSQL gecisi, Rate limiting, Vanity URL

---

## Slayt 10: Tesekkurler ve Q&A

Projemizi dinlediginiz icin tesekkur ederiz.

**Canli Demo'ya gecis yapiyoruz.**

*(Sorulariniz?)*

GitHub: https://github.com/talhaergelen/bmtm-url_shortener_service
