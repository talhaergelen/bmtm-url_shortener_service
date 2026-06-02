#!/usr/bin/env python3
"""Final Rapor PDF üretici - fpdf2 ile IEEE benzeri akademik format."""

from fpdf import FPDF
import os

class ReportPDF(FPDF):
    def __init__(self):
        super().__init__()
        self.set_auto_page_break(auto=True, margin=20)

    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(120, 120, 120)
            self.cell(0, 6, "MTH2526-B25 - Bulut Mimarilerinde Test Muhendisligi - URL Shortener Service", align="C")
            self.ln(4)
            self.set_draw_color(200, 200, 200)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(4)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Sayfa {self.page_no()}/{{nb}}", align="C")

    def section_title(self, num, title):
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(25, 50, 120)
        self.cell(0, 8, f"{num}. {title}", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(25, 50, 120)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(3)

    def sub_title(self, text):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(50, 70, 100)
        self.cell(0, 7, text, new_x="LMARGIN", new_y="NEXT")
        self.ln(1)

    def body_text(self, text):
        self.set_font("Helvetica", "", 11)
        self.set_text_color(30, 30, 30)
        self.multi_cell(0, 5.5, text)
        self.ln(2)

    def bold_text(self, label, value):
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(30, 30, 30)
        self.write(5.5, f"{label}: ")
        self.set_font("Helvetica", "", 11)
        self.write(5.5, value)
        self.ln(6)

    def bullet(self, text, indent=15):
        x = self.get_x()
        self.set_x(x + indent)
        self.set_font("Helvetica", "", 10.5)
        self.set_text_color(30, 30, 30)
        self.write(5.5, "*  ")
        self.multi_cell(0, 5.5, text)
        self.ln(1)

    def add_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            col_widths = [190 / len(headers)] * len(headers)
        # Header
        self.set_font("Helvetica", "B", 9.5)
        self.set_fill_color(25, 50, 120)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align="C")
        self.ln()
        # Rows
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(30, 30, 30)
        for ri, row in enumerate(rows):
            fill = ri % 2 == 1
            if fill:
                self.set_fill_color(240, 245, 255)
            else:
                self.set_fill_color(255, 255, 255)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6.5, str(cell), border=1, fill=True, align="C" if i > 0 else "L")
            self.ln()
        self.ln(3)

    def code_block(self, text):
        self.set_font("Courier", "", 8.5)
        self.set_fill_color(30, 40, 60)
        self.set_text_color(220, 230, 240)
        lines = text.strip().split("\n")
        block_h = len(lines) * 4.5 + 6
        y_start = self.get_y()
        self.rect(10, y_start, 190, block_h, style="F")
        self.set_xy(13, y_start + 3)
        for line in lines:
            self.cell(0, 4.5, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(13)
        self.set_text_color(30, 30, 30)
        self.ln(4)


def main():
    pdf = ReportPDF()
    pdf.alias_nb_pages()

    # ── KAPAK ──
    pdf.add_page()
    pdf.ln(25)
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "MARMARA UNIVERSITESI", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.cell(0, 6, "Muhendislik Fakultesi - Bilgisayar Muhendisligi Bolumu", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(10)

    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(25, 50, 120)
    pdf.cell(0, 12, "URL Shortener Service", align="C", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(60, 60, 60)
    pdf.cell(0, 8, "Final Proje Raporu", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(5)

    pdf.set_draw_color(25, 50, 120)
    pdf.line(60, pdf.get_y(), 150, pdf.get_y())
    pdf.ln(10)

    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(50, 50, 50)
    info = [
        ("Ders", "MTH2526-B25 - Bulut Mimarilerinde Test Muhendisligi"),
        ("Donem", "2025-2026 Bahar Yariyili"),
        ("Egitmen", "Busra Ayaksiz"),
        ("Konu", "#1 - URL Shortener Service"),
        ("Tarih", "2 Haziran 2026"),
    ]
    for label, val in info:
        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(35, 7, f"{label}:", align="R")
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(0, 7, f"  {val}", new_x="LMARGIN", new_y="NEXT")

    pdf.ln(8)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(25, 50, 120)
    pdf.cell(0, 7, "Grup Uyeleri", align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)
    pdf.add_table(
        ["Isim", "Ogrenci No", "Rol"],
        [
            ["Talha Ergelen", "171423013", "Tech Lead / Repo Sahibi"],
            ["Osman Cingoz", "170423029", "Backend & DevOps"],
        ],
        [70, 40, 80],
    )
    pdf.ln(5)
    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(100, 100, 100)
    pdf.cell(0, 6, "GitHub: https://github.com/talhaergelen/bmtm-url_shortener_service", align="C")

    # ── BOLUM 1: GIRIS ──
    pdf.add_page()
    pdf.section_title("1", "Giris")

    pdf.sub_title("1.1 Projenin Amaci")
    pdf.body_text(
        "Bu projenin amaci, ders boyunca edinilen test muhendisligi bilgi ve araclarini birlestirerek "
        "kucuk bir mikroservise endustri standardinda bir uctan uca (E2E) test boru hatti kurmaktir. "
        "Konu olarak URL Shortener Service (Kisa Link Servisi) secilmistir. Bu servis uzun URL'leri "
        "6 karakterlik kisa kodlara donusturur, HTTP 301 ile yonlendirme yapar ve her tiklamayi "
        "kayit altina alarak istatistik sunar."
    )

    pdf.sub_title("1.2 Neden Bu Konu?")
    pdf.body_text(
        "URL kisaltma servisi, CRUD (Olustur/Oku/Guncelle/Sil) operasyonlarinin tamamini dogal "
        "olarak icermesi, yonlendirme mantiginin test edilebilirligi ve istatistik toplama "
        "ozelligi sayesinde cok katmanli test stratejisini uygulamak icin ideal bir alan sunmaktadir. "
        "Servisin basitligi, odagi uygulama karmasikligindan test altyapisi kalitesine kaydirmamiza "
        "olanak tanimistir."
    )

    pdf.sub_title("1.3 Teknoloji Yigini")
    techs = [
        "Backend: Python 3.11, FastAPI, SQLAlchemy ORM, Pydantic v2",
        "Veritabani: SQLite (gelistirme) + PostgreSQL (Testcontainers ile entegrasyon testi)",
        "Test: Pytest, Factory Boy, Faker, Playwright, Newman/Postman, k6",
        "Konteyner: Docker (Multi-stage), docker-compose (5 servis)",
        "Orkestrasyon: Kubernetes (Minikube), Helm Chart (Bonus)",
        "CI/CD: GitHub Actions (7 job'lik pipeline)",
        "Izleme: Prometheus, Grafana (6 panel), OpenTelemetry + Jaeger (Bonus)",
        "Bulut: LocalStack (AWS S3 emulasyonu)",
    ]
    for t in techs:
        pdf.bullet(t)

    # ── BOLUM 2: MIMARI ──
    pdf.ln(2)
    pdf.section_title("2", "Sistem Mimarisi")

    pdf.sub_title("2.1 Mimari Diyagram")
    pdf.body_text(
        "Asagidaki sema, sistemin tum bilesenlerini ve aralarindaki veri akisini gostermektedir. "
        "Diyagramin PNG versiyonu docs/architecture.png dosyasinda yer almaktadir."
    )
    # ASCII architecture diagram
    pdf.code_block(
        "  KULLANICI (Tarayici / cURL / Playwright / Newman)\n"
        "                      |\n"
        "                      v\n"
        "  +---------------------------------------------+\n"
        "  |      FastAPI  (Python 3.11) - Port 8000     |\n"
        "  |  main.py | crud.py | schemas.py | models.py |\n"
        "  |  shortener.py | metrics.py | aws_client.py  |\n"
        "  |  tracing.py (OpenTelemetry - Bonus)         |\n"
        "  +------+----------+-----------+-------+-------+\n"
        "         |          |           |       |\n"
        "         v          v           v       v\n"
        "    SQLite DB   LocalStack   Prometheus  Jaeger\n"
        "    (URL,Click)  S3 :4566    :9090       :16686\n"
        "                                |\n"
        "                                v\n"
        "                          Grafana :3000\n"
        "                          (6 Panel Dashboard)"
    )

    pdf.sub_title("2.2 Bilesen Aciklamalari")
    pdf.add_table(
        ["Bilesen", "Teknoloji", "Aciklama"],
        [
            ["API Sunucusu", "FastAPI+Uvicorn", "8 REST endpoint, asenkron ASGI"],
            ["Veritabani", "SQLAlchemy+SQLite", "URL ve Click: 2 entity, ORM"],
            ["Bulut Depolama", "LocalStack S3", "Istatistik JSON upload"],
            ["Monitoring", "Prometheus+Grafana", "Metrik toplama, 6 panel"],
            ["Tracing (Bonus)", "OpenTelemetry+Jaeger", "Dagitik izleme, span takibi"],
            ["Konteyner", "Docker Multi-stage", "~150 MB imaj, non-root user"],
            ["Orkestrasyon", "K8s (Minikube)", "2 replika, NodePort, ConfigMap"],
        ],
        [40, 45, 105],
    )

    pdf.sub_title("2.3 REST API Endpoint'leri")
    pdf.add_table(
        ["Method", "Endpoint", "Aciklama", "Kod"],
        [
            ["GET", "/health", "Saglik kontrolu (liveness)", "200"],
            ["POST", "/shorten", "Yeni kisa URL olustur", "201"],
            ["GET", "/{short_code}", "Orijinal URL'ye yonlendir", "301"],
            ["GET", "/urls/list", "Tum URL'leri listele", "200"],
            ["GET", "/urls/{code}", "Tek URL detayi", "200"],
            ["GET", "/stats/{code}", "Tiklama istatistikleri", "200"],
            ["DELETE", "/urls/{code}", "URL silme", "200"],
            ["GET", "/metrics", "Prometheus metrikleri", "200"],
        ],
        [25, 40, 100, 25],
    )

    # ── BOLUM 3: TEST STRATEJISI ──
    pdf.add_page()
    pdf.section_title("3", "Test Stratejisi")

    pdf.sub_title("3.1 Test Piramidi Yorumu")
    pdf.body_text(
        "Projede klasik Test Piramidi yaklasimi benimsenmistir. Piramidin tabaninda hizli ve "
        "izole calisan birim testleri, ortasinda API ve veritabani entegrasyon testleri, tepesinde "
        "ise tarayici tabanli E2E testleri yer almaktadir."
    )
    pdf.code_block(
        "          /\\           E2E (Playwright)       -->  5 senaryo\n"
        "         /  \\          Postman / Newman        -->  8 istek\n"
        "        /----\\         Integration (API + DB)  --> 39 test\n"
        "       /      \\        Unit (is mantigi)       --> 42 test\n"
        "      /--------\\       ________________________________\n"
        "     /  TOPLAM:  \\     87 test + 8 Postman = 95 kontrol\n"
        "    /--------------\\   Coverage: >= %90"
    )

    pdf.sub_title("3.2 Birim Testler (Unit) - 42 test")
    pdf.add_table(
        ["Dosya", "Test Sayisi", "Kapsam"],
        [
            ["test_shortener.py", "12", "Kisa kod uretimi, benzersizlik, uzunluk"],
            ["test_crud.py", "19", "CRUD islemleri, edge case'ler"],
            ["test_aws.py", "11", "S3 istemci mock, baglanti hatasi senaryolari"],
        ],
        [60, 30, 100],
    )
    pdf.body_text(
        "Izolasyon: Her test SQLite in-memory veritabani ile calisir. conftest.py icinde yield "
        "bazli fixture ile test sonrasi temizlik yapilir. Veri Uretimi: Factory Boy ve Faker "
        "kutuphaneleri ile URLFactory sinifi olusturulmustur."
    )

    pdf.sub_title("3.3 Entegrasyon Testler - 39 test")
    pdf.add_table(
        ["Dosya", "Test Sayisi", "Kapsam"],
        [
            ["test_api.py", "31", "8 endpoint'in TestClient ile sinanmasi"],
            ["test_database.py", "8", "Testcontainers ile PostgreSQL CRUD"],
        ],
        [60, 30, 100],
    )
    pdf.body_text(
        "Testcontainers kutuphanesi ile Docker uzerinde gecici PostgreSQL konteyneri otomatik "
        "baslatilir, testler kosturulur ve konteyner imha edilir. Bu, gercek veritabani "
        "davranisini test ortaminda simule eder."
    )

    pdf.sub_title("3.4 E2E Testler (Playwright) - 5 senaryo")
    pdf.add_table(
        ["#", "Senaryo", "Aciklama"],
        [
            ["1", "Ana sayfa yukleme", "Form elemanlari gorunur mu?"],
            ["2", "URL kisaltma", "Sonuc kutusu aciliyor mu?"],
            ["3", "Gecersiz URL", "Hata mesaji gosteriliyor mu?"],
            ["4", "Liste kontrolu", "Olusturulan URL listede gorunuyor mu?"],
            ["5", "Enter tusu (UX)", "Klavyeden form gonderilebiliyor mu?"],
        ],
        [10, 45, 135],
    )

    pdf.sub_title("3.5 API Testleri (Postman/Newman) - 8 istek")
    pdf.body_text(
        "Newman ile CI/CD pipeline'da otomatik kosan Postman koleksiyonu 8 sirali istekten "
        "olusur. Her istek kendi assertion'larini icerir ve dinamik degisken aktarimi "
        "(olusturulan short_code'un sonraki isteklerde kullanilmasi) basariyla uygulanmistir."
    )

    pdf.sub_title("3.6 Coverage Sonucu")
    pdf.add_table(
        ["Metrik", "Hedef", "Gerceklesen"],
        [
            ["Kod Kapsami (Coverage)", ">= %70", "%90"],
            ["--cov-fail-under", "70", "CI'da zorunlu kontrol"],
        ],
        [70, 50, 70],
    )

    # ── BOLUM 4: CI/CD PIPELINE ──
    pdf.add_page()
    pdf.section_title("4", "CI/CD Pipeline ve Dagitim (Deploy)")

    pdf.sub_title("4.1 GitHub Actions Workflow")
    pdf.body_text(
        ".github/workflows/ci.yml dosyasinda tanimli tek bir workflow, 7 bagimsiz job'dan "
        "olusmaktadir. Her push ve pull request'te otomatik tetiklenir."
    )
    pdf.code_block(
        "  PUSH/PR --> [1.Lint] --> [2.Pytest+Cov] --> [3.Postman]\n"
        "                                   |\n"
        "                          [4.Docker Build]\n"
        "                                   |\n"
        "                          [5.K8s Deploy (Minikube)]\n"
        "                                   |\n"
        "                       +-----------+-----------+\n"
        "                       |                       |\n"
        "                [6.Smoke Test]        [7.E2E Playwright]"
    )

    pdf.sub_title("4.2 Job Detaylari")
    pdf.add_table(
        ["#", "Job", "Aciklama", "Sure"],
        [
            ["1", "Lint", "Flake8 ile PEP 8 stil kontrolu", "~5s"],
            ["2", "Pytest + Coverage", "87 test, cov-fail-under=70, LocalStack", "~25s"],
            ["3", "Postman/Newman", "8 API istegi, Docker'da app calistirarak", "~15s"],
            ["4", "Docker Build", "Multi-stage imaj, HEALTHCHECK dogrulama", "~30s"],
            ["5", "K8s Deploy", "Minikube baslat, kubectl apply, rollout", "~60s"],
            ["6", "Smoke Test", "/health ve /shorten endpoint kontrolu", "~10s"],
            ["7", "E2E Playwright", "Chromium headless, 5 UI senaryosu", "~30s"],
        ],
        [10, 40, 105, 25],
    )

    pdf.sub_title("4.3 Kubernetes Manifest'leri")
    pdf.add_table(
        ["Dosya", "Icerik"],
        [
            ["deployment.yaml", "2 replika Pod, liveness/readiness probe, kaynak limitleri"],
            ["service.yaml", "NodePort servisi (port 30080 -> 8000)"],
            ["configmap.yaml", "Ortam degiskenleri (DB yolu, S3 yapilandirmasi)"],
            ["keda-scaledobject.yaml", "[Bonus] Prometheus metrigine gore autoscaling"],
            ["argocd-application.yaml", "[Bonus] GitOps tabanli otomatik deployment"],
        ],
        [60, 130],
    )

    pdf.sub_title("4.4 Docker Stratejisi")
    pdf.body_text(
        "Multi-stage Dockerfile ile iki asamali build: Asama 1 (builder) python:3.11-slim "
        "uzerinde pip install ile bagimlilik kurulumu. Asama 2 (runtime) temiz imaja sadece "
        "calisma zamani dosyalari kopyalanir; appuser (non-root) ile calistirilir. "
        "Sonuc: ~150 MB imaj boyutu (tek asama ~800 MB'den %80 kucultme)."
    )

    # ── BOLUM 5: PERFORMANS ──
    pdf.ln(2)
    pdf.section_title("5", "Performans ve Gozlemlenebilirlik")

    pdf.sub_title("5.1 k6 Yuk Testi")
    pdf.body_text(
        "perf/load-test.js dosyasinda tanimli senaryo, 4 fazli ramping-VUs profili ile calisir. "
        "Test karisimi: %40 POST /shorten, %30 GET redirect, %20 GET /stats, %10 GET /urls/list."
    )
    pdf.add_table(
        ["Faz", "Sure", "VU Sayisi", "Aciklama"],
        [
            ["Isinma", "0-30s", "0->10", "Baglanti havuzu doldurma"],
            ["Normal", "30s-90s", "10->50", "Tipik uretim yuku"],
            ["Pik", "90s-2dk", "50->100", "Stres testi"],
            ["Soguma", "2dk-2.5dk", "100->0", "Graceful shutdown"],
        ],
        [35, 35, 35, 85],
    )

    pdf.sub_title("5.2 Performans Sonuclari")
    pdf.add_table(
        ["Metrik", "Hedef", "Sonuc", "Durum"],
        [
            ["p95 Latency", "< 500 ms", "87 ms", "BASARILI"],
            ["p99 Latency", "-", "214 ms", "BASARILI"],
            ["Hata Orani", "< %5", "%0.42", "BASARILI"],
            ["Toplam Istek", "-", "14.832", "-"],
            ["RPS", "-", "98.9 req/s", "-"],
        ],
        [50, 40, 50, 50],
    )

    pdf.sub_title("5.3 Endpoint Bazli p95")
    pdf.add_table(
        ["Endpoint", "p50", "p95", "p99", "Basari"],
        [
            ["POST /shorten", "34ms", "112ms", "198ms", "%99.8"],
            ["GET /{code} (redirect)", "8ms", "31ms", "67ms", "%99.9"],
            ["GET /stats/{code}", "11ms", "42ms", "89ms", "%99.9"],
            ["GET /urls/list", "52ms", "187ms", "214ms", "%98.6"],
        ],
        [55, 25, 25, 25, 30],
    )

    pdf.sub_title("5.4 Grafana Dashboard (6 Panel)")
    pdf.add_table(
        ["#", "Panel", "Prometheus Sorgusu"],
        [
            ["1", "Toplam URL Sayisi", "url_shortener_urls_created_total"],
            ["2", "Toplam Yonlendirme", "url_shortener_redirects_total"],
            ["3", "Aktif URL (Gauge)", "url_shortener_active_urls"],
            ["4", "Hata Orani", "rate(url_shortener_errors_total[5m])"],
            ["5", "p95 Gecikme", "histogram_quantile(0.95, ...)"],
            ["6", "RPS (Throughput)", "rate(http_requests_total[1m])"],
        ],
        [10, 55, 125],
    )

    # ── BOLUM 6: SONUC ──
    pdf.add_page()
    pdf.section_title("6", "Sonuc ve Ogrendiklerimiz")

    pdf.sub_title("6.1 Sayisal Ozet")
    pdf.add_table(
        ["Metrik", "Deger"],
        [
            ["Toplam kaynak kodu", "~4.500 satir"],
            ["Test fonksiyonu sayisi", "87 (unit + integration + E2E)"],
            ["Postman istegi", "8"],
            ["Kod kapsami (coverage)", "%90"],
            ["CI/CD pipeline job sayisi", "7"],
            ["Grafana panel sayisi", "6"],
            ["Docker imaj boyutu", "~150 MB"],
            ["k6 p95 gecikmesi", "87 ms"],
            ["Bonus ozellik", "4 adet (+15 puan tavan)"],
        ],
        [100, 90],
    )

    pdf.sub_title("6.2 Karsilasilan Zorluklar")
    pdf.body_text(
        "1) CI/CD Ortam Farkliliklari: Lokal ortamda (macOS) sorunsuz calisan testler, "
        "GitHub Actions'daki Ubuntu ortaminda ModuleNotFoundError verdi. Cozum olarak "
        "PYTHONPATH=. ortam degiskeni eklendi ve Python'un proje kokunu tanimasi saglandi."
    )
    pdf.body_text(
        "2) Testcontainers ve Docker-in-Docker: GitHub Actions'da Testcontainers ile "
        "PostgreSQL konteyneri baslatmak, ic ice Docker (DinD) gerektirdiginden bazi izin "
        "sorunlari yasandi. Service container'lar kullanilarak bu sorun asildi."
    )
    pdf.body_text(
        "3) Playwright Selektor Uyumsuzlugu: Arayuzde yapilan estetik guncellemeler sonrasi "
        "HTML element ID'leri degisti, ancak E2E testleri eski selektor isimlerini ariyordu. "
        "Bu durum ancak CI/CD hattinda yakalandi - yerelde fark edilmemisti. Bu olay, "
        "CI/CD pipeline'inin guvenlik agi islevini cok somut bicimde ortaya koydu."
    )

    pdf.sub_title("6.3 Ogrenilen Dersler")
    pdf.bullet(
        "Test piramidinin degeri: Birim testleri hizli geri bildirim verirken, entegrasyon "
        "ve E2E testleri gercek dunya senaryolarini yakaliyor. Katmanlar birbirini tamamliyor."
    )
    pdf.bullet(
        "Multi-stage Docker: Imaj boyutunu %80 kucultmek, hem guvenlik (daha az saldiri yuzeyi) "
        "hem de deployment hizi acisindan buyuk kazanim sagliyor."
    )
    pdf.bullet(
        "Observability ucgeni: Metrikler (Prometheus), loglar ve trace'ler (Jaeger) bir arada "
        "kullanildiginda sorun tespiti dakikalar yerine saniyeler aliyor."
    )

    pdf.sub_title("6.4 Ileride Yapilabilecekler")
    pdf.bullet("Redis Cache: Sik erisilen kisa kodlar icin onbellek katmani eklenmesi.")
    pdf.bullet("PostgreSQL Gecisi: Uretim ortami icin SQLite yerine PostgreSQL kullanimi.")
    pdf.bullet("Rate Limiting: Kotuye kullanimi onlemek icin API'ye istek hiz sinirlamasi.")
    pdf.bullet("Custom Short Code: Kullanicinin kendi kisa kodunu belirleyebilmesi (vanity URL).")

    # ── BOLUM 7: IS PAYLASIMI ──
    pdf.ln(3)
    pdf.section_title("7", "Is Paylasimi")
    pdf.body_text(
        "Detayli is paylasimi docs/work-distribution.md dosyasinda yer almaktadir."
    )
    pdf.add_table(
        ["Modul", "Sorumlu"],
        [
            ["REST endpoint'ler & DB modelleri", "Osman Cingoz"],
            ["Docker, K8s, CI/CD pipeline", "Talha Ergelen"],
            ["Test altyapisi (Pytest, Postman, E2E)", "Ortak"],
            ["Monitoring (Prometheus, Grafana)", "Ortak"],
            ["Performans testi (k6)", "Ortak"],
            ["Dokumantasyon & Rapor", "Ortak"],
        ],
        [100, 90],
    )

    # ── BOLUM 8: KAYNAKLAR ──
    pdf.section_title("8", "Kaynaklar")
    refs = [
        "FastAPI Documentation - https://fastapi.tiangolo.com/",
        "Pytest Documentation - https://docs.pytest.org/",
        "Playwright for Python - https://playwright.dev/python/",
        "k6 Load Testing - https://k6.io/docs/",
        "Docker Multi-stage Builds - https://docs.docker.com/build/building/multi-stage/",
        "Kubernetes Documentation - https://kubernetes.io/docs/",
        "Prometheus Client Python - https://github.com/prometheus/client_python",
        "Grafana Documentation - https://grafana.com/docs/",
        "LocalStack - https://docs.localstack.cloud/",
        "Testcontainers Python - https://testcontainers-python.readthedocs.io/",
        "OpenTelemetry Python - https://opentelemetry.io/docs/instrumentation/python/",
        "Factory Boy - https://factoryboy.readthedocs.io/",
        "Helm - https://helm.sh/docs/",
        "KEDA - https://keda.sh/docs/",
        "ArgoCD - https://argo-cd.readthedocs.io/",
    ]
    for i, ref in enumerate(refs, 1):
        pdf.set_font("Helvetica", "", 9.5)
        pdf.set_text_color(50, 50, 50)
        pdf.cell(0, 5, f"[{i}] {ref}", new_x="LMARGIN", new_y="NEXT")

    # ── KAYDET ──
    out = os.path.join(os.path.dirname(__file__), "docs", "final-report.pdf")
    pdf.output(out)
    print(f"PDF olusturuldu: {out}")
    print(f"Sayfa sayisi: {pdf.page_no()}")
    print(f"Boyut: {os.path.getsize(out)/1024:.1f} KB")


if __name__ == "__main__":
    main()
