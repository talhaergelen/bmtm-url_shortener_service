"""
main.py — FastAPI Ana Uygulama

Bu dosya ne işe yarar?
  TÜM API endpoint'lerini (URL'leri) tanımlar.
  Bu dosya uygulamanın "kalbi"dir.

FastAPI nedir?
  Python ile hızlı web API'leri yazmak için framework (çerçeve).
  Sen Python fonksiyonu yazarsın, o bunu web API'sine dönüştürür.

API nedir?
  Application Programming Interface — Programlar arası iletişim protokolü.
  Kullanıcı (veya başka bir program) bize HTTP isteği gönderir,
  biz JSON formatında yanıt veririz.

Endpoint nedir?
  API'nin belirli bir URL adresi.
  Örnek: POST /shorten → "Bana bir URL kısalt"
         GET /abc123  → "abc123 kodlu URL'ye yönlendir"

HTTP Metodları:
  GET    → Veri al (okuma)
  POST   → Yeni veri oluştur
  DELETE → Veri sil
  PUT    → Veri güncelle
"""

import os as _os
import time
import logging
from typing import List
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse, Response, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST

from . import models, schemas, crud
from .database import engine, get_db
from .config import get_settings
from .metrics import (
    URL_CREATED_TOTAL,
    URL_REDIRECTS_TOTAL,
    URL_NOT_FOUND_TOTAL,
    REQUEST_DURATION,
    ACTIVE_URLS_GAUGE
)
from .aws_client import ensure_bucket_exists, upload_stats_to_s3
from .tracing import setup_tracing, instrument_fastapi

# Logger — uygulama günlüğü (log kayıtları)
logger = logging.getLogger(__name__)
settings = get_settings()


