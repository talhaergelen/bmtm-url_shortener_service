# URL Shortener Service — 10 Dakikalık Sunum Notları

Bu notlar slaytların üstüne koymak için değil, sunumda konuşurken destek almak için hazırlandı.

## Slayt 1 — Problem & Çözüm

Merhaba hocam, dönem projesi olarak URL Shortener Service geliştirdik. Bu servis uzun URL'leri kısa linklere dönüştürüyor, kısa linke tıklandığında kullanıcıyı orijinal adrese yönlendiriyor ve her linkin tıklanma sayısını takip ediyor.

Bu projedeki ana hedefimiz karmaşık bir ürün geliştirmek değil, küçük bir mikroservisin etrafına ders kapsamında öğrendiğimiz test ve bulut mühendisliği altyapısını kurmaktı. Bu yüzden uygulamayı FastAPI ile sade tuttuk; asıl emeği test, CI/CD, Docker, Kubernetes, monitoring ve performans tarafında gösterdik.

## Slayt 2 — Mimari Diyagram

Mimaride kullanıcı tarafında tarayıcı, Swagger, Postman ve otomatik testler var. Bunların hepsi FastAPI uygulamasına istek gönderiyor. API endpoint'leri `main.py` içinde, veritabanı işlemleri `crud.py` içinde, veri modelleri `models.py` içinde tutuluyor.

Veritabanı tarafında iki entity var: `URL` ve `Click`. `URL` kısa kodu, orijinal adresi ve toplam tıklama sayısını tutuyor. `Click` ise her tıklamayı ayrı kayıt olarak saklıyor. LocalStack S3 ile istatistikleri yerel AWS ortamına yazıyoruz. Prometheus metrikleri topluyor, Grafana gösteriyor, Jaeger ise tracing tarafını sağlıyor.

## Slayt 3 — Test Stratejisi

Test stratejisinde test piramidi yaklaşımını kullandık. En altta hızlı çalışan unit testler var. Bunlar kısa kod üretme algoritmasını ve CRUD fonksiyonlarını test ediyor.

Orta katmanda integration testler var. Burada API, CRUD ve veritabanı zincirinin birlikte çalışmasını kontrol ediyoruz. Testcontainers ile gerçek PostgreSQL container'ı başlatıp veritabanı davranışını ayrıca doğruladık.

Üst katmanda ise Playwright ile E2E testler var. Bunlar gerçek tarayıcı gibi ana sayfayı açıyor, URL giriyor, butona basıyor, sonuç kutusunu ve listeyi kontrol ediyor. Ayrıca Postman/Newman koleksiyonu CI içinde API akışını test ediyor.

## Slayt 4 — CI/CD Pipeline

GitHub Actions workflow tek dosyada tanımlı. Pipeline önce lint çalıştırıyor, sonra Pytest ve coverage kontrolü yapıyor. Daha sonra Newman ile Postman API testleri koşuyor. Ardından Docker image build ediliyor.

Docker image başarılı oluşturulunca Minikube üzerinde Kubernetes deployment yapılıyor. ConfigMap, Deployment ve Service manifestleri uygulanıyor. Rollout tamamlandıktan sonra smoke test çalışıyor. Smoke testte `/health`, `/shorten`, `/stats`, `/urls/list` ve delete akışı kontrol ediliyor. En sonda Playwright E2E testleri çalışıyor.

## Slayt 5 — Monitoring & Observability

Bu slaytta Grafana dashboard ekran görüntüsünü göstereceğiz. Prometheus uygulamadaki `/metrics` endpoint'ini 15 saniyede bir scrape ediyor. Uygulamada toplam oluşturulan URL sayısı, redirect sayısı, aktif URL sayısı, hata sayısı ve request duration histogramı gibi metrikler var.

Grafana bu metrikleri panele dönüştürüyor. Böylece sistem sadece çalışıyor mu diye değil, ne kadar hızlı çalışıyor, hata oranı nedir, yoğunluk artınca nasıl davranıyor gibi sorulara da cevap verebiliyoruz. Ek olarak OpenTelemetry ve Jaeger ile trace takibi bonus olarak eklendi.

## Slayt 6 — Sayılar

Projede 87 Pytest test fonksiyonu ve 8 Postman isteği var. Coverage hedefi şartnamede en az yüzde 70'ti; biz yaklaşık yüzde 90 seviyesine çıktık.

Performans testi k6 ile yapıldı. Yük profili 100 sanal kullanıcıya kadar çıkıyor. Sonuçlarda p95 latency 87 ms çıktı, yani 500 ms hedefinin oldukça altında. Hata oranı yüzde 0.42 seviyesinde kaldı. CI/CD tarafında 7 job'lık pipeline var.

## Slayt 7 — Öğrendiklerim & Zorluklar

En önemli öğrendiğimiz şey testlerin sonradan eklenen bir kontrol değil, mimarinin parçası olarak düşünülmesi gerektiği oldu.

Zorluklardan biri lokal ortam ile CI ortamının farklı davranmasıydı. Bunu environment variable'lar, `PYTHONPATH` ayarları ve fixture izolasyonu ile çözdük. Bir diğer zorluk Testcontainers'ın Docker'a bağımlı olmasıydı. Ayrıca arayüz değiştikçe Playwright selector'larının kırılabileceğini gördük, bu yüzden UI elemanlarına daha stabil id'ler verdik.

Sonuç olarak bu proje bize sadece FastAPI uygulaması yazmayı değil; test piramidi, otomatik pipeline, container ortamı, Kubernetes deployment ve observability zincirini birlikte kurmayı öğretti.

## Ekran Görüntüsü Yerleri

1. Slayt 5'te büyük turuncu placeholder var: buraya Grafana dashboard ekran görüntüsünü koy.
2. Slayt 4'te sağ alanda isteğe bağlı GitHub Actions başarılı workflow ekran görüntüsü için alan var. Koymak zorunlu değil ama iyi görünür.

## Demo Sırası

1. `http://localhost:8000` arayüzünü aç.
2. Ana sayfada geçerli bir URL kısalt.
3. Oluşan kısa URL'yi göster.
4. `Aç` butonuyla redirect mantığını göster.
5. URL Yönetimi sekmesinde listenin güncellendiğini göster.
6. Metrikler sekmesinde canlı metrikleri göster.
7. Servisler sekmesinden Swagger veya `/metrics` linkini aç.
8. Eğer Docker Compose stack açıksa Grafana'ya geçip dashboard'u göster.
