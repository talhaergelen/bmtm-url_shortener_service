# SORU-CEVAP HAZIRLIK REHBERİ (Q&A — 3 Dakika)
## Hocanın Sorabileceği TÜM Sorular ve Cevaplar

> Bu doküman, sunumdan SONRA gelen Soru-Cevap bölümü için hazırlanmıştır.
> Hoca rastgele **kod satırı**, **mimari karar** veya **operasyonel senaryo** sorabilir.
> Aşağıdaki sorular gerçek projenizin koduna dayanmaktadır. Cevapları ezberlemeyin, **anlayın**.

---

## BÖLÜM 1 — "Bu Kod Satırı Ne Yapıyor?"

### Soru 1: `shortener.py` dosyasındaki `generate_short_code()` fonksiyonu ne yapıyor?

**Kod (shortener.py, Satır 30-40):**

```python
ALPHABET = string.ascii_letters + string.digits  # 62 karakter (a-z, A-Z, 0-9)
CODE_LENGTH = 6

def generate_short_code() -> str:
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))
```

**Cevap:**
Bu fonksiyon, büyük/küçük harfler ve rakamlardan oluşan 62 karakterlik bir alfabe tanımlıyor. Bu alfabeden rastgele 6 karakter seçerek kısa kod üretiyor. 62 üzeri 6 kuvveti yaklaşık 56 milyar farklı kombinasyon demektir, dolayısıyla çakışma olasılığı son derece düşük.

Önemli nokta: `random.choice()` yerine `secrets.choice()` kullandık. Bunun nedeni; `random` modülü tahmin edilebilir sonuçlar üretebilirken, `secrets` modülü işletim sisteminin kriptografik rasgele sayı üreticisini kullandığından çok daha güvenlidir.

---

### Soru 2: `generate_unique_short_code()` neden döngü kullanıyor?

**Kod (shortener.py, Satır 43-61):**

```python
def generate_unique_short_code(db: Session) -> str:
    while True:
        code = generate_short_code()
        existing = db.query(models.URL).filter(models.URL.short_code == code).first()
        if not existing:
            return code
```

**Cevap:**
Üretilen kod veritabanında zaten kayıtlıysa çakışma (collision) olur ve iki farklı URL aynı kısa koda sahip olurdu. Bu yüzden her üretilen kodu önce veritabanında aratıyoruz. Eğer yoksa kullanıyoruz, varsa yeni bir tane üretiyoruz. 56 milyar ihtimal olduğu için bu döngü pratikte yalnızca bir kere dönecektir.

---

### Soru 3: `main.py`'daki `@app.middleware("http")` ne yapıyor?

**Kod (main.py, Satır 177-199):**

```python
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)
    return response
```

**Cevap:**
Middleware, her HTTP isteği geldiğinde otomatik olarak devreye giren bir katmandır. Sanki bir stoper gibi çalışır: istek geldiğinde zamanı başlatır, yanıt gönderilince durdurur ve geçen süreyi Prometheus'un `REQUEST_DURATION` histogram metriğine kaydeder. Bu sayede Grafana'da p95 latency gibi istatistikleri görebiliyoruz.

---

### Soru 4: `@app.get("/metrics")` neden `@app.get("/{short_code}")`'dan ÖNCE tanımlandı?

**Kod (main.py, Satır 283-299):**

```python
# ⚠️ ÖNEMLI: Bu route /{short_code}'dan ÖNCE tanımlanmalı!
@app.get("/metrics", tags=["Sistem"])
def prometheus_metrics():
    ...

@app.get("/{short_code}", tags=["URL"])  # Catch-all route
def redirect_to_url(short_code: str, ...):
    ...
```

**Cevap:**
FastAPI, URL eşleştirmesini **yukarıdan aşağıya** sırayla yapar. `/{short_code}` bir "catch-all" yani herkesi yakalayan bir route'tur. Eğer `/metrics` route'u bunun altına yazılsaydı, `/metrics` isteği geldiğinde sistem "metrics" kelimesini bir `short_code` olarak yorumlayacak ve veritabanında arayacaktı. `/metrics`'i üste yazarak bu problemi önledik.

---

### Soru 5: `redirect_to_url()` fonksiyonu HTTP 301 mi 302 mi döndürüyor ve neden?

**Kod (main.py, Satır 335):**

```python
return RedirectResponse(url=db_url.original_url, status_code=301)
```

