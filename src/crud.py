"""
crud.py — Veritabanı İşlemleri (CRUD)

Bu dosya ne işe yarar?
  Veritabanındaki tüm okuma/yazma işlemlerini yapar.

CRUD nedir?
  Create (Oluştur), Read (Oku), Update (Güncelle), Delete (Sil)
  Her uygulamanın temel veri işlemleri bunlardır.

  Örnek:
  Create → Yeni kısa URL oluştur (INSERT INTO urls ...)
  Read   → Kısa kodu bul (SELECT * FROM urls WHERE short_code = ...)
  Update → Tıklama sayısını artır (UPDATE urls SET click_count = click_count + 1 ...)
  Delete → Kısa URL'yi sil (DELETE FROM urls WHERE id = ...)
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from . import models, schemas
from .shortener import generate_unique_short_code, is_valid_url
from .config import get_settings

settings = get_settings()


# ─────────────────────────────────────────────────────────
# CREATE — Yeni Kayıt Oluşturma
# ─────────────────────────────────────────────────────────

def create_short_url(db: Session, url_data: schemas.URLCreate) -> models.URL:
    """
    Yeni bir kısa URL oluşturur ve veritabanına kaydeder.

    Akış:
    1. URL geçerli mi? Kontrol et
    2. Benzersiz kısa kod üret
    3. Veritabanına kaydet
    4. Kaydı geri döndür

    Args:
        db: Veritabanı bağlantısı (session)
        url_data: Kullanıcıdan gelen URL bilgisi

    Returns:
        Oluşturulan URL kaydı
    """
    if not is_valid_url(url_data.original_url):
        raise ValueError(f"Geçersiz URL: {url_data.original_url}")

    # Benzersiz kısa kod üret
    short_code = generate_unique_short_code(db)

    # Yeni URL kaydı oluştur (henüz veritabanında değil, sadece Python'da)
    db_url = models.URL(
        short_code=short_code,
        original_url=url_data.original_url,
        click_count=0
    )

    db.add(db_url)      # Veritabanına ekle (henüz gerçekleşmedi)
    db.commit()          # Gerçekleştir (kaydet)
    db.refresh(db_url)  # Veritabanından taze veriyi al (örn: id, created_at)

    return db_url


# ─────────────────────────────────────────────────────────
# READ — Kayıt Okuma
# ─────────────────────────────────────────────────────────

def get_url_by_short_code(db: Session, short_code: str) -> Optional[models.URL]:
    """
    Kısa koda göre URL'yi bulur.

    Args:
        db: Veritabanı bağlantısı
        short_code: Aranan kısa kod (örn: "abc123")

    Returns:
        URL kaydı veya None (bulunamadıysa)
    """
    return db.query(models.URL).filter(models.URL.short_code == short_code).first()


def get_all_urls(db: Session, skip: int = 0, limit: int = 100) -> List[models.URL]:
    """
    Tüm URL'leri listeler.

    skip ve limit neden var?
      Veritabanında 1 milyon URL olabilir. Hepsini bir anda göndermek yavaş olur.
      skip=0, limit=10 → İlk 10 URL
      skip=10, limit=10 → Sonraki 10 URL (sayfalama/pagination)
    """
    return db.query(models.URL).offset(skip).limit(limit).all()


def get_url_count(db: Session) -> int:
    """Toplam kısa URL sayısını döndürür."""
    return db.query(models.URL).count()


# ─────────────────────────────────────────────────────────
# UPDATE — Kayıt Güncelleme
# ─────────────────────────────────────────────────────────

def increment_click_count(db: Session, url: models.URL) -> models.URL:
    """
    Bir URL'nin tıklama sayısını 1 artırır.

    Bu fonksiyon ne zaman çağrılır?
      Birisi kısa URL'yi kullandığında (GET /{short_code} endpoint'i)
      tıklama sayısını artırırız.
    """
    url.click_count += 1  # Python'da sayıyı artır
    db.commit()            # Veritabanına kaydet
    db.refresh(url)        # Taze veriyi al
    return url


def record_click(db: Session, url: models.URL) -> models.Click:
    """
    Tıklama kaydı oluşturur (detaylı istatistik için).

    URL'nin click_count'unu artırmanın yanı sıra,
    ayrı bir Click tablosuna da kayıt ekleriz.
    Bu sayede "ne zaman tıklandı?" sorusunu cevaplayabiliriz.
    """
    # Click kaydı oluştur
    click = models.Click(url_id=url.id)
    db.add(click)

    # Ayrıca click_count'u da artır
    url.click_count += 1

    db.commit()
    db.refresh(url)
    return click


# ─────────────────────────────────────────────────────────
# DELETE — Kayıt Silme
# ─────────────────────────────────────────────────────────

def delete_url(db: Session, short_code: str) -> bool:
    """
    Kısa URL'yi siler.

    Returns:
        True → Başarıyla silindi
        False → URL bulunamadı
    """
    db_url = get_url_by_short_code(db, short_code)
    if not db_url:
        return False

    db.delete(db_url)  # Sil (henüz gerçekleşmedi)
    db.commit()         # Gerçekleştir
    return True


# ─────────────────────────────────────────────────────────
# YARDIMCI FONKSİYONLAR
# ─────────────────────────────────────────────────────────

def build_short_url(short_code: str) -> str:
    """
    Kısa kodu tam URL'ye dönüştürür.

    Örnek: "abc123" → "http://localhost:8000/abc123"
    """
    return f"{settings.base_url}/{short_code}"
