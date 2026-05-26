# URL Shortener Service

**Bulut Mimarilerinde Test Mühendisliği — MTH2526-B25**  
Marmara Üniversitesi, Bilgisayar Mühendisliği Bölümü  
2025–2026 Bahar Yarıyılı — Konu #1: URL Shortener Service

---

## 📋 Proje Açıklaması

Uzun URL'leri kısa kodlara dönüştüren, yönlendirme yapan ve tıklama istatistiklerini takip eden bir mikroservis.

**Özellikler:**
- 🔗 URL kısaltma — `https://uzun-adres.com/...` → `http://localhost:8000/abc123`
- ↪️ Otomatik yönlendirme — Kısa link açıldığında orijinal adrese gider
- 📊 Tıklama istatistikleri — Her kısa link için kaç kez tıklandığı
- 🔍 Swagger UI — `http://localhost:8000/docs` adresinden API belgeleri
- 📈 Prometheus + Grafana — Gerçek zamanlı metrik izleme
- ☁️ LocalStack/S3 — İstatistiklerin buluta kaydedilmesi

---

## 👥 Grup Üyeleri

| İsim | Öğrenci No | Rol |
|------|-----------|-----|
| *İsim giriniz* | *No giriniz* | Tech Lead |
| *İsim giriniz* | *No giriniz* | Backend |
| *İsim giriniz* | *No giriniz* | DevOps |

---

## 🏗️ Mimari

```
┌─────────────┐    ┌──────────────┐    ┌─────────────┐
│  Kullanıcı  │───▶│  FastAPI     │───▶│  SQLite DB  │
│  (Browser)  │    │  (Port 8000) │    │  urls tablosu│
└─────────────┘    └──────┬───────┘    └─────────────┘
                          │
              ┌───────────┼───────────┐
              ▼           ▼           ▼
       ┌──────────┐ ┌──────────┐ ┌──────────┐
       │LocalStack│ │Prometheus│ │ Grafana  │
       │  (S3)    │ │(Port9090)│ │(Port3000)│
       │Port 4566 │ └──────────┘ └──────────┘
       └──────────┘
```

**Bileşenler:**
- `src/main.py` — FastAPI uygulaması, tüm endpoint'ler
- `src/models.py` — Veritabanı tabloları (URL, Click)
- `src/crud.py` — CRUD işlemleri (Create/Read/Update/Delete)
- `src/schemas.py` — Pydantic veri doğrulama şemaları
- `src/shortener.py` — Kısa kod üretme algoritması
- `src/metrics.py` — Prometheus metrik tanımları
- `src/aws_client.py` — LocalStack S3 istemcisi

---

## 🚀 Hızlı Başlangıç

### Yöntem 1: Direkt Python (En Basit)

```bash
# 1. Bağımlılıkları kur
pip install -r requirements.txt

# 2. Uygulamayı çalıştır
python -m uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# 3. Tarayıcıda aç
# http://localhost:8000       → HTML arayüz
# http://localhost:8000/docs  → Swagger API belgeleri
```

### Yöntem 2: Docker Compose (Tam Stack)

```bash
# Tüm servisleri başlat (app + localstack + prometheus + grafana)
docker-compose up -d

# Servis adresleri:
# http://localhost:8000  → Uygulama
# http://localhost:4566  → LocalStack (Sahte AWS)
# http://localhost:9090  → Prometheus
# http://localhost:3000  → Grafana (admin/admin)

# Logları gör
docker-compose logs -f app

# Durdur
docker-compose down
```

### Yöntem 3: Kubernetes (Minikube)

```bash
# Minikube başlat
minikube start

# Docker image'ı Minikube'ye yükle
minikube image build . -t url-shortener:latest

# Kubernetes manifest'leri uygula
kubectl apply -f k8s/

# Servise eriş
minikube service url-shortener-service --url

# Durumu kontrol et
kubectl get pods
kubectl get services
```

---

## 🧪 Testler

### Unit & Integration Testler (Pytest)

```bash
# Tüm testleri çalıştır + coverage raporu
pytest tests/unit/ tests/integration/ \
  --cov=src \
  --cov-report=term-missing \
  -v

# Sadece unit testler
pytest tests/unit/ -v

# Sadece integration testler
pytest tests/integration/ -v

# Coverage %70'in üzerinde mi?
pytest --cov=src --cov-fail-under=70
```

### E2E Testler (Playwright)

```bash
# Playwright kur (ilk seferinde)
pip install pytest-playwright
playwright install chromium

# E2E testleri çalıştır (uygulama çalışırken)
pytest tests/e2e/ -v
```

