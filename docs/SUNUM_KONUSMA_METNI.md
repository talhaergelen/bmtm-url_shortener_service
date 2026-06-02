# SUNUM KONUŞMA METNİ
## Cloud-Native URL Shortener Service — 10 Dakika

> Bu metin, sunumda her slaytta ne söyleyeceğini kelimesi kelimesine içerir.  
> Ekranından veya telefonundan okuyabilirsin. Parantez içindeki notlar sana yönergedir, sesli okuma.

---

## SLAYT 1 — KAPAK (0:00 – 0:30)
**[Ekranda: URL Shortener Service başlığı, isimler, kurum bilgisi]**

Hocam merhabalar. Ben Osman Çingöz, takım arkadaşım Talha Ergelen. Marmara Üniversitesi Bilgisayar Mühendisliği Bölümü, 2025-2026 Bahar Yarıyılı, MTH2526 kodlu Bulut Mimarilerinde Test Mühendisliği dersinin dönem projesi olarak URL Shortener Service isimli projemizi sunacağız. Danışmanımız Büşra Ayaksız hocamızdır.

---

## SLAYT 2 — PROBLEM & ÇÖZÜM (0:30 – 2:00)
**[Ekranda: Sol tarafta "Domain Problemi", sağ tarafta "Mühendislik Çözümü"]**

Bu slaytta projemizin temel motivasyonunu görüyorsunuz. Sol taraftaki kutudan başlarsak; domain problemimiz aslında basit: Uzun ve karmaşık URL'lerin paylaşım zorluğu var. Bunun yanında, bir linke kaç kişinin ne zaman tıkladığını yani tıklama verisini ve trafik istatistiklerini takip edemiyoruz.

Sağ taraftaki kutuya geçersek, bizim mühendislik çözümümüzün odak noktası, uygulamanın kendisinden ziyade, onun etrafını saran test, dağıtım ve izleme altyapısıdır. Yani biz bu projede bir link kısaltma servisi yaptık ama asıl hedefimiz bu servisi bir bahane olarak kullanıp arkasında endüstri standardında bir mühendislik altyapısı kurmaktı.

Bulut uyumluluğu açısından mikroservis mimarisine uygun şekilde Docker ve Kubernetes'e tam entegrasyon sağladık. Otomasyon tarafında, uçtan uca yani E2E seviyesinde otomatik bir test boru hattı kurduk. Observability yani gözlemlenebilirlik tarafında ise Prometheus, Grafana ve Jaeger ile gerçek zamanlı metrikler ve dağıtık izleme entegrasyonunu tamamladık.

---

## SLAYT 3 — SİSTEM MİMARİSİ (2:00 – 3:30)
**[Ekranda: 4 katmanlı mimari diyagram + sağda src/ klasör yapısı]**

Mimarimizi katmanlı bir yapıda tasarladık. En altta çekirdek katmanımız var: FastAPI framework'ü, SQLAlchemy ORM'i ve veritabanı olarak geliştirme ortamında SQLite, test ve üretim ortamlarında ise PostgreSQL kullanıyoruz.

Bir üst katmanda konteyner katmanımız yer alıyor. Uygulamayı Docker ile paketliyoruz ve Kubernetes, yani Minikube üzerinde 2 replika pod olarak çalıştırıyoruz. Liveness ve readiness probe'ları ile podların sağlığını kontrol ediyoruz.

Bulut katmanında ise AWS S3 simülasyonu için LocalStack kullanıyoruz. İstatistik verilerini JSON formatında S3 bucket'ına yedekliyoruz.

En üst katman gözlemlenebilirlik katmanıdır. Prometheus metrikleri toplar, Grafana bunları panellerde görselleştirir, OpenTelemetry ve Jaeger ise dağıtık izleme sağlar.

Sağ tarafta da kaynak kod yapımızı görüyorsunuz. Her dosyanın tek bir sorumluluğu var: main.py giriş noktası ve endpoint tanımları, crud.py veritabanı işlemleri, shortener.py kısa kod üretim algoritması, metrics.py Prometheus metrikleri, tracing.py Jaeger entegrasyonu ve aws_client.py LocalStack bağlantısı.

---

## SLAYT 4 — TEST STRATEJİSİ (3:30 – 5:00)
**[Ekranda: Sol tarafta test piramidi, sağda %90+ coverage göstergesi]**

Test stratejimizde endüstri standardı olan Test Piramidi yaklaşımını uyguladık. Piramidi aşağıdan yukarıya doğru anlatıyorum:

