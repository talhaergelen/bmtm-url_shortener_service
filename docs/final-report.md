# URL Shortener Service — Final Proje Raporu

**Ders:** MTH2526-B25 — Bulut Mimarilerinde Test Mühendisliği  
**Dönem:** 2025–2026 Bahar Yarıyılı  
**Eğitmen:** Büşra Ayaksız  
**Proje Konusu:** Konu #1 — URL Shortener Service  
**Tarih:** 2 Haziran 2026  
**GitHub:** https://github.com/talhaergelen/bmtm-url_shortener_service

---

## Grup Üyeleri

| İsim | Öğrenci No | Rol |
|------|-----------|-----|
| Talha Ergelen | 171423013 | Tech Lead / Repo Sahibi |
| Osman Çingöz | 170423029 | Backend & DevOps |

---

## 1. Giriş

### 1.1 Projenin Amacı

Bu projenin amacı, ders boyunca edinilen test mühendisliği bilgi ve araçlarını birleştirerek küçük bir mikroservise endüstri standardında bir uçtan uca (E2E) test boru hattı kurmaktır. Konu olarak **URL Shortener Service** (Kısa Link Servisi) seçilmiştir. Bu servis uzun URL'leri 6 karakterlik kısa kodlara dönüştürür, HTTP 301 ile yönlendirme yapar ve her tıklamayı kayıt altına alarak istatistik sunar.

### 1.2 Neden Bu Konu?

URL kısaltma servisi, CRUD (Oluştur/Oku/Güncelle/Sil) operasyonlarının tamamını doğal olarak içermesi, yönlendirme mantığının test edilebilirliği ve istatistik toplama özelliği sayesinde çok katmanlı test stratejisini uygulamak için ideal bir alan sunmaktadır. Servisin basitliği, odağı uygulama karmaşıklığından **test altyapısı kalitesine** kaydırmamıza olanak tanımıştır.

### 1.3 Kapsam

Proje aşağıdaki teknoloji ve araçları kapsamaktadır:

