# CANLI DEMO KONUŞMA METNİ (7 Dakika)
## Slayt sunumundan SONRA başlar

> Ekranında yan yana açık olacaklar:
> - **Sol yarı:** Terminal (VS Code veya iTerm)
> - **Sağ yarı:** Tarayıcı (localhost:8000 Admin Dashboard + GitHub sekmesi)
> 
> Tarayıcıda hazır açık sekmeler:
> 1. localhost:8000 (Arayüz — Ana Sayfa)
> 2. github.com/talhaergelen/bmtm-url_shortener_service (Actions sekmesi)
> 3. localhost:3000 (Grafana)
> 4. localhost:16686 (Jaeger)

---

## ADIM 1 — ARAYÜZDEN URL KISALT + PR AÇ + CI TETİKLE (0:00 – 2:00)

**[Tarayıcıda localhost:8000 Ana Sayfa açık]**

Hocam önce sistemimizin çalıştığını göstereyim. Gördüğünüz gibi Admin Dashboard'umuz ayakta. Üst kısımda anlık istatistiklerimiz var: Toplam URL sayısı, toplam tıklanma ve servis durumu "Sağlıklı" olarak görünüyor.

**[URL KISALT kutusuna `https://marmara.edu.tr` yaz ve "Kısalt" butonuna bas]**

Şimdi canlı olarak bir URL kısaltıyorum. Marmara Üniversitesi'nin adresini yapıştırıp "Kısalt" butonuna basıyorum. Gördüğünüz gibi sistem bize 6 haneli benzersiz bir kısa kod üretti ve alt taraftaki tabloya düştü.

**[Tablodaki kısa koda tıkla, yeni sekmede marmara.edu.tr açılsın]**

Kısa linkimize tıklıyorum. Gördüğünüz gibi bizi anında Marmara Üniversitesi sitesine yönlendirdi. Bu bir 301 Redirect, yani kalıcı yönlendirmedir.

**[Arayüz sekmesine geri dön, "Yenile" butonuna bas]**

Arayüze geri dönüp yenilediğimde bakın tıklanma sayısı 1 arttı. Sistem her tıklamayı veritabanına kaydedip anlık olarak arayüze yansıtıyor.

**[Terminale geç]**

Şimdi CI/CD pipeline'ımızı tetiklemek için bir Pull Request açıyorum. Terminalde yeni bir dal oluşturuyorum:

```bash
git checkout -b demo/live-feature
echo "demo canli degisikligi eklendi" >> README.md
git add README.md
git commit -m "docs: canli demo güncellemesi"
git push origin demo/live-feature
```

**[Tarayıcıda GitHub sekmesine geç]**

GitHub'a gidiyorum. Bakın yeşil "Compare & pull request" butonu çıktı. Buna tıklıyorum ve PR'ımı açıyorum.

**[Create pull request butonuna bas]**

PR açıldığı an bakın alt kısımda sarı çarklar dönmeye başladı. GitHub Actions pipeline'ımız otomatik olarak tetiklendi. Lint, Test, Newman, Docker Build aşamaları sırayla koşmaya başlıyor.

---

## ADIM 2 — PR MERGE + CD TETİKLEME (2:00 – 3:00)

**[GitHub PR sayfasında kal]**

Pipeline'ın tamamlanmasını beklerken size akışı anlatayım. Şu an ilk adım olan Lint çalışıyor, flake8 ile PEP-8 uyumluluğu kontrol ediliyor. Ardından Pytest koşacak ve coverage kontrolü yapılacak. Sonra Newman API testleri ve Docker multi-stage build gelecek.

**[Eğer pipeline yeşile döndüyse "Merge pull request" butonuna bas. Dönmediyse aşağıdaki cümleyi söyle:]**

Pipeline devam ediyor ama ben size akışını göstermek için Actions sekmesine geçeyim.

