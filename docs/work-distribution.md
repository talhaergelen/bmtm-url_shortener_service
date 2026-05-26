# İş Paylaşımı — URL Shortener Service

**Marmara Üniversitesi — Bulut Mimarilerinde Test Mühendisliği**  
**Konu #1: URL Shortener Service**

---

## Üyeler

| İsim | Öğrenci No | Rol |
|------|-----------|-----|
| *[İsim 1]* | *[No]* | Tech Lead, Repo Sahibi |
| *[İsim 2]* | *[No]* | Backend & Veritabanı |
| *[İsim 3]* | *[No]* | DevOps & CI/CD |

> **Not:** Bu tabloyu gerçek isimler ve öğrenci numaralarıyla doldurun.

---

## Modül Sorumluluğu

| Modül | Sorumlu | Yardımcı |
|-----------------------------|---------|----------|
| FastAPI endpoint'leri (main.py) | İsim 2 | İsim 1 |
| Veritabanı modelleri (models.py) | İsim 2 | İsim 3 |
| CRUD işlemleri (crud.py) | İsim 2 | İsim 1 |
| Kısaltma algoritması (shortener.py) | İsim 1 | — |
| Prometheus metrikleri (metrics.py) | İsim 1 | İsim 3 |
| AWS/LocalStack istemcisi (aws_client.py) | İsim 3 | İsim 1 |
| Dockerfile (multi-stage) | İsim 3 | İsim 2 |
| docker-compose.yml | İsim 3 | İsim 1 |
| Kubernetes manifestleri (k8s/) | İsim 3 | — |
| GitHub Actions CI/CD (.github/) | İsim 3 | İsim 1 |
| Grafana dashboard | İsim 1 | İsim 3 |
| Unit testler (tests/unit/) | İsim 2 | İsim 1 |
| Integration testler (tests/integration/) | İsim 1 | İsim 2 |
| E2E testler (tests/e2e/) | İsim 2 | İsim 1 |
| Postman koleksiyonu | İsim 1 | İsim 2 |
| k6 performans testleri (perf/) | İsim 1 | — |
| HTML arayüzü (src/static/) | İsim 2 | — |
| Final rapor (docs/final-report.pdf) | İsim 1 | İsim 2 + 3 |
| Sunum slaytları | İsim 3 | İsim 1 |

---

## Sunum Sorumluluğu (20 dakika slot)

| Süre | Bölüm | Sorumlu |
|------|-------|---------|
| 0–3 dk | Problem & Mimari | İsim 1 |
| 3–7 dk | Test Stratejisi & Pipeline | İsim 2 |
| 7–14 dk | Canlı Demo (PR → CI → Deploy → Metrik → E2E) | İsim 3 |
| 14–17 dk | Sayılar & Performans Sonuçları | İsim 1 |
| 17–20 dk | Q&A | Hep birlikte |

---

## Commit İstatistikleri

> Bu bölümü sunum öncesi aşağıdaki komutla doldurun:
```bash
git shortlog -sn --all
```

| Üye | Commit Sayısı |
|-----|--------------|
| *İsim 1* | *--* |
| *İsim 2* | *--* |
| *İsim 3* | *--* |

---

## Haftalık Çalışma Özeti

| Hafta | Yapılan İşler |
|-------|--------------|
| Hafta 1 | Proje planlaması, FastAPI kurulumu, temel endpoint'ler |
| Hafta 2 | Veritabanı modelleri, CRUD, Pytest unit testleri |
| Hafta 3 | Docker, Kubernetes, GitHub Actions |
| Hafta 4 | E2E testler, k6 performans, Grafana dashboard, rapor |
