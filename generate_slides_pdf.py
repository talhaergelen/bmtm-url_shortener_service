#!/usr/bin/env python3
"""Sunum Slaytlari PDF uretici."""

from fpdf import FPDF
import os

class SlidesPDF(FPDF):
    def __init__(self):
        super().__init__(orientation="L", format="A4")  # Landscape
        self.set_auto_page_break(auto=False)
        self.slide_num = 0

    def new_slide(self, title, subtitle=None):
        self.slide_num += 1
        self.add_page()
        # Background
        self.set_fill_color(15, 23, 42)
        self.rect(0, 0, 297, 210, "F")
        # Title bar
        self.set_fill_color(30, 64, 175)
        self.rect(0, 0, 297, 35, "F")
        self.set_font("Helvetica", "B", 22)
        self.set_text_color(255, 255, 255)
        self.set_xy(15, 8)
        self.cell(0, 12, title)
        if subtitle:
            self.set_font("Helvetica", "", 11)
            self.set_text_color(180, 200, 255)
            self.set_xy(15, 22)
            self.cell(0, 8, subtitle)
        # Slide number
        self.set_font("Helvetica", "", 9)
        self.set_text_color(100, 120, 180)
        self.set_xy(270, 195)
        self.cell(0, 8, f"{self.slide_num}/10")
        # Reset position
        self.set_xy(15, 42)
        self.set_text_color(220, 230, 245)

    def slide_text(self, text, size=13):
        self.set_font("Helvetica", "", size)
        self.set_text_color(200, 210, 230)
        self.multi_cell(267, 7, text)
        self.ln(3)

    def slide_bullet(self, text, size=12):
        self.set_font("Helvetica", "", size)
        self.set_text_color(200, 210, 230)
        x = self.get_x()
        self.set_x(x + 8)
        # bullet dot
        self.set_fill_color(99, 102, 241)
        self.ellipse(x + 8, self.get_y() + 2, 3, 3, "F")
        self.set_x(x + 15)
        self.multi_cell(250, 6.5, text)
        self.ln(2)

    def slide_bold(self, label, value, size=12):
        self.set_font("Helvetica", "B", size)
        self.set_text_color(129, 140, 248)
        self.write(7, f"{label}: ")
        self.set_font("Helvetica", "", size)
        self.set_text_color(200, 210, 230)
        self.write(7, value)
        self.ln(8)

    def slide_table(self, headers, rows, col_widths=None):
        if col_widths is None:
            total = 267
            col_widths = [total / len(headers)] * len(headers)
        x_start = self.get_x()
        # Header
        self.set_font("Helvetica", "B", 10)
        self.set_fill_color(30, 64, 175)
        self.set_text_color(255, 255, 255)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=0, fill=True, align="C")
        self.ln()
        # Rows
        self.set_font("Helvetica", "", 10)
        for ri, row in enumerate(rows):
            if ri % 2 == 0:
                self.set_fill_color(30, 41, 59)
            else:
                self.set_fill_color(20, 30, 48)
            self.set_text_color(200, 210, 230)
            self.set_x(x_start)
            for i, cell in enumerate(row):
                self.cell(col_widths[i], 6.5, str(cell), border=0, fill=True,
                          align="C" if i > 0 else "L")
            self.ln()
        self.ln(3)

    def slide_code(self, text):
        self.set_font("Courier", "", 9)
        self.set_fill_color(10, 15, 30)
        self.set_text_color(56, 189, 248)
        lines = text.strip().split("\n")
        h = len(lines) * 5 + 6
        y = self.get_y()
        self.rect(15, y, 267, h, "F")
        self.set_xy(18, y + 3)
        for line in lines:
            self.cell(0, 5, line, new_x="LMARGIN", new_y="NEXT")
            self.set_x(18)
        self.set_text_color(200, 210, 230)
        self.ln(4)