- **Backend:** Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic v2
- **Veritabanı:** SQLite (geliştirme), PostgreSQL (Testcontainers ile entegrasyon testi)
- **Test:** Pytest, Factory Boy, Faker, Playwright, Newman/Postman, k6
- **Konteyner:** Docker (Multi-stage), docker-compose
- **Orkestrasyon:** Kubernetes (Minikube), Helm Chart
- **CI/CD:** GitHub Actions (7 job'lık pipeline)
- **İzleme:** Prometheus, Grafana (6 panel), OpenTelemetry + Jaeger
- **Bulut:** LocalStack (AWS S3 emülasyonu)

---

## 2. Sistem Mimarisi

### 2.1 Mimari Diyagram

Aşağıdaki diyagram, sistemin tüm bileşenlerini ve aralarındaki veri akışını göstermektedir. Diyagramın PNG versiyonu `docs/architecture.png` dosyasında yer almaktadır.

```
┌──────────────────────────────────────────────────────────────────┐
│                        KULLANICI KATMANI                         │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │  Tarayıcı   │  │   cURL /    │  │   Playwright / Newman   │  │
│  │  (HTML UI)  │  │   Postman   │  │   (Otomatik Testler)    │  │
│  └──────┬──────┘  └──────┬──────┘  └────────────┬────────────┘  │
└─────────┼────────────────┼──────────────────────┼───────────────┘
          │                │                      │
          ▼                ▼                      ▼
┌──────────────────────────────────────────────────────────────────┐
│                      UYGULAMA KATMANI                            │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │              FastAPI (Python 3.11) — Port 8000             │  │
│  │                                                            │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │  │
│  │  │ main.py  │ │ crud.py  │ │schemas.py│ │ shortener.py │  │  │
│  │  │ 8 REST   │ │ CRUD     │ │ Pydantic │ │ Kod üretim   │  │  │
│  │  │ endpoint │ │ işlemleri│ │ doğrulama│ │ algoritması  │  │  │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐                   │  │
│  │  │metrics.py│ │aws_client│ │tracing.py│                   │  │
│  │  │Prometheus│ │ S3 client│ │OpenTeleme│                   │  │
│  │  │ exporter │ │LocalStack│ │try+Jaeger│                   │  │
│  │  └────┬─────┘ └────┬─────┘ └────┬─────┘                   │  │
│  └───────┼────────────┼────────────┼─────────────────────────┘  │
└──────────┼────────────┼────────────┼────────────────────────────┘
           │            │            │
     ┌─────▼─────┐ ┌────▼─────┐ ┌───▼──────┐  ┌──────────────┐
     │Prometheus │ │LocalStack│ │  Jaeger   │  │   SQLite /   │
     │ :9090     │ │ S3 :4566 │ │  :16686   │  │ PostgreSQL   │
     └─────┬─────┘ └──────────┘ └──────────┘  └──────────────┘
           │
     ┌─────▼─────┐
     │  Grafana   │
     │  :3000     │
     │ (6 panel)  │
     └───────────┘
```

### 2.2 Bileşen Açıklamaları

| Bileşen | Teknoloji | Açıklama |
|---------|-----------|----------|
| **API Sunucusu** | FastAPI + Uvicorn | 8 REST endpoint; asenkron ASGI sunucu |
| **Veritabanı** | SQLAlchemy + SQLite | `URL` ve `Click` olmak üzere 2 entity; ORM tabanlı |
| **Bulut Depolama** | LocalStack S3 | İstatistik JSON dosyalarının sahte AWS S3 bucket'ına yazılması |
| **Monitoring** | Prometheus + Grafana | Metrik toplama (15s aralık) ve 6 panelli dashboard ile görselleştirme |
| **Tracing** | OpenTelemetry + Jaeger | Dağıtık izleme; her isteğin span bazlı takibi |
| **Konteyner** | Docker Multi-stage | Builder + Runtime aşaması; ~150 MB imaj boyutu |
| **Orkestrasyon** | Kubernetes (Minikube) | Deployment (2 replika), Service (NodePort), ConfigMap |

### 2.3 REST API Endpoint'leri

| Method | Endpoint | Açıklama | HTTP Kodu |
|--------|----------|----------|-----------|
| `GET` | `/health` | Sağlık kontrolü (liveness probe) | 200 |
| `POST` | `/shorten` | Yeni kısa URL oluştur | 201 |
| `GET` | `/{short_code}` | Orijinal URL'ye yönlendir | 301 |
| `GET` | `/urls/list` | Tüm URL'leri listele (pagination) | 200 |
| `GET` | `/urls/{short_code}` | Tek URL detayı | 200 |
| `GET` | `/stats/{short_code}` | Tıklama istatistikleri | 200 |
| `DELETE` | `/urls/{short_code}` | URL silme | 200 |
| `GET` | `/metrics` | Prometheus metrikleri | 200 |

---

## 3. Test Stratejisi

### 3.1 Test Piramidi Yorumu

Projede klasik **Test Piramidi** yaklaşımı benimsenmiştir. Piramidin tabanında hızlı ve izole çalışan birim testleri, ortasında API ve veritabanı entegrasyon testleri, tepesinde ise tarayıcı tabanlı E2E testleri yer almaktadır.

```
         ╱  ╲           E2E (Playwright)         →   5 senaryo
        ╱    ╲          Postman / Newman          →   8 istek
       ╱──────╲         Integration (API + DB)    →  39 test
      ╱        ╲        Unit (iş mantığı)         →  42 test
     ╱──────────╲
    ╱  TOPLAM:   ╲      87 test fonksiyonu + 8 Postman isteği
   ╱──────────────╲     Coverage: ≥ %90
```

### 3.2 Katman Bazlı Test Detayları

#### Birim Testler (Unit) — 42 test

| Dosya | Test Sayısı | Kapsam |
|-------|------------|--------|
| `test_shortener.py` | 12 | Kısa kod üretim algoritması, benzersizlik, uzunluk kontrolü |
| `test_crud.py` | 19 | Oluşturma, okuma, güncelleme, silme işlemleri; edge case'ler |
| `test_aws.py` | 11 | S3 istemci mock testleri; bağlantı hatası senaryoları |

- **İzolasyon:** Her test SQLite in-memory veritabanı ile çalışır; `conftest.py` içinde `yield` bazlı fixture ile test sonrası temizlik yapılır.
- **Veri Üretimi:** `Factory Boy` ve `Faker` kütüphaneleri ile `URLFactory` sınıfı oluşturulmuştur. Her test çalışmasında rastgele ama tutarlı test verisi üretilir.

#### Entegrasyon Testler (Integration) — 39 test

| Dosya | Test Sayısı | Kapsam |
|-------|------------|--------|
| `test_api.py` | 31 | Tüm 8 endpoint'in FastAPI TestClient ile sınanması |
| `test_database.py` | 8 | Testcontainers ile geçici PostgreSQL üzerinde CRUD doğrulama |

- **Testcontainers:** `testcontainers` kütüphanesi ile Docker üzerinde geçici PostgreSQL konteyneri otomatik başlatılır, testler koşturulur ve konteyner imha edilir. Bu, gerçek veritabanı davranışını test ortamında simüle eder.

#### E2E Testler (Playwright) — 5 senaryo

| Senaryo | Açıklama |
|---------|----------|
| 1 | Ana sayfa başarıyla yükleniyor, form elemanları görünür |
| 2 | URL kısaltma formu çalışıyor, sonuç kutusu açılıyor |
| 3 | Geçersiz URL girişinde hata mesajı gösteriliyor |
| 4 | Oluşturulan URL ana sayfadaki listede görünüyor |
| 5 | Enter tuşu ile form gönderilebiliyor (UX testi) |

#### API Testleri (Postman/Newman) — 8 istek

Newman ile CI/CD pipeline'da otomatik koşan Postman koleksiyonu 8 sıralı istekten oluşur. Her istek kendi assertion'larını içerir ve dinamik değişken aktarımı (oluşturulan `short_code`'un sonraki isteklerde kullanılması) başarıyla uygulanmıştır.

### 3.3 Coverage Hedefi ve Sonucu

| Metrik | Hedef | Gerçekleşen |
|--------|-------|-------------|
| Kod Kapsamı (Coverage) | ≥ %70 | **%90** |
| `--cov-fail-under` | 70 | CI'da zorunlu kontrol |

---

## 4. CI/CD Pipeline ve Dağıtım (Deploy)

### 4.1 GitHub Actions Workflow

`.github/workflows/ci.yml` dosyasında tanımlı tek bir workflow, 7 bağımsız job'dan oluşmaktadır. Her push ve pull request'te otomatik tetiklenir.

```
┌─────────┐     ┌──────────────────┐     ┌───────────────┐
│  PUSH / │────▶│  1. Lint (Flake8) │────▶│ 2. Pytest +   │
│   PR    │     │                  │     │   Coverage    │
└─────────┘     └──────────────────┘     └───────┬───────┘
                                                 │
                    ┌────────────────────────────┐│
                    │                            ▼│
              ┌─────┴───────┐          ┌─────────┴───────┐
              │ 3. Postman  │          │ 4. Docker Build  │
              │   Newman    │          │  (Multi-stage)   │
              └─────────────┘          └────────┬────────┘
                                                │
                                       ┌────────▼────────┐
                                       │ 5. K8s Deploy   │
                                       │   (Minikube)    │
                                       └────────┬────────┘
                                                │
                                 ┌──────────────┼──────────────┐
                                 ▼                             ▼
                        ┌────────────────┐           ┌─────────────────┐
                        │ 6. Smoke Test  │           │ 7. E2E Playwright│
                        │ (Health+API)   │           │   (5 senaryo)   │
                        └────────────────┘           └─────────────────┘
```

### 4.2 Job Detayları

| # | Job | Açıklama | Süre |
|---|-----|----------|------|
| 1 | **Lint** | Flake8 ile PEP 8 stil kontrolü | ~5s |
| 2 | **Pytest + Coverage** | 87 test + `--cov-fail-under=70` kontrolü; LocalStack S3 konteyner servisi | ~25s |
| 3 | **Postman — Newman** | 8 API isteği; uygulama Docker'da ayağa kaldırılarak test edilir | ~15s |
| 4 | **Docker Build** | Multi-stage imaj derleme; `HEALTHCHECK` ile sağlık doğrulama | ~30s |
| 5 | **K8s Deploy** | Minikube başlatma, `kubectl apply -f k8s/`, rollout bekleme | ~60s |
| 6 | **Smoke Test** | Deploy sonrası `/health` ve `/shorten` endpoint kontrolü | ~10s |
| 7 | **E2E — Playwright** | Chromium headless tarayıcıda 5 UI senaryosu | ~30s |

### 4.3 Kubernetes Manifest'leri

`k8s/` dizininde aşağıdaki manifest dosyaları bulunmaktadır:

| Dosya | İçerik |
|-------|--------|
| `deployment.yaml` | 2 replika Pod tanımı, liveness/readiness probe, kaynak limitleri |
| `service.yaml` | NodePort servisi (port 30080 → 8000) |
| `configmap.yaml` | Ortam değişkenleri (veritabanı yolu, S3 yapılandırması) |
| `keda-scaledobject.yaml` | **[Bonus]** Prometheus metriğine göre event-driven autoscaling |
| `argocd-application.yaml` | **[Bonus]** GitOps tabanlı otomatik deployment |

### 4.4 Docker Stratejisi

Multi-stage Dockerfile ile iki aşamalı build:

- **Aşama 1 (builder):** `python:3.11-slim` üzerinde `pip install --prefix=/install` ile bağımlılık kurulumu
- **Aşama 2 (runtime):** Temiz imaja sadece çalışma zamanı dosyaları kopyalanır; `appuser` (non-root) ile çalıştırılır
- **Sonuç:** ~150 MB imaj boyutu (tek aşama ~800 MB'den %80 küçülme)

---

## 5. Performans ve Gözlemlenebilirlik

### 5.1 k6 Yük Testi

`perf/load-test.js` dosyasında tanımlı senaryo, 4 fazlı ramping-VUs profili ile çalışır:

| Faz | Süre | VU Sayısı | Açıklama |
|-----|------|-----------|----------|
| Isınma | 0–30s | 0 → 10 | Bağlantı havuzu doldurma |
| Normal | 30s–90s | 10 → 50 | Tipik üretim yükü |
| Pik | 90s–2dk | 50 → 100 | Stres testi |
| Soğuma | 2dk–2.5dk | 100 → 0 | Graceful shutdown |

**Test Karışımı:** %40 POST /shorten, %30 GET /{code} (redirect), %20 GET /stats, %10 GET /urls/list

### 5.2 Performans Sonuçları

| Metrik | Hedef | Sonuç | Durum |
|--------|-------|-------|-------|
| p95 Latency | < 500 ms | **87 ms** | ✅ Başarılı |
| p99 Latency | — | **214 ms** | ✅ |
| Hata Oranı | < %5 | **%0.42** | ✅ Başarılı |
| Toplam İstek | — | **14.832** | — |
| RPS | — | **98.9 req/s** | — |

**Endpoint Bazlı p95:**

| Endpoint | p50 | p95 | Başarı |
|----------|-----|-----|--------|
| POST /shorten | 34ms | 112ms | %99.8 |
| GET /{code} (redirect) | 8ms | 31ms | %99.9 |
| GET /stats/{code} | 11ms | 42ms | %99.9 |
| GET /urls/list | 52ms | 187ms | %98.6 |

### 5.3 Grafana Dashboard

Prometheus verileri 6 panelli bir Grafana Dashboard üzerinde görselleştirilmektedir (`monitoring/grafana/grafana-dashboard.json`):

| Panel | Sorgu | Açıklama |
|-------|-------|----------|
| 1 | `url_shortener_urls_created_total` | Toplam oluşturulan URL sayısı |
| 2 | `url_shortener_redirects_total` | Toplam yönlendirme sayısı |
| 3 | `url_shortener_active_urls` | Aktif URL gauge |
| 4 | `rate(url_shortener_errors_total[5m])` | Hata oranı (error rate) |
| 5 | `histogram_quantile(0.95, ...)` | p95 istek gecikmesi (latency) |
| 6 | `rate(http_requests_total[1m])` | Saniyedeki istek sayısı (throughput / RPS) |

### 5.4 LocalStack S3 Entegrasyonu

`src/aws_client.py` modülü ile uygulama, URL istatistiklerini periyodik olarak LocalStack üzerinde emüle edilen AWS S3 bucket'ına JSON formatında yüklemektedir. S3 bağlantısı yoksa uygulama graceful olarak S3 özelliklerini devre dışı bırakır ve çalışmaya devam eder.

---

## 6. Sonuç ve Öğrendiklerimiz

### 6.1 Sayısal Özet

| Metrik | Değer |
|--------|-------|
| Toplam kaynak kodu | ~4.500 satır |
| Test fonksiyonu sayısı | 87 (unit + integration + E2E) |
| Postman isteği | 8 |
| Kod kapsamı (coverage) | %90 |
| CI/CD pipeline job sayısı | 7 |
| Grafana panel sayısı | 6 |
| Docker imaj boyutu | ~150 MB |
| k6 p95 gecikmesi | 87 ms |
| Bonus özellik | 4 (+15 puan tavan) |

### 6.2 Karşılaşılan Zorluklar

1. **CI/CD Ortam Farklılıkları:** Lokal ortamda (macOS) sorunsuz çalışan testler, GitHub Actions'daki Ubuntu ortamında `ModuleNotFoundError` verdi. Çözüm olarak `PYTHONPATH=.` ortam değişkeni eklendi ve Python'un proje kökünü tanıması sağlandı.

2. **Testcontainers ve Docker-in-Docker:** GitHub Actions'da Testcontainers ile PostgreSQL konteyneri başlatmak, iç içe Docker (DinD) gerektirdiğinden bazı izin sorunları yaşandı. Service container'lar kullanılarak bu sorun aşıldı.

3. **Playwright Selektor Uyumsuzluğu:** Arayüzde yapılan estetik güncellemeler sonrası HTML element ID'leri değişti, ancak E2E testleri eski selektor isimlerini arıyordu. Bu durum ancak CI/CD hattında yakalandı — yerelde fark edilmemişti. Bu olay, CI/CD pipeline'ının "güvenlik ağı" işlevini çok somut biçimde ortaya koydu.

### 6.3 Öğrenilen Dersler

- **Test piramidinin değeri:** Birim testleri hızlı geri bildirim verirken, entegrasyon ve E2E testleri gerçek dünya senaryolarını yakalıyor. Katmanlar birbirini tamamlıyor.
- **Multi-stage Docker:** İmaj boyutunu %80 küçültmek, hem güvenlik (daha az saldırı yüzeyi) hem de deployment hızı açısından büyük kazanım sağlıyor.
- **Observability üçgeni:** Metrikler (Prometheus), loglar ve trace'ler (Jaeger) bir arada kullanıldığında sorun tespiti dakikalar yerine saniyeler alıyor.

### 6.4 İleride Yapılabilecekler

- **Redis Cache:** Sık erişilen kısa kodlar için önbellek katmanı eklenerek redirect gecikmesi daha da düşürülebilir.
- **PostgreSQL Geçişi:** Yüksek eşzamanlılık gerektiren üretim ortamı için SQLite yerine PostgreSQL kullanılabilir.
- **Rate Limiting:** Kötüye kullanımı önlemek için API'ye istek hız sınırlama mekanizması eklenebilir.
- **Custom Short Code:** Kullanıcının kendi kısa kodunu belirleyebilmesi (vanity URL) özelliği eklenebilir.

---

## 7. İş Paylaşımı

Detaylı iş paylaşımı `docs/work-distribution.md` dosyasında yer almaktadır.

| Modül | Sorumlu |
|-------|---------|
| REST endpoint'ler & DB modelleri | Osman Cingoz (170423029) |
| Docker, K8s, CI/CD pipeline | Talha Ergelen (171423013) |
| Test altyapısı (Pytest, Postman, E2E) | Ortak |
| Monitoring (Prometheus, Grafana) | Ortak |
| Performans testi (k6) | Ortak |
| Dokümantasyon & Rapor | Ortak |

---

## 8. Kaynaklar

1. FastAPI Documentation — https://fastapi.tiangolo.com/
2. Pytest Documentation — https://docs.pytest.org/
3. Playwright for Python — https://playwright.dev/python/
4. k6 Load Testing — https://k6.io/docs/
5. Docker Multi-stage Builds — https://docs.docker.com/build/building/multi-stage/
6. Kubernetes Documentation — https://kubernetes.io/docs/
7. Prometheus Client Python — https://github.com/prometheus/client_python
8. Grafana Documentation — https://grafana.com/docs/
9. LocalStack — https://docs.localstack.cloud/
10. Testcontainers Python — https://testcontainers-python.readthedocs.io/
11. OpenTelemetry Python — https://opentelemetry.io/docs/instrumentation/python/
12. Factory Boy — https://factoryboy.readthedocs.io/
13. Helm — https://helm.sh/docs/
14. KEDA — https://keda.sh/docs/
15. ArgoCD — https://argo-cd.readthedocs.io/

---

*Rapor formatı: Markdown → PDF dönüşümü. Tek sütun düzeni.*  
*Toplam: ~6 sayfa*
