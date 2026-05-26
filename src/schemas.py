"""
schemas.py — Pydantic Şemaları (API Veri Formatları)

Bu dosya ne işe yarar?
  API'mize gelen ve giden verilerin formatını tanımlar.

Şema nedir?
  "Bu endpoint'e hangi veriler gelmeli, hangi veriler dönmeli?" sorusunun cevabı.

  Örnek:
  Kullanıcı bize POST ile şunu gönderir:
    { "original_url": "https://google.com" }

  Biz ona şunu döneriz:
    { "short_code": "abc123", "short_url": "http://localhost:8000/abc123", ... }

Pydantic nedir?
  Python'da veri doğrulama kütüphanesi.
  "original_url bir URL mi?" diye otomatik kontrol eder.
  Tip güvenliği sağlar (string yerine int gelirse hata verir).
"""

from pydantic import BaseModel, field_validator

from datetime import datetime
from typing import Optional, List


# ─────────────────────────────────────────────────────────
# ISTEK (REQUEST) ŞEMALARI — Kullanıcıdan Gelen Veriler
# ─────────────────────────────────────────────────────────

class URLCreate(BaseModel):
    """
    Yeni kısa URL oluşturma isteği.

    Kullanıcı bize sadece şunu gönderir:
      { "original_url": "https://google.com" }
    """
    original_url: str  # Kısaltılacak uzun URL

    @field_validator("original_url")
    @classmethod
    def validate_url(cls, v: str) -> str:
        """URL formatı doğru mu kontrol eder."""
        if not v.startswith(("http://", "https://")):
            raise ValueError("URL http:// veya https:// ile başlamalıdır")
        if len(v) > 2048:
            raise ValueError("URL çok uzun (max 2048 karakter)")
        return v


# ─────────────────────────────────────────────────────────
# YANIT (RESPONSE) ŞEMALARI — Kullanıcıya Gönderilen Veriler
# ─────────────────────────────────────────────────────────

class URLResponse(BaseModel):
    """
    URL oluşturduktan sonra kullanıcıya döneceğimiz yanıt.

    Örnek yanıt:
    {
      "id": 1,
      "short_code": "abc123",
      "short_url": "http://localhost:8000/abc123",
      "original_url": "https://google.com",
      "click_count": 0,
      "created_at": "2024-01-15T10:30:00"
    }
    """
    id: int
    short_code: str
    short_url: str           # Tam kısa URL (base_url + short_code)
    original_url: str
    click_count: int
    created_at: datetime

    class Config:
        from_attributes = True  # SQLAlchemy model → Pydantic dönüşümü için


class URLStats(BaseModel):
    """
    Bir kısa URL'nin istatistikleri.

    Örnek:
    {
      "short_code": "abc123",
      "original_url": "https://google.com",
      "click_count": 42,
      "created_at": "2024-01-15T10:30:00"
    }
    """
    short_code: str
    original_url: str
    click_count: int
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class URLList(BaseModel):
    """URL listesi için şema."""
    urls: List[URLResponse]
    total: int


class HealthCheck(BaseModel):
    """Sunucu sağlık kontrolü yanıtı."""
    status: str
    message: str
    version: str = "1.0.0"