def main():
    pdf = SlidesPDF()

    # SLIDE 1: KAPAK
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, 297, 210, "F")
    # Accent bar
    pdf.set_fill_color(30, 64, 175)
    pdf.rect(0, 70, 297, 4, "F")
    pdf.set_fill_color(99, 102, 241)
    pdf.rect(0, 74, 297, 2, "F")

    pdf.set_font("Helvetica", "B", 32)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 30)
    pdf.cell(297, 15, "URL Shortener Service", align="C")

    pdf.set_font("Helvetica", "", 16)
    pdf.set_text_color(148, 163, 184)
    pdf.set_xy(0, 48)
    pdf.cell(297, 10, "Bulut Mimarilerinde Test Muhendisligi - Donem Projesi", align="C")

    pdf.set_xy(0, 85)
    pdf.set_font("Helvetica", "", 13)
    pdf.set_text_color(200, 210, 230)
    pdf.cell(297, 8, "MTH2526-B25 | 2025-2026 Bahar Yariyili", align="C")

    pdf.set_xy(0, 100)
    pdf.cell(297, 8, "Egitmen: Busra Ayaksiz", align="C")

    pdf.set_xy(0, 120)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(129, 140, 248)
    pdf.cell(297, 8, "Talha Ergelen (171423013)  |  Osman Cingoz (170423029)", align="C")

    pdf.set_xy(0, 140)
    pdf.set_font("Helvetica", "", 11)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(297, 8, "github.com/talhaergelen/bmtm-url_shortener_service", align="C")

    pdf.set_xy(0, 160)
    pdf.set_text_color(71, 85, 105)
    pdf.cell(297, 8, "Haziran 2026", align="C")

    # SLIDE 2: Problem & Cozum
    pdf.new_slide("Problem ve Cozum", "Neden URL Shortener? Neden test pipeline?")
    pdf.slide_bold("Problem", "Uzun ve karmasik URL'lerin paylasim zorlugu, tiklama verisinin takip edilememesi")
    pdf.slide_bold("Cozum", "Mikroservis tabanli, bulut teknolojileri ile izlenebilir bir link kisaltma servisi")
    pdf.ln(3)
    pdf.slide_bullet("Uzun URL'yi http://host/abc123 formuna cevirme")
    pdf.slide_bullet("HTTP 301 yonlendirme ve tiklama analizi")
    pdf.slide_bullet("8 REST API endpoint, Swagger Docs ve HTML UI")
    pdf.slide_bullet("Docker, Kubernetes, Prometheus, Grafana entegrasyonu")
    pdf.slide_bullet("LocalStack S3 ile bulut depolama simulasyonu")
    pdf.slide_bullet("OpenTelemetry + Jaeger ile dagitik izleme (Bonus)")

    # SLIDE 3: Mimari
    pdf.new_slide("Mimari Diyagram", "Tum bilesenler tek sayfada")
    pdf.slide_code(
        "  KULLANICI (Tarayici / cURL / Playwright / Newman)\n"
        "                      |\n"
        "                      v\n"
        "  +---------------------------------------------+\n"
        "  |      FastAPI  (Python 3.11) - Port 8000      |\n"
        "  |  main.py | crud.py | schemas.py | models.py  |\n"
        "  |  shortener.py | metrics.py | aws_client.py   |\n"
        "  |  tracing.py (OpenTelemetry - Bonus)          |\n"
        "  +------+----------+-----------+-------+--------+\n"
        "         |          |           |       |\n"
        "         v          v           v       v\n"
        "    SQLite DB   LocalStack   Prometheus  Jaeger\n"
        "    (URL,Click)  S3 :4566    :9090       :16686\n"
        "                                |\n"
        "                                v\n"
        "                          Grafana :3000 (6 Panel)"
    )
    pdf.slide_table(
        ["Bilesen", "Teknoloji", "Detay"],
        [
            ["API Sunucu", "FastAPI + Uvicorn", "8 endpoint, ASGI"],
            ["Veritabani", "SQLAlchemy + SQLite", "2 entity (URL, Click)"],
            ["Bulut", "LocalStack S3", "Istatistik JSON upload"],
            ["Monitor", "Prometheus + Grafana", "6 panelli dashboard"],
            ["Tracing", "OpenTelemetry + Jaeger", "Dagitik izleme (Bonus)"],
        ],
        [45, 60, 162],
    )

    # SLIDE 4: Test Stratejisi
    pdf.new_slide("Test Stratejisi", "Test piramidi yorumu, katman bazli test sayilari")
    pdf.slide_code(
        "          /\\           E2E (Playwright)       -->  5 senaryo\n"
        "         /  \\          Postman / Newman        -->  8 istek\n"
        "        /----\\         Integration (API + DB)  --> 39 test\n"
        "       /      \\        Unit (is mantigi)       --> 42 test\n"
        "      /--------\\       ________________________________\n"
        "     /  TOPLAM:  \\     87 test + 8 Postman = 95 kontrol\n"
        "    /--------------\\   Coverage: >= %90"
    )
    pdf.slide_table(
        ["Katman", "Arac", "Sayi", "Detay"],
        [
            ["Unit", "Pytest, Factory Boy", "42", "shortener, crud, aws testleri"],
            ["Integration", "TestClient, Testcontainers", "39", "API + PostgreSQL"],
            ["E2E", "Playwright (headless)", "5", "UI senaryolari"],
            ["API", "Postman / Newman", "8", "Dinamik degisken aktarimi"],
            ["Performans", "k6", "1", "100 VU, 4 fazli ramping"],
        ],
        [40, 65, 20, 142],
    )

    # SLIDE 5: CI/CD
    pdf.new_slide("CI/CD Pipeline", "GitHub Actions - 7 job, tek workflow")
    pdf.slide_code(
        "  PUSH/PR --> [1.Lint] --> [2.Pytest+Cov] --> [3.Postman]\n"
        "                                   |\n"
        "                          [4.Docker Build (multi-stage)]\n"
        "                                   |\n"
        "                          [5.K8s Deploy (Minikube)]\n"
        "                                   |\n"
        "                       +-----------+-----------+\n"
        "                       |                       |\n"
        "                [6.Smoke Test]        [7.E2E Playwright]"
    )
    pdf.slide_table(
        ["#", "Job", "Icerik", "Sure"],
        [
            ["1", "Lint", "Flake8 PEP8 kontrolu", "~5s"],
            ["2", "Test", "Pytest + cov-fail-under=70", "~25s"],
            ["3", "Postman", "Newman 8 API istegi", "~15s"],
            ["4", "Docker", "Multi-stage + Healthcheck", "~30s"],
            ["5", "K8s", "Minikube deploy + rollout", "~60s"],
            ["6", "Smoke", "/health + /shorten kontrolu", "~10s"],
            ["7", "E2E", "Playwright 5 senaryo", "~30s"],
        ],
        [15, 35, 155, 30],
    )

    # SLIDE 6: Performans
    pdf.new_slide("Performans Testi (k6)", "100 esanlamli kullanici, 4 fazli yuk profili")
    pdf.slide_table(
        ["Metrik", "Hedef", "Sonuc", "Durum"],
        [
            ["p95 Latency", "< 500 ms", "87 ms", "BASARILI"],
            ["p99 Latency", "-", "214 ms", "BASARILI"],
            ["Hata Orani", "< %5", "%0.42", "BASARILI"],
            ["Toplam Istek", "-", "14.832", "-"],
            ["RPS", "-", "98.9 req/s", "-"],
        ],
        [70, 60, 70, 67],
    )
    pdf.ln(2)
    pdf.slide_table(
        ["Endpoint", "p50", "p95", "p99", "Basari"],
        [
            ["POST /shorten", "34ms", "112ms", "198ms", "%99.8"],
            ["GET /{code} redirect", "8ms", "31ms", "67ms", "%99.9"],
            ["GET /stats/{code}", "11ms", "42ms", "89ms", "%99.9"],
            ["GET /urls/list", "52ms", "187ms", "214ms", "%98.6"],
        ],
        [75, 40, 40, 40, 40],
    )

    # SLIDE 7: Monitoring
    pdf.new_slide("Monitoring ve Observability", "Prometheus + Grafana + Jaeger + LocalStack S3")
    pdf.slide_table(
        ["#", "Grafana Panel", "Prometheus Sorgusu"],
        [
            ["1", "Toplam URL Sayisi", "url_shortener_urls_created_total"],
            ["2", "Toplam Yonlendirme", "url_shortener_redirects_total"],
            ["3", "Aktif URL (Gauge)", "url_shortener_active_urls"],
            ["4", "Hata Orani (Error Rate)", "rate(url_shortener_errors_total[5m])"],
            ["5", "p95 Gecikme (Latency)", "histogram_quantile(0.95, ...)"],
            ["6", "RPS (Throughput)", "rate(http_requests_total[1m])"],
        ],
        [15, 75, 177],
    )
    pdf.ln(3)
    pdf.slide_bullet("Prometheus: Her 15 saniyede metrik toplama (scrape)")
    pdf.slide_bullet("Grafana: 6 panel ile gercek zamanli goruntuleme (localhost:3000)")
    pdf.slide_bullet("LocalStack S3: Istatistik JSON dosyalarinin bulut depolamaya yuklenmesi")
    pdf.slide_bullet("OpenTelemetry + Jaeger: Dagitik izleme, span bazli istek takibi (Bonus)")

    # SLIDE 8: Sayilar
    pdf.new_slide("Sayilarla Proje Ozeti", "Tum metrikler tek bakista")
    pdf.slide_table(
        ["Metrik", "Deger"],
        [
            ["Kaynak kodu", "~4.500 satir"],
            ["Test sayisi", "87 fonksiyon + 8 Postman"],
            ["Coverage", "%90"],
            ["CI/CD job", "7"],
            ["Grafana panel", "6"],
            ["Docker imaj", "~150 MB"],
            ["k6 p95", "87 ms"],
        ],
        [130, 137],
    )
    pdf.ln(2)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(129, 140, 248)
    pdf.cell(0, 8, "Bonus Ozellikler (+15 puan tavan):")
    pdf.ln(10)
    pdf.slide_bullet("Helm Chart paketleme (+5)")
    pdf.slide_bullet("KEDA event-driven autoscaling (+5)")
    pdf.slide_bullet("ArgoCD GitOps (+5)")
    pdf.slide_bullet("OpenTelemetry distributed tracing (+5)")

    # SLIDE 9: Zorluklar
    pdf.new_slide("Zorluklar ve Ogrendiklerimiz", "3 temel zorluk ve 3 onemli ders")
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(248, 113, 113)
    pdf.cell(0, 8, "Karsilasilan Zorluklar:")
    pdf.ln(10)
    pdf.slide_bullet("CI/CD ortam farkliliklari: ModuleNotFoundError -> PYTHONPATH cozumu")
    pdf.slide_bullet("Testcontainers Docker-in-Docker izin sorunlari -> Service container")
    pdf.slide_bullet("Playwright selektor uyumsuzlugu: UI degisikligi sonrasi ID degisimi")
    pdf.ln(5)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(52, 211, 153)
    pdf.cell(0, 8, "Ogrenilen Dersler:")
    pdf.ln(10)
    pdf.slide_bullet("Test piramidi katmanlari birbirini tamamliyor")
    pdf.slide_bullet("Multi-stage Docker ile %80 imaj kucultme = guvenlik + hiz")
    pdf.slide_bullet("Observability ucgeni: Metrik + Log + Trace = hizli hata tespiti")

    # SLIDE 10: Q&A
    pdf.add_page()
    pdf.set_fill_color(15, 23, 42)
    pdf.rect(0, 0, 297, 210, "F")
    pdf.set_fill_color(30, 64, 175)
    pdf.rect(0, 80, 297, 4, "F")
    pdf.set_fill_color(99, 102, 241)
    pdf.rect(0, 84, 297, 2, "F")

    pdf.set_font("Helvetica", "B", 36)
    pdf.set_text_color(255, 255, 255)
    pdf.set_xy(0, 40)
    pdf.cell(297, 20, "Tesekkurler!", align="C")

    pdf.set_font("Helvetica", "", 18)
    pdf.set_text_color(148, 163, 184)
    pdf.set_xy(0, 65)
    pdf.cell(297, 10, "Canli Demo'ya gecis yapiyoruz.", align="C")

    pdf.set_xy(0, 100)
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(129, 140, 248)
    pdf.cell(297, 10, "Sorulariniz?", align="C")

    pdf.set_xy(0, 130)
    pdf.set_font("Helvetica", "", 12)
    pdf.set_text_color(100, 116, 139)
    pdf.cell(297, 8, "GitHub: github.com/talhaergelen/bmtm-url_shortener_service", align="C")

    # Save
    out = os.path.join(os.path.dirname(__file__), "docs", "slides.pdf")
    pdf.output(out)
    print(f"Slides PDF: {out}")
    print(f"Sayfa: {pdf.page_no()}")
    print(f"Boyut: {os.path.getsize(out)/1024:.1f} KB")


if __name__ == "__main__":
    main()