En altta, piramidin tabanında Unit Testlerimiz var. 20'den fazla test fonksiyonuyla Pytest, Factory Boy ve Faker kütüphanelerini kullanarak iş mantığını izole bir şekilde test ediyoruz. Kısa kod üretim algoritması ve CRUD fonksiyonları burada doğrulanıyor.

Bir üst katmanda Entegrasyon Testleri yer alıyor. Burada API, CRUD ve veritabanı katmanları birlikte test ediliyor. Testcontainers sayesinde her test koşumunda izole bir PostgreSQL konteyneri ayağa kaldırılıyor ve gerçek veritabanı davranışı doğrulanıyor.

API katmanında Postman ve Newman ile 8 adet API isteği koşuyoruz. Dinamik değişkenlerle URL oluşturma, yönlendirme ve silme gibi senaryolar test ediliyor.

Ve piramidin en tepesinde E2E testlerimiz var. 5 adet Playwright senaryosuyla gerçek bir Chromium tarayıcısı açılıyor, kullanıcı gibi form dolduruluyor, buton tıklanıyor ve sonuçlar doğrulanıyor.

Sağ taraftaki göstergede gördüğünüz gibi şartnamede minimum %70 coverage istenirken, biz %90'ın üzerine çıktık. Bu da yazdığımız kodun neredeyse tamamının test tarafından kapsandığı anlamına geliyor.

---

## SLAYT 5 — CI/CD PIPELINE (5:00 – 6:30)
**[Ekranda: 7 aşamalı pipeline akış şeması, yeşil tikler]**

Sürekli entegrasyon ve dağıtım hattımız GitHub Actions üzerinde çalışıyor. Her push ve her pull request'te bu 7 aşamalı pipeline otomatik olarak tetikleniyor. Soldan sağa doğru anlatıyorum:

Birinci adım Lint. Flake8 ile PEP-8 kod standartlarına uyum kontrolü yapılıyor. Kodun okunabilirliği ve tutarlılığı burada garanti altına alınıyor.

İkinci adım Test. Pytest ile tüm birim ve entegrasyon testleri izolasyonlu veritabanı üzerinde koşuyor. Coverage %70'in altına düşerse pipeline bilerek hata veriyor.

Üçüncü adım API Check. Newman ile Postman koleksiyonundaki 8 API isteği sırayla koşuluyor.

Dördüncü adım Docker Build. Multi-stage build ile yaklaşık 150 megabaytlık optimize edilmiş bir imaj üretiliyor ve SHA etiketiyle işaretleniyor.

Beşinci adım Kubernetes Deploy. Minikube üzerine ConfigMap, Deployment ve Service manifestleri uygulanıyor ve rollout status bekleniyor.

Altıncı adım Smoke Test. Canlıya çıkan uygulamanın /health endpoint'ine istek atılarak sistemin sağlıklı yanıt verdiği doğrulanıyor.

Yedinci ve son adım E2E UI testi. Playwright headless modda çalışarak kullanıcı arayüzünün canlı ortamda sorunsuz çalıştığını kanıtlıyor.

---

## SLAYT 6 — PERFORMANS VE YÜK TESTİ (6:30 – 7:30)
**[Ekranda: p95 = 87ms göstergesi, hata oranı, RPS, endpoint dağılım tablosu]**

Performans testlerimizi k6 aracıyla yaptık. 100 maksimum sanal kullanıcı ile 4 aşamalı bir yük profili oluşturduk.

Sol taraftaki büyük göstergede p95 latency değerimizi görüyorsunuz: 87 milisaniye. Yani isteklerin yüzde 95'i 87 milisaniyenin altında yanıt aldı. Hedefimiz 500 milisaniyeydi, bunu rahat rahat geçtik.

Hata oranımız %0.42 seviyesinde kaldı ki bu, hedefimiz olan %5'in çok altında. Saniyede ortalama 98.9 istek işledik ve toplamda yaklaşık 15.000 istek attık.

Sağ alttaki tabloda kritik endpoint dağılımını görüyorsunuz. Redirect endpoint'imiz, yani kısa linke tıklandığında yapılan yönlendirme, p50'de 8 milisaniye, p95'te 31 milisaniye ile en hızlı endpoint'imiz. URL kısaltma işlemi p95'te 112 milisaniye ve URL listeleme p95'te 187 milisaniye sürdü.

---

## SLAYT 7 — MONİTORİNG & TRACİNG (7:30 – 8:30)
**[Ekranda: 6 Grafana panel grafiği + Jaeger trace diyagramı + S3 entegrasyonu]**

Gözlemlenebilirlik katmanımıza bakalım. Üst bölümde Prometheus ve Grafana entegrasyonumuzu görüyorsunuz. 6 adet panel kurguladık: Aktif URL Sayısı, Saniyedeki İstek yani RPS, 404 Hata Oranı, p50, p95 ve p99 Latency değerleri, CPU Kullanımı ve RAM Kullanımı.

