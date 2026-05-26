"""
metrics.py — Prometheus Metrikleri

Bu dosya ne işe yarar?
  Uygulamamızın sağlığını ve performansını izlemek için sayaçlar tanımlar.
  Prometheus bu sayaçları okur, Grafana bunları grafiğe döker.

Prometheus nedir?
  Bir izleme (monitoring) sistemi. Uygulamadan düzenli aralıklarla veri toplar.
  "Kaç istek geldi?", "Ortalama yanıt süresi ne?" gibi sorular sorar.

Grafana nedir?
  Prometheus'tan aldığı verileri güzel grafiklerle gösterir.
  Dashboard (gösterge paneli) gibi düşünebilirsin.

Metrik türleri:
  Counter  → Sadece artar (toplam istek sayısı gibi)
  Gauge    → Artar ve azalır (aktif kullanıcı sayısı gibi)
  Histogram → Dağılım ölçer (yanıt süresi dağılımı gibi)
"""

from prometheus_client import Counter, Histogram, Gauge


# ─────────────────────────────────────────────────────────
# SAYAÇLAR (COUNTER) — Sadece artabilir
# ─────────────────────────────────────────────────────────

# Toplam kaç URL kısaltıldı
URL_CREATED_TOTAL = Counter(
    "url_shortener_urls_created_total",
    "Oluşturulan toplam kısa URL sayısı"
)

# Toplam kaç redirect yapıldı
URL_REDIRECTS_TOTAL = Counter(
    "url_shortener_redirects_total",
    "Toplam redirect (yönlendirme) sayısı",
    ["short_code"]  # Hangi kısa koda göre ayrıştır
)

# Başarısız istekler
URL_NOT_FOUND_TOTAL = Counter(
    "url_shortener_not_found_total",
    "Bulunamayan URL isteği sayısı"
)

# ─────────────────────────────────────────────────────────
# HISTOGRAM — Dağılım Ölçer
# ─────────────────────────────────────────────────────────

# API yanıt süreleri (saniye cinsinden)
# Grafana'da p95 latency = %95'lik dilim yanıt süresi
REQUEST_DURATION = Histogram(
    "url_shortener_request_duration_seconds",
    "API istek yanıt süresi (saniye)",
    ["method", "endpoint"],  # GET /shorten gibi etiketler
    buckets=[0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0]
)

# ─────────────────────────────────────────────────────────
# GAUGE — Anlık Değer
# ─────────────────────────────────────────────────────────

# Veritabanındaki toplam URL sayısı
ACTIVE_URLS_GAUGE = Gauge(
    "url_shortener_active_urls",
    "Veritabanındaki toplam aktif URL sayısı"
)