# ─────────────────────────────────────────────────────────
# UYGULAMA BAŞLATMA
# ─────────────────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Uygulama başlarken ve kapanırken çalışır.

    Başlarken:
    - Veritabanı tablolarını oluştur
    - S3 bucket'ı hazırla

    Kapanırken:
    - Temizlik yap
    """
    # Başlatma
    logger.info("🚀 URL Shortener Service başlatılıyor...")

    # Veritabanı tablolarını oluştur
    models.Base.metadata.create_all(bind=engine)
    logger.info("✅ Veritabanı tabloları hazır")

    # S3 bucket'ı hazırla (LocalStack çalışıyorsa)
    if ensure_bucket_exists():
        logger.info("✅ S3 bucket hazır")
    else:
        logger.warning("⚠️  S3 (LocalStack) bağlantısı yok — S3 özellikleri devre dışı")

    yield  # Uygulama burada çalışır

    # Kapanma
    logger.info("🛑 URL Shortener Service kapatılıyor...")


# FastAPI uygulamasını oluştur
app = FastAPI(
    title="URL Shortener Service",
    description="""
    ## 🔗 URL Kısaltma Servisi

    Bu API ile:
    - Uzun URL'leri kısa kodlara dönüştürebilirsiniz
    - Kısa kodları kullanarak orijinal URL'ye yönlenebilirsiniz
    - Her kısa URL'nin kaç kez tıklandığını görebilirsiniz

    **Konu #1: URL Shortener Service** — Bulut Mimarilerinde Test Mühendisliği Dönem Projesi
    """,
    version="1.0.0",
    lifespan=lifespan,
    # ReDoc ve Swagger UI — CDN yerine unpkg kullan (daha güvenilir)
    redoc_js_url="https://unpkg.com/redoc@latest/bundles/redoc.standalone.js",
    swagger_ui_parameters={"persistAuthorization": True},
)


# Static dosyaları sun (HTML arayüzü)
_static_dir = _os.path.join(_os.path.dirname(__file__), "static")

# OpenTelemetry — FastAPI instrumentation (app yaratıldıktan hemen sonra)
try:
    setup_tracing(db_engine=engine)
    instrument_fastapi(app)
except Exception as e:
    logger.warning(f"⚠️  OTel başlatılamadı: {e}")

if _os.path.exists(_static_dir):
    app.mount("/static", StaticFiles(directory=_static_dir), name="static")


@app.get("/", response_class=HTMLResponse, tags=["Sistem"], include_in_schema=False)
def serve_frontend():
    """Ana sayfa — HTML arayüzünü döndürür."""
    html_file = _os.path.join(_static_dir, "index.html")
    if _os.path.exists(html_file):
        with open(html_file, "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>URL Shortener API</h1><p><a href='/docs'>API Docs</a></p>")


# CORS Middleware — Farklı domainlerden API'ye erişim izni
# Örneğin: Tarayıcıda çalışan JavaScript'in API'ye erişebilmesi için
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Tüm originlere izin ver (production'da kısıtla!)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ─────────────────────────────────────────────────────────
# MIDDLEWARE — Her İsteği Aralayan Katman
# ─────────────────────────────────────────────────────────

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    """
    Middleware nedir?
      Her HTTP isteği gelmeden önce ve yanıt gitmeden sonra çalışan kod.

    Bu middleware ne yapıyor?
      Her isteğin ne kadar sürdüğünü ölçüyor ve Prometheus'a kaydediyor.
      Stopwatch gibi: istek geldi → timer başlat → yanıt gönderildi → timer durdur.
    """
    start_time = time.time()  # Zamanı başlat

    response = await call_next(request)  # İsteği işle

    duration = time.time() - start_time  # Geçen süreyi hesapla

    # Prometheus'a kaydet
    REQUEST_DURATION.labels(
        method=request.method,
        endpoint=request.url.path
    ).observe(duration)

    return response


# ─────────────────────────────────────────────────────────
# ENDPOINT'LER — API Adresleri
# ─────────────────────────────────────────────────────────

@app.get("/health", response_model=schemas.HealthCheck, tags=["Sistem"])
def health_check():
    """
    Sağlık Kontrolü Endpoint'i

    Ne işe yarar?
      "Uygulama çalışıyor mu?" sorusuna cevap verir.
      Kubernetes bu endpoint'i kullanarak uygulamanın sağlıklı olup olmadığını kontrol eder.
      GitHub Actions smoke test olarak bu endpoint'i çağırır.

    Örnek yanıt:
      { "status": "healthy", "message": "URL Shortener çalışıyor", "version": "1.0.0" }
    """
    return schemas.HealthCheck(
        status="healthy",
        message="URL Shortener Service çalışıyor 🚀",
        version="1.0.0"
    )


@app.post("/shorten", response_model=schemas.URLResponse, status_code=201, tags=["URL"])
def create_short_url(
    url_data: schemas.URLCreate,
    db: Session = Depends(get_db)
):
    """
    Yeni Kısa URL Oluştur

    Kullanım:
      POST /shorten
      Body: { "original_url": "https://google.com" }

    Yanıt:
      { "short_code": "abc123", "short_url": "http://localhost:8000/abc123", ... }

    Depends(get_db) nedir?
      FastAPI'nin dependency injection özelliği.
      "Bu endpoint için bir veritabanı bağlantısı lazım" der.
      FastAPI otomatik olarak get_db() fonksiyonunu çağırır.
    """
    try:
        db_url = crud.create_short_url(db, url_data)

        # Prometheus sayacını artır
        URL_CREATED_TOTAL.inc()

        # Aktif URL sayısını güncelle
        ACTIVE_URLS_GAUGE.set(crud.get_url_count(db))

        # İstatistikleri S3'e yükle (LocalStack çalışıyorsa)
        # Not: Bu çağrı LocalStack yoksa sessizce başarısız olur
        try:
            upload_stats_to_s3({
                "event": "url_created",
                "short_code": db_url.short_code,
                "original_url": db_url.original_url,
                "total_urls": crud.get_url_count(db)
            })
        except Exception:
            pass  # LocalStack olmasa da devam et

        # short_url ekleyerek yanıt döndür
        return schemas.URLResponse(
            id=db_url.id,
            short_code=db_url.short_code,
            short_url=crud.build_short_url(db_url.short_code),
            original_url=db_url.original_url,
            click_count=db_url.click_count,
            created_at=db_url.created_at
        )

    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


# ─────────────────────────────────────────────────────────
# PROMETHEUS METRİKLERİ ENDPOINT'İ
# ÖNEMLI: Bu route /{short_code}'dan ÖNCE tanımlanmalı!
# ─────────────────────────────────────────────────────────

@app.get("/metrics", tags=["Sistem"])
def prometheus_metrics():
    """
    Prometheus Metrikleri

    Prometheus bu endpoint'i düzenli aralıklarla çeker (scrape eder).
    Dönen veri düz metin formatındadır (PromQL formatı).

    ⚠️ Bu route /{short_code}'dan ÖNCE olmalı, aksi halde catch-all tarafından yakalanır!
    """
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/{short_code}", tags=["URL"])
def redirect_to_url(short_code: str, db: Session = Depends(get_db)):
    """
    Kısa URL'ye Yönlendir (Redirect)

    Kullanım:
      GET /abc123

    Ne olur?
      - "abc123" veritabanında aranır
      - Bulunursa → 301 Redirect ile orijinal URL'ye yönlendirir
      - Bulunamazsa → 404 Not Found hatası verir

    HTTP 301 nedir?
      "Bu adres kalıcı olarak başka bir yere taşındı" demek.
      Tarayıcı otomatik olarak yeni adrese gider.
    """
    db_url = crud.get_url_by_short_code(db, short_code)

    if not db_url:
        URL_NOT_FOUND_TOTAL.inc()
        raise HTTPException(
            status_code=404,
            detail=f"'{short_code}' kodlu kısa URL bulunamadı"
        )

    # Tıklamayı kaydet ve sayacı artır
    crud.record_click(db, db_url)

    # Prometheus'a kaydet
    URL_REDIRECTS_TOTAL.labels(short_code=short_code).inc()

    # Kullanıcıyı orijinal URL'ye yönlendir
    return RedirectResponse(url=db_url.original_url, status_code=301)


@app.get("/urls/list", response_model=List[schemas.URLResponse], tags=["URL"])
def list_urls(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Tüm Kısa URL'leri Listele

    Kullanım:
      GET /urls/list
      GET /urls/list?skip=0&limit=10  (sayfalama için)

    Yanıt:
      [ { "short_code": "abc123", ... }, { "short_code": "xyz789", ... }, ... ]
    """
    db_urls = crud.get_all_urls(db, skip=skip, limit=limit)

    return [
        schemas.URLResponse(
            id=url.id,
            short_code=url.short_code,
            short_url=crud.build_short_url(url.short_code),
            original_url=url.original_url,
            click_count=url.click_count,
            created_at=url.created_at
        )
        for url in db_urls
    ]