Prometheus, FastAPI uygulamasındaki /metrics endpoint'ini her 15 saniyede bir okuyarak http_requests_total ve http_request_duration_seconds gibi özel metrikleri topluyor. Grafana da bu ham verileri görsel panellere dönüştürüyor.

Alt sol tarafta Dağıtık İzleme, yani Jaeger ve OpenTelemetry entegrasyonumuzu görüyorsunuz. Örneğin bir /shorten isteği geldiğinde toplam 80 milisaniye sürdüğünü, bunun 30 milisaniyesinin validasyon, 45 milisaniyesinin ise PostgreSQL sorgusunda harcandığını adım adım izleyebiliyoruz.

Alt sağda ise S3 Bulut Entegrasyonu var. LocalStack üzerinden url-shortener-stats isimli bir bucket'a JSON formatında istatistik yedekleme yapıyoruz.

---

## SLAYT 8 — SAYILAR VE BONUS (8:30 – 9:15)
**[Ekranda: Sol tarafta 4 kutu (30+ test, %90+ coverage, 87ms, %0.42), sağda bonus listesi]**

Projenin sayısal özetine bakarsak: 30'dan fazla test fonksiyonumuz var. Unit, Integration, API ve E2E olmak üzere tüm katmanlar kapsanıyor. Kod kapsamımız %90'ın üzerinde. p95 latency 87 milisaniye ve hata oranı %0.42 seviyesinde.

Sağ tarafta ileri seviye kazanımlarımız, yani bonus özelliklerimiz yer alıyor. Dört tane bonus tamamladık:

Birincisi Helm Chart: Kubernetes paketleme ve tek komutla yönetim. İkincisi KEDA Autoscaling: Prometheus metriklerine göre event-driven ölçekleme. Üçüncüsü ArgoCD GitOps: Git push tabanlı sürekli dağıtım. Dördüncüsü OpenTelemetry: Jaeger ile mikroservis bazlı dağıtık izleme.

Alt kısımdaki yeşil bant ise rubrik uyum durumunu gösteriyor: Tüm zorunlu ve asgari gereksinimler başarıyla tamamlanmıştır.

---

## SLAYT 9 — ZORLUKLAR VE ÇÖZÜMLER (9:15 – 9:50)
**[Ekranda: 3 zorluk-çözüm kutusu (kırmızı → yeşil)]**

Proje boyunca karşılaştığımız 3 önemli zorluk ve çözümlerini görüyorsunuz.

Birincisi Test İzolasyonu problemi. Pytest koşumlarında eski verilerin yeni testleri bozması, yani veri kirlenmesi yaşadık. Bunu conftest.py içerisinde yield bazlı oturumlar kurarak ve her test için in-memory veritabanını sıfırlayarak çözdük.

İkincisi Platform Bağımsızlık sorunu. Windows ortamında C++ Build Tools eksikliği sebebiyle Pydantic ve Psycopg2 gibi kütüphanelerde derleme hataları aldık. Bunu Docker Multi-stage build uygulayarak her ortamda tutarlı, optimize edilmiş bir Linux ortamı sağlayarak çözdük.

Üçüncüsü Eşzamanlı Yük, yani Concurrency problemi. k6 ile 100 sanal kullanıcı yük altındayken SQLite'ın write lock limitlerine takıldık. CI/CD ortamına Testcontainers ile PostgreSQL entegre ederek üretim ortamı için gerçek bir ilişkisel veritabanı yönetim sistemi gereksinimini kanıtladık.

---

## SLAYT 10 — CANLI DEMO & SORU-CEVAP (9:50 – 10:00)
**[Ekranda: Terminal ekranı, demo adımları listesi]**

Sunumun slayt kısmı bu kadardı. Ekranda gördüğünüz gibi altyapımız ayağa kaldırıldı ve log akışı aktif. Sistem soru-cevap için hazırdır.

Dilerseniz şimdi canlı demo aşamasına geçebiliriz. PR açışı ve CI tetikleme, Kubernetes deployment kontrolü, Grafana dashboard canlı izleme, k6 ile yük testi ve p95 latency doğrulaması, ve Playwright E2E senaryo koşumu yapabiliriz.

Teşekkür ederiz, sorularınızı bekliyoruz.

---

> **NOT:** Toplam süre yaklaşık 10 dakikadır.  
> Prova yaparken kronometreyle ölç. Hızlı gidersen 8-9 dk sürer, yavaş okursan 11 dk'yı bulabilir.
> En az 3 kere prova et!
