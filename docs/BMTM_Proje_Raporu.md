# Bulut Mimari ve Test Mühendisliği Dönem Projesi Raporu
## URL Shortener Service (BMTM)

**Geliştirici:** Osman Cingöz
**Proje Adı:** Bulut Tabanlı URL Kısaltma ve Yönlendirme Servisi
**Versiyon:** 1.0.0

---

## 1. Proje Özeti ve Amacı
Bu proje, bulut mimarileri ve test mühendisliği (BMTM) prensiplerini temel alarak geliştirilmiş, yüksek erişilebilirliğe (high-availability) sahip bir URL Kısaltma servisidir. Sistemin amacı sadece uzun URL'leri kısaltmak değil; bu sürecin etrafında güvenilir, test edilebilir, izlenebilir ve ölçeklenebilir bir mikroservis altyapısı kurmaktır.

## 2. Kullanılan Teknolojiler ve Mimari

Uygulama modern Python ve Bulut Bilişim araçları etrafında şekillendirilmiştir:
*   **Web Çerçevesi:** FastAPI (Asenkron, yüksek performanslı ve dahili Swagger UI desteği)
*   **Veritabanı:** SQLite (Geliştirme) ve PostgreSQL (Testcontainers ile CI/CD ortamında entegrasyon)
*   **ORM:** SQLAlchemy 2.0 (Modern ve type-safe veritabanı işlemleri)
*   **Bulut Simülasyonu:** LocalStack (AWS S3 entegrasyonu simülasyonu)
*   **Konteynerleştirme:** Docker & Docker Compose
*   **Orkestrasyon:** Kubernetes (Minikube üzerinden K8s Deployment, Service, ConfigMap)
*   **CI/CD Pipeline:** GitHub Actions

## 3. Test Mühendisliği Süreçleri

Projenin en kritik bileşenlerinden biri olan Test Mühendisliği standartları eksiksiz uygulanmıştır. **Test Kapsamı (Coverage) %90** seviyesindedir (Şartname minimumu: %70).

### 3.1. Birim (Unit) Testleri
Sistemin iş mantığını izole bir şekilde test etmek amacıyla yazılmıştır. 
*   **URL Doğrulama:** `http://`, `https://`, localhost gibi formatların geçerliliği test edilmiştir.
*   **Kod Üretimi:** Üretilen kısa kodların tam 6 karakter olduğu, sadece alfanümerik karakterler barındırdığı ve rastgelelik (unique) özelliği test edilmiştir.
*   **Crud İşlemleri:** Veritabanına yazma, silme ve tıklama sayısı artırma işlemleri test edilmiştir.

### 3.2. Entegrasyon (Integration) Testleri
Bileşenlerin birbiriyle olan iletişimi test edilmiştir.
*   **API Entegrasyon Testleri:** `/shorten`, `/urls/list`, `/stats/{short_code}` uç noktaları uçtan uca HTTP istekleriyle (TestClient) test edilmiştir.
*   **Veritabanı Entegrasyonu (Testcontainers):** GitHub Actions üzerinde veya lokalde Docker aracılığıyla geçici bir **PostgreSQL** ayağa kaldırılarak gerçek veritabanı davranışları (Cascade Delete, Unique Constraint) doğrulanmıştır.

### 3.3. Test Verisi Üretimi (Factory Boy & Faker)
Testlerin veriye bağımlılığını azaltmak ve dinamik testler koşturabilmek için **Factory Boy** kütüphanesi kullanılmıştır. Her test koşumunda Faker aracılığıyla rastgele URL'ler ve istatistik verileri üretilmektedir.

### 3.4. E2E (Playwright) UI Testleri
Kullanıcının tarayıcı üzerinden yaşadığı deneyimi simüle etmek amacıyla Playwright entegre edilmiştir.
*   Arayüzün yüklenmesi, butonlara tıklanması ve URL sonuçlarının ekrana gelmesi Chromium üzerinde otomatik test edilmektedir.

## 4. Gözlemlenebilirlik (Observability) ve Monitoring

Bulut tabanlı bir sistemin "kör" olmaması için 3 temel ayak (Logs, Metrics, Traces) projeye entegre edilmiştir.

### 4.1. Metrikler (Prometheus & Grafana)
*   Sistemde Prometheus istemcisi aracılığıyla özel metrikler (`http_requests_total`, `http_request_duration_seconds`) toplanmaktadır.
*   `/metrics` endpoint'i üzerinden dışarı açılan bu veriler **Grafana** dashboard'una bağlanmış ve anlık CPU, RAM ve İstek sayısı görselleştirilmiştir.

### 4.2. Dağıtık İzleme (Distributed Tracing - Jaeger)
*   **OpenTelemetry** kullanılarak sisteme Jaeger entegre edilmiştir.
*   Bir kullanıcının API'ye attığı isteklerin veritabanı seviyesine (SQLAlchemy sorgularına) kadar ne kadar sürede çalıştığı Jaeger UI (`localhost:16686`) üzerinden şelale (waterfall) grafikleriyle izlenebilmektedir.

## 5. Devops ve CI/CD Pipeline Süreçleri

Proje için **GitHub Actions** üzerinde otomatik çalışan 7 aşamalı devasa bir CI/CD zinciri kurulmuştur. Geliştirici ana dallara kod gönderdiğinde şu adımlar sırasıyla işletilir:

1.  **Lint:** `flake8` ile Python PEP8 standartlarına uyum kontrolü.
2.  **Test:** `pytest` çalıştırılır ve coverage'ın %70 üzerinde olduğu doğrulanır. (PostgreSQL Testcontainers dahil)
3.  **Postman / Newman:** Uygulama ayağa kaldırılarak Newman CLI aracıyla Postman API koleksiyonları koşturulur.
4.  **Docker Build:** Proje `url-shortener:latest` olarak build edilir ve commit SHA ile etiketlenir.
5.  **K8s Deploy:** `minikube` ortamına Kubernetes manifestleri (ConfigMap, Deployment, Service) uygulanır.
6.  **Smoke Test:** Canlıya alınan uygulamanın çalışıp çalışmadığını doğrulamak için kritik endpoint'lere Bash üzerinden `curl` istekleri atılır.
7.  **E2E UI Test:** Playwright testleri koşturularak arayüz sağlığı doğrulanır.

## 6. S3 Bulut Entegrasyonu (LocalStack)
Servisin bazı statik verileri (veya gelecekte eklenecek kullanıcı dosyalarını) bulutta depolaması senaryosunu simüle etmek amacıyla projede **LocalStack** kullanılmıştır.
Uygulama açılırken `boto3` kullanarak AWS S3'e (LocalStack üzerindeki sahte S3'e) bağlanır ve bir `url-shortener-stats` bucket'ı oluşturur. 

## 7. Sonuç
Proje; kod kalitesi, test mühendisliği yaklaşımları (Testcontainers, Factory Boy, Playwright), CI/CD otomasyonu, Kubernetes dağıtımı ve detaylı monitoring (Prometheus, Jaeger) altyapısıyla güncel sektör standartlarında, tam teşekküllü bir bulut mimarisi örneği olarak başarıyla tamamlanmıştır.