### Postman / Newman

```bash
# Newman kur (ilk seferinde)
npm install -g newman

# Koleksiyonu çalıştır (uygulama çalışırken)
newman run postman/collection.json \
  --env-var "base_url=http://localhost:8000"
```

### k6 Performans Testi

```bash
# k6 kur: https://k6.io/docs/get-started/installation/

# Performans testini çalıştır (uygulama çalışırken)
k6 run perf/load-test.js

# JSON sonuç dosyasıyla
k6 run perf/load-test.js --out json=perf/results.json
```

---

## 🔌 API Endpoint'leri

| Method | Endpoint | Açıklama |
|--------|----------|---------|
| `GET` | `/health` | Sağlık kontrolü |
| `POST` | `/shorten` | Yeni kısa URL oluştur |
| `GET` | `/{short_code}` | Orijinal URL'ye yönlendir (301) |
| `GET` | `/urls/list` | Tüm kısa URL'leri listele |
| `GET` | `/urls/{short_code}` | URL detayını göster |
| `GET` | `/stats/{short_code}` | Tıklama istatistikleri |
| `DELETE` | `/urls/{short_code}` | URL'yi sil |
| `GET` | `/metrics` | Prometheus metrikleri |

**Örnek İstekler:**

```bash
# URL kısaltma
curl -X POST http://localhost:8000/shorten \
  -H "Content-Type: application/json" \
  -d '{"original_url": "https://google.com"}'

# İstatistik
curl http://localhost:8000/stats/abc123

# URL silme
curl -X DELETE http://localhost:8000/urls/abc123
```

---

## 📁 Proje Yapısı

```
bmtm-url_shortener_service/
├── README.md                    ← Bu dosya
├── LICENSE                      ← MIT Lisansı
├── Dockerfile                   ← Multi-stage Docker image
├── docker-compose.yml           ← Tam geliştirme ortamı
├── requirements.txt             ← Python bağımlılıkları
├── pyproject.toml               ← Proje metadata
├── .env                         ← Ortam değişkenleri
├── src/
│   ├── main.py                  ← FastAPI app + endpoint'ler
│   ├── models.py                ← Veritabanı modelleri
│   ├── crud.py                  ← CRUD işlemleri
│   ├── schemas.py               ← Pydantic şemaları
│   ├── shortener.py             ← Kısaltma algoritması
│   ├── metrics.py               ← Prometheus metrikleri
│   ├── database.py              ← DB bağlantısı
│   ├── config.py                ← Uygulama ayarları
│   ├── aws_client.py            ← S3 istemcisi
│   └── static/
│       └── index.html           ← Web arayüzü (E2E için)
├── tests/
│   ├── conftest.py              ← Pytest fixtures
│   ├── factories.py             ← Factory Boy + Faker
│   ├── unit/
│   │   ├── test_shortener.py    ← Algoritma unit testleri
│   │   └── test_crud.py         ← CRUD unit testleri
│   ├── integration/
│   │   ├── test_api.py          ← API endpoint testleri
│   │   └── test_database.py     ← Testcontainers DB testleri
│   └── e2e/
│       └── test_ui.py           ← Playwright E2E testleri
├── postman/
│   └── collection.json          ← Newman ile çalışan koleksiyon
├── k8s/
│   ├── configmap.yaml           ← Kubernetes ortam ayarları
│   ├── deployment.yaml          ← Pod tanımı (2 replika)
│   └── service.yaml             ← NodePort servisi
├── .github/
│   └── workflows/
│       └── ci.yml               ← GitHub Actions pipeline
├── monitoring/
│   ├── prometheus.yml           ← Prometheus yapılandırması
│   └── grafana/
│       └── grafana-dashboard.json ← Grafana dashboard (6 panel)
├── perf/
│   ├── load-test.js             ← k6 test senaryosu
│   └── report.md                ← Performans sonuçları
└── docs/
    ├── architecture.png         ← Mimari diyagram
    ├── final-report.pdf         ← 6 bölüm akademik rapor
    ├── slides.pdf               ← Sunum slaytları
    └── work-distribution.md     ← Grup iş paylaşımı
```

---

## 🎬 Demo Videosu

> **Video linki:** *[Buraya Drive/YouTube linki eklenecek]*

---

## 📊 Test Coverage

```
Coverage: %70+ (pytest --cov=src --cov-fail-under=70)
```

---

## 📄 Lisans

MIT License — Bkz. [LICENSE](LICENSE)
