"""
config.py — Uygulama Ayarları

Bu dosya ne işe yarar?
  .env dosyasındaki ayarları okur ve uygulama genelinde kullanılabilir hale getirir.
  Örneğin veritabanı adresi, base URL gibi değerleri buradan alırız.

Pydantic Settings ne demek?
  Python'da veri doğrulama kütüphanesi. "DATABASE_URL bir string mi?" gibi kontroller yapar.
"""

from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Uygulama Bilgileri
    app_name: str = "URL Shortener Service"
    debug: bool = False

    # Veritabanı — URL'leri nerede saklayacağımız
    database_url: str = "sqlite:///./urlshortener.db"

    # Kısa URL'lerin başı (örn: http://localhost:8000/abc123)
    base_url: str = "http://localhost:8000"

    # AWS (LocalStack) ayarları
    aws_endpoint_url: str = "http://localhost:4566"
    aws_access_key_id: str = "test"
    aws_secret_access_key: str = "test"
    aws_default_region: str = "us-east-1"
    s3_bucket_name: str = "url-shortener-stats"

    class Config:
        env_file = ".env"  # .env dosyasından okur
        case_sensitive = False
        extra = "ignore"  # Tanımlanmamış .env değerlerini yoksay


@lru_cache()  # Ayarları her seferinde yeniden okumamak için önbelleğe alır
def get_settings() -> Settings:
    return Settings()