**[Actions sekmesine tıkla, en üstteki workflow'u aç]**

Bakın burada 7 aşamamızı görüyorsunuz: Lint, Test, API Check, Docker Build, K8s Deploy, Smoke Test ve E2E UI. Her biri başarıyla tamamlandığında yeşil tik alıyor. Bu pipeline her push ve pull request'te otomatik tetikleniyor.

---

## ADIM 3 — MİNİKUBE DEPLOYMENT KONTROLÜ (3:00 – 4:00)

**[Terminale geç]**

Kubernetes tarafında deployment durumunu kontrol edelim:

```
kubectl get pods
```

Bakın hocam, url-shortener pod'larımız "Running" durumunda. 2 replika çalışıyor, yani yüksek erişilebilirlik sağlanmış.

```
kubectl get svc
```

Service'imiz de aktif ve ClusterIP üzerinden erişilebilir durumda.

**[Arayüzde Servisler sayfasına geç]**

Arayüzümüzün "Servisler" sayfasından da tüm bileşenlerin durumunu görebiliyoruz. Bakın: FastAPI App, Prometheus, Grafana, LocalStack S3, Jaeger UI — hepsi "Çalışıyor" durumunda. Yani tüm altyapımız sağlıklı.

---

## ADIM 4 — GRAFANA METRİKLERİ (4:00 – 5:00)

**[Tarayıcıda Grafana sekmesine (localhost:3000) geç]**

Şimdi Grafana dashboard'umuza bakalım. Prometheus metrikleri buraya akıyor. 6 adet panelimiz var:

Üst sırada Toplam URL Sayısı — bakın az önce oluşturduğumuz URL burada sayıya yansıdı. Yanında Toplam Redirect Sayısı — az önce tıkladığımız yönlendirme burada. Aktif URL'ler ve Hata Oranı panellerimiz de var.

Alt sırada ise p95 Latency ve RPS yani saniyedeki istek sayısı grafikleri var. Bu paneller sayesinde sistemi sadece "çalışıyor mu?" diye değil, "ne kadar iyi çalışıyor?" diye de izleyebiliyoruz.

**[Arayüzde Metrikler sayfasına geç]**

Kendi dashboard'umuzdan da aynı verilere bakabiliriz. Burada Prometheus'un topladığı ham metrikleri ve servis sağlık durumunu anlık olarak görüyorsunuz. Status: healthy, uptime bilgisi ve uygulama metrikleri listelenmiş durumda.

---

## ADIM 5 — k6 YÜK TESTİ (5:00 – 6:00)

**[Terminale geç]**

Şimdi sistemimizin yük altında nasıl davrandığını gösterelim. k6 aracıyla küçük bir load test koşuyorum:

```
k6 run perf/load-test.js
```

**[Test koşarken konuş:]**

Bakın şu an sanal kullanıcılar oluşturuluyor ve sisteme eşzamanlı istekler atılıyor. Ekranda yeşil çizgilerle akan her satır başarılı bir HTTP isteğini temsil ediyor.

**[Test bittiğinde sonuç ekranını göster:]**

Test tamamlandı. Sonuçlara bakarsak: p95 latency değerimiz — bakın burada — 87 milisaniye civarında çıktı. Hedefimiz 500 milisaniyenin altıydı, bunu rahat rahat geçtik. Hata oranı da %1'in altında, yani sistem yük altında bile stabil kaldı.

**[Hemen Grafana sekmesine geç]**

Grafana'ya dönersek bakın az önce koştuğumuz yük testinin etkisini panellerde görebiliyoruz. RPS grafiği yükseldi, latency panelinde de trafik altındaki davranışımız gözüküyor.

---

## ADIM 6 — PLAYWRIGHT E2E TESTİ (6:00 – 7:00)

**[Terminale geç]**

Son olarak uçtan uca testimizi canlı koşalım. Playwright ile tarayıcının otomatik açılmasını sağlıyorum:

```bash
PYTHONPATH=. pytest tests/e2e/test_ui.py::TestE2EUrlShortener::test_url_shortening_creates_result --headed --no-cov --timeout=30
```

**[Ellerini klavyeden çek ve ekranı izle]**

Bakın hocam, şu an hiçbir şeye dokunmuyorum. Playwright kendi kendine bir Chromium tarayıcısı açtı, localhost:8000 adresimize gitti, URL kısaltma kutusuna otomatik olarak bir adres yazdı, "Kısalt" butonuna bastı ve sonucun tabloya düştüğünü doğruladı. Tüm bunları bir robot yaptı, ben hiçbir yere tıklamadım.

**[Terminalde yeşil PASSED yazısını göster]**

Ve terminalde gördüğünüz gibi test PASSED, yani başarıyla geçti. Bu, gerçek bir kullanıcının yapacağı akışın otomatik olarak doğrulandığı anlamına geliyor. Her deployment'tan sonra bu testler otomatik koşarak regresyon olmadığını garanti ediyor.

---

## KAPANIŞ (7:00)

**[Arayüzde Ana Sayfa'ya dön]**

Özetlersek hocam: Az önce canlı olarak URL kısalttık, tıklayıp yönlendirmeyi gördük, GitHub'a PR açıp CI/CD pipeline'ını tetikledik, Kubernetes üzerinde pod'ların çalıştığını doğruladık, Grafana'da metrikleri izledik, k6 ile yük testi koşup performansı ölçtük ve son olarak Playwright ile tarayıcıyı robotla test ettik.

Tüm bu süreçler, yani test, build, deploy ve izleme tamamen otomatize edilmiş durumda. Sorularınızı bekliyoruz.

---

## ⚠️ YEDEK PLAN (Bir şey bozulursa)

Eğer demo sırasında herhangi bir sorun çıkarsa (internet koparsa, Docker çökerse, port çakışırsa) şu cümleyi söyle:

> "Hocam şu an lokal ortamda bir port çakışması/bağlantı sorunu yaşıyorum ama bu senaryoların hepsini daha önce test edip kaydetmiştim. GitHub Actions'taki başarılı pipeline kayıtlarından ve raporlarımızdan gösterebilirim."

Sonra GitHub Actions sekmesine geçip daha önceki başarılı bir workflow'u aç ve yeşil tikleri göster.

---

## 🎯 DEMO ÖNCESİ KONTROL LİSTESİ

Sunumdan 10 dakika önce şunları yap:
- [ ] `docker-compose up -d` ile tüm servisleri başlat
- [ ] Tarayıcıda localhost:8000 açılıyor mu? Kontrol et
- [ ] Tarayıcıda localhost:3000 (Grafana) açılıyor mu?
- [ ] Tarayıcıda localhost:16686 (Jaeger) açılıyor mu?
- [ ] Terminal açık mı? Proje klasöründe misin?
- [ ] GitHub reposu tarayıcıda açık mı?
- [ ] `git checkout main && git pull` yaptın mı?
- [ ] Eski demo branch'ini sil: `git branch -D demo/live-feature && git push origin --delete demo/live-feature`