**Cevap:**
**HTTP 301 — Kalıcı Yönlendirme** kullanıyoruz. 301 ile tarayıcı bu yönlendirmeyi önbelleğe (cache) alır; aynı kısa linke tekrar tıklandığında sunucuya tekrar istek atmadan doğrudan gider. Bu hem performans açısından avantajlıdır hem de URL kısaltma servisinin doğasına uygundur çünkü kısa kodlar kalıcıdır, değişmez. 302 geçici yönlendirme olduğu için önbelleğe alınmaz.

---

### Soru 6: `lifespan` fonksiyonu ne zaman çalışır?

**Kod (main.py, Satır 64-92):**

```python
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Başlarken
    models.Base.metadata.create_all(bind=engine)
    ensure_bucket_exists()
    yield  # <-- Uygulama burada çalışır
    # Kapanırken
    logger.info("🛑 Servis kapatılıyor...")
```

**Cevap:**
`lifespan` fonksiyonu uygulama başlarken ve kapanırken bir kez çalışan başlatma ve temizlik kodudur. `yield` keyword'ünden önceki kısım uygulama ayağa kalkarken, sonraki kısım kapanırken çalışır. Burada veritabanı tablolarını oluşturuyor ve S3 bucket'ını hazırlıyoruz. Bu sayede her istekte tekrar tekrar bu işlemleri yapmıyoruz.

---

## BÖLÜM 2 — "Dockerfile'da Neden Multi-Stage Kullandın?"

### Soru 7: Multi-stage build nedir, neden kullandınız?

**Kod (Dockerfile, Satır 1-70):**

```dockerfile
# AŞAMA 1: Bağımlılıkları kur
FROM python:3.11-slim AS builder
RUN pip install --prefix=/install -r requirements.txt

# AŞAMA 2: Sadece çalışmak için gereken şeyler
FROM python:3.11-slim AS runtime
COPY --from=builder /install /usr/local  # builder'dan paketleri al
COPY src/ ./src/
```

**Cevap:**
Multi-stage build'de Docker imajı birden fazla aşamada oluşturulur. İlk aşamada (`builder`) Python paketleri indirilip kurulur. İkinci aşamada (`runtime`) temiz bir Python ortamı başlatılır ve yalnızca çalışmak için gereken dosyalar kopyalanır: pip, derleyiciler, geliştirme araçları gibi gereksiz şeyler son imajda yer almaz.

Sonuç: Tek aşamalı bir imaj 800MB olabilirken, bizim imajımız yalnızca ~150MB'tır. Daha küçük imaj demek daha hızlı indirme, daha az saldırı yüzeyi ve daha az güvenlik açığı demektir.

---

### Soru 8: `USER appuser` satırı neden var?

**Kod (Dockerfile, Satır 36, 53):**

```dockerfile
RUN useradd --create-home --shell /bin/bash appuser
USER appuser
```

**Cevap:**
Güvenlik prensibi olarak konteynerler root kullanıcı olarak çalışmamalıdır. Eğer bir saldırgan konteyner içine girmeyi başarırsa ve konteyner root olarak çalışıyorsa, host sisteme de zarar verebilir. `appuser` gibi kısıtlı yetkili bir kullanıcı oluşturup ona geçmek, bu riski minimize eder. Bu Docker'ın "least privilege" (en az yetki) güvenlik prensibinin uygulamasıdır.

---

### Soru 9: `HEALTHCHECK` satırı ne işe yarar?

**Kod (Dockerfile, Satır 62-63):**

```dockerfile
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"
```

**Cevap:**
Docker'ın yerleşik sağlık kontrol mekanizmasıdır. Her 30 saniyede bir `/health` endpoint'ine istek atarak konteynerin hala çalışıp çalışmadığını kontrol eder. 3 kez üst üste başarısız olursa konteyneri "unhealthy" olarak işaretler. Kubernetes de bu bilgiyi kullanarak sağlıksız pod'ları otomatik olarak yeniden başlatabilir.

---

## BÖLÜM 3 — "Coverage Neden Buradan Düşük?"

### Soru 10: Test coverage neden %100 değil de %90?

**Cevap:**
%100 coverage her zaman doğru hedef değildir. Bizim durumumuzda bazı kod blokları kasıtlı olarak test edilmemiştir:

1. **Hata yönetimi kodları (except blokları):** LocalStack'in olmadığı senaryolardaki `except: pass` blokları gibi kenar durumlar. Bunları test etmek için LocalStack'i bilerek bozulan bir ortamda çalıştırmak gerekir ki bu fazla maliyetlidir.
2. **Startup/shutdown kodu:** `lifespan` fonksiyonunun bazı dalları, entegrasyon testi ortamında farklı davranır.
3. **Güvenli taraf:** %70 şartname minimum'u, %90 ise sağlam bir üretim standardıdır. Kalan %10 kritik iş mantığı değil, hata yollarıdır.

