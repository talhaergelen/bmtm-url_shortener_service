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

WORKDIR /app

COPY requirements.txt .

# /install prefix'e kur — --user yerine prefix kullanmak daha güvenilir
# Çünkü kullanıcı değiştiğinde --user path'i kaybolur
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt


# ── AŞAMA 2: RUNTIME ──────────────────────────────────────
FROM python:3.11-slim AS runtime

# Güvenlik: Root olmayan kullanıcı oluştur
RUN useradd --create-home --shell /bin/bash appuser

WORKDIR /app

# Builder'dan kurulu paketleri sistem Python'una kopyala
COPY --from=builder /install /usr/local

# Uygulama kodunu kopyala
COPY src/ ./src/

# .env varsa kopyala (yoksa build bozulmasın)
COPY requirements.txt .

# Kullanıcıya geç
USER appuser

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

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