@app.get("/urls/{short_code}", response_model=schemas.URLResponse, tags=["URL"])
def get_url_detail(short_code: str, db: Session = Depends(get_db)):
    """
    Belirli Bir Kısa URL'nin Detayı

    Kullanım:
      GET /urls/abc123

    NOT: Bu endpoint yönlendirme YAPMAZ, sadece bilgi gösterir.
         Yönlendirme için GET /abc123 kullanın.
    """
    db_url = crud.get_url_by_short_code(db, short_code)

    if not db_url:
        raise HTTPException(
            status_code=404,
            detail=f"'{short_code}' kodlu URL bulunamadı"
        )

    return schemas.URLResponse(
        id=db_url.id,
        short_code=db_url.short_code,
        short_url=crud.build_short_url(db_url.short_code),
        original_url=db_url.original_url,
        click_count=db_url.click_count,
        created_at=db_url.created_at
    )


@app.get("/stats/{short_code}", response_model=schemas.URLStats, tags=["İstatistik"])
def get_url_stats(short_code: str, db: Session = Depends(get_db)):
    """
    URL İstatistiklerini Görüntüle

    Kullanım:
      GET /stats/abc123

    Yanıt:
      {
        "short_code": "abc123",
        "original_url": "https://google.com",
        "click_count": 42,
        "created_at": "2024-01-15T10:30:00"
      }
    """
    db_url = crud.get_url_by_short_code(db, short_code)

    if not db_url:
        raise HTTPException(
            status_code=404,
            detail=f"'{short_code}' kodlu URL bulunamadı"
        )

    return db_url


@app.delete("/urls/{short_code}", tags=["URL"])
def delete_url(short_code: str, db: Session = Depends(get_db)):
    """
    Kısa URL'yi Sil

    Kullanım:
      DELETE /urls/abc123

    Yanıt:
      { "message": "abc123 başarıyla silindi" }
    """
    success = crud.delete_url(db, short_code)

    if not success:
        raise HTTPException(
            status_code=404,
            detail=f"'{short_code}' kodlu URL bulunamadı"
        )

    # Aktif URL sayısını güncelle
    ACTIVE_URLS_GAUGE.set(crud.get_url_count(db))

    return {"message": f"'{short_code}' başarıyla silindi"}