---

## BÖLÜM 4 — "Deploy Çökerse Rollback Nasıl Yapılır?"

### Soru 11: Kubernetes'te rollback nasıl yapılır?

**Cevap:**

Kubernetes'te rollback için birkaç yöntem var:

**Yöntem 1 — Hızlı Rollback (1 komut):**
```bash
kubectl rollout undo deployment/url-shortener
```
Bu komut önceki versiyona anında geri döner. Kubernetes tüm pod'ları eski imajla yeniden başlatır.

**Yöntem 2 — Belirli bir versiyona rollback:**
```bash
kubectl rollout history deployment/url-shortener  # Geçmişi gör
kubectl rollout undo deployment/url-shortener --to-revision=2  # 2. versiyona dön
```

**Biz bunu nasıl fark ederiz?**
Grafana'da hata oranı veya p95 latency anormal artarsa, Prometheus alerting ile anında haberdar olabiliriz. Kubernetes'in readiness probe'u başarısız olan pod'lara trafik yönlendirmeyi zaten durdurur.

---

### Soru 12: CI/CD pipeline'da bir adım başarısız olursa ne olur?

**Cevap:**

GitHub Actions'ta her job `needs:` bağımlılığıyla sıralanmıştır. Bir job başarısız olduğunda bağımlı tüm sonraki joblar otomatik olarak iptal edilir.

Örneğin:
- **Test jobı başarısız olursa** → Docker build, K8s deploy, Smoke test, E2E hepsi iptal edilir. Hatalı kod hiçbir zaman canlıya çıkmaz.
- **Smoke test başarısız olursa** → E2E iptal edilir, bize bildirim gelir.

Bu sayede pipeline bir "kalite kapısı" (quality gate) gibi davranır. Her aşama bir sonrakine ancak başarı durumunda geçer.

---

### Soru 13: Testcontainers nedir, neden kullandınız?

**Cevap:**

Testcontainers, test sırasında Docker konteynerleri ayağa kaldıran bir Python/Java kütüphanesidir. Biz entegrasyon testlerimizde şöyle kullanıyoruz:

```python
# tests/conftest.py
with PostgreSQLContainer("postgres:15") as pg:
    # Test için gerçek PostgreSQL başlat
    engine = create_engine(pg.get_connection_url())
    # Testleri çalıştır
    # Test bitince konteyner otomatik silinir
```

**Neden SQLite değil?**
SQLite, üretim ortamında kullandığımız PostgreSQL ile davranışsal farklar gösterebilir. Örneğin concurrent write (eşzamanlı yazma) lock'ları SQLite'ta farklı çalışır. Testcontainers sayesinde CI ortamında da birebir üretim veritabanıyla test ediyoruz.

---

## BÖLÜM 5 — MİMARİ SAVUNMA SORULARI

### Soru 14: Neden SQLAlchemy ORM kullandınız, direkt SQL yazabilirdiniz?

**Cevap:**

ORM (Object-Relational Mapping) kullanmanın birkaç avantajı var:

1. **Veritabanı bağımsızlığı:** Geliştirmede SQLite, testte ve üretimde PostgreSQL kullanıyoruz. ORM sayesinde sorgu kodu değişmiyor, sadece bağlantı string'i değişiyor.
2. **SQL Injection güvenliği:** ORM parametreleri otomatik olarak escape eder, manuel SQL'de bu riski göz ardı etmek kolaydır.
3. **Hız:** Basit CRUD operasyonları için ORM, raw SQL yazmaktan çok daha hızlıdır.

---

### Soru 15: Prometheus metrikleri nasıl tanımlandı?

**Kod (src/metrics.py):**

```python
from prometheus_client import Counter, Histogram, Gauge

URL_CREATED_TOTAL = Counter(
    "url_shortener_urls_created_total",
    "Toplam oluşturulan URL sayısı"
)

URL_REDIRECTS_TOTAL = Counter(
    "url_shortener_redirects_total",
    "Toplam yönlendirme sayısı",
    labelnames=["short_code"]
)

REQUEST_DURATION = Histogram(
    "http_request_duration_seconds",
    "HTTP istek süresi",
    labelnames=["method", "endpoint"]
)

ACTIVE_URLS_GAUGE = Gauge(
    "url_shortener_active_urls",
    "Şu an aktif URL sayısı"
)
```

**Cevap:**
Prometheus'un 4 temel metrik tipini kullandık:

