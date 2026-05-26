# ─────────────────────────────────────────────────────────
# Multi-Stage Dockerfile
# ─────────────────────────────────────────────────────────
#
# Multi-stage nedir?
#   Birden fazla "aşama" ile Docker image'ı inşa ederiz.
#   
#   Aşama 1 (builder): Tüm bağımlılıkları kur
#   Aşama 2 (runtime): Sadece çalıştırmak için gereken şeyleri koy
#   
# Neden multi-stage?
#   Tek aşama: Image boyutu ~800MB (gereksiz araçlar dahil)
#   Multi-stage: Image boyutu ~150MB (sadece gerekli şeyler)
#   
#   Daha küçük image = daha hızlı download, daha az güvenlik açığı
#
# ─────────────────────────────────────────────────────────

# ── AŞAMA 1: BUILDER ──────────────────────────────────────
# Bağımlılıkları derle/kur
FROM python:3.11-slim AS builder

# Çalışma dizini
WORKDIR /app

# Bağımlılık dosyasını kopyala (kod değişse bile cache kullanmak için)
COPY requirements.txt .

# pip ile bağımlılıkları kur
# --no-cache-dir: pip cache'ini kaldır (image boyutunu küçültür)
# --user: Sistem Python'una değil, kullanıcı dizinine kur
RUN pip install --no-cache-dir --user -r requirements.txt


# ── AŞAMA 2: RUNTIME ──────────────────────────────────────
# Üretim için hafif ve güvenli image
FROM python:3.11-slim AS runtime

# Güvenlik: Root olmayan kullanıcı oluştur
# Production'da root ile çalışmak güvenlik riski
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Builder aşamasından kurulu Python paketlerini kopyala
COPY --from=builder /root/.local /home/appuser/.local

# Uygulama kodunu kopyala
COPY src/ ./src/
COPY .env .env

# Kullanıcıya geç
USER appuser

# PATH'e kullanıcı Python bin'ini ekle
ENV PATH=/home/appuser/.local/bin:$PATH

# Uygulama portu (belgele — expose ettik ama host'a açmaz)
EXPOSE 8000

# Sağlık kontrolü — Docker bu komutu çalıştırarak container'ın sağlıklı olup olmadığını anlar
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')"

# Başlatma komutu
# uvicorn: FastAPI için ASGI sunucusu
# src.main:app → src/main.py dosyasındaki 'app' değişkeni
# --host 0.0.0.0 → Tüm ağ arayüzlerine dinle (container içinden erişim için)
# --port 8000 → Port numarası
CMD ["python", "-m", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