- **Counter:** Sadece artar, hiç sıfırlanmaz. Toplam URL sayısı ve redirect sayısı için kullandık.
- **Histogram:** Değerlerin dağılımını ölçer. İstek süresi için kullandık; p50, p95, p99 gibi persentil değerleri buradan hesaplanır.
- **Gauge:** Artıp azalabilir. Şu an veritabanındaki aktif URL sayısı için kullandık.

---

### Soru 16: Kubernetes'te "2 replika" neden?

**Cevap:**

Yüksek erişilebilirlik (High Availability) için. Tek bir pod çalışıyorken o pod bir sebepten kapanırsa (güncelleme, hata, donanım arızası) servis tamamen erişilemez hale gelir. 2 replika ile:

1. Bir pod güncelleme alırken diğeri trafik almaya devam eder (Rolling Update).
2. Bir pod çökerse Kubernetes otomatik olarak yenisini başlatır, bu sürede diğer pod hizmet verir.
3. Yük iki pod arasında dağıtılır (Load Balancing).

---

### Soru 17: LocalStack nedir, gerçek AWS'den ne farkı var?

**Cevap:**

LocalStack, AWS servislerini yerel makinede veya CI ortamında simüle eden açık kaynak bir araçtır. Biz S3 (Simple Storage Service) bucket'ı simüle etmek için kullandık.

**Farkı:** LocalStack gerçek AWS'e bağlanmaz, dolayısıyla internet bağlantısı gerekmez ve ücret ödemezsiniz. Endpoint adresi `http://localhost:4566` olur, gerçek AWS'de ise `https://s3.amazonaws.com` olur.

**Neden kullandık?** CI ortamında gerçek AWS kullanmak için credential yönetimi ve maliyet gerekir. LocalStack ile bu yükü ortadan kaldırdık ve testlerimiz tamamen izole, ücretsiz ve hızlı çalıştı.

---

### Soru 18: Jaeger ve OpenTelemetry'nin farkı nedir?

**Cevap:**

- **OpenTelemetry:** Dağıtık izleme için açık standart ve SDK. Hangi backend'e veri göndereceğinizi bilmez, sadece "trace topla" der. Bir enstrümantasyon katmanıdır.
- **Jaeger:** OpenTelemetry'nin topladığı trace verilerini depolayan ve görselleştiren backend'dir. Jaeger UI'da hangi fonksiyonun kaç ms sürdüğünü grafiksel olarak görebilirsiniz.

Yani: `Kod → OpenTelemetry SDK → Jaeger → Jaeger UI`

Biz `tracing.py` dosyasında FastAPI ve SQLAlchemy'yi OpenTelemetry ile instrument ettik; bu sayede her HTTP isteği ve her DB sorgusu otomatik olarak trace oluşturuyor.

---

### Soru 19: "O kısmı takım arkadaşım yaptı" diyebilir misiniz?

**Cevap (Söylenecek Cümle):**

> "Hayır hocam, bu projede kod reviewı birlikte yaptık. Ben şu anda gördüğünüz kodu size açıklayabilirim."

**Sonra şunları söyleyin:**
- main.py'deki endpointleri ben de biliyorum çünkü hep birlikte test ettik.
- CI/CD'nin her adımını ikimiz de takip ettik.
- Sadece kod yazmak değil, birlikte debug ettik, birlikte çalıştırdık.

---

## BÖLÜM 6 — HIZLI BAŞVURU (Son Dakika Özeti)

| Dosya | Ne Yapar | Anahtar Satır |
|---|---|---|
| `main.py` | Tüm API endpoint'leri | Satır 226: `POST /shorten`, Satır 302: redirect |
| `shortener.py` | Kısa kod üretimi | Satır 40: `secrets.choice()` |
| `crud.py` | Veritabanı işlemleri | SQLAlchemy session, ORM sorguları |
| `metrics.py` | Prometheus metrikleri | Counter, Histogram, Gauge |
| `tracing.py` | Jaeger / OpenTelemetry | OTLP exporter, env variable |
| `Dockerfile` | Multi-stage build | Satır 21: builder, Satır 33: runtime |
| `conftest.py` | Test fixture'ları | yield session, in-memory DB |
| `ci.yml` | GitHub Actions | 7 job, sıralı bağımlılıklar |

---

> **SON HATIRLATMA:** "Nasıl yaptınız?" sorusuna cevap verirken her zaman **"Neden bu kararı aldık?"** bağlamını da ekleyin. Hoca sadece kodu değil, mühendislik kararlarınızı değerlendiriyor.
