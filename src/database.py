"""
database.py — Veritabanı Bağlantısı

Bu dosya ne işe yarar?
  Uygulamamız ile veritabanı (PostgreSQL/SQLite) arasındaki köprüdür.
  
Veritabanı nedir?
  Verileri düzenli sakladığımız yer. Tablo tablo saklarız.
  Bizim tablomuz: URL'ler
  
  | id | short_code | original_url              | click_count | created_at |
  |----|------------|---------------------------|-------------|------------|
  | 1  | abc123     | https://google.com/...    | 42          | 2024-01-01 |
  | 2  | xyz789     | https://youtube.com/...   | 7           | 2024-01-02 |

SQLAlchemy nedir?
  Python ile veritabanı arasında tercüman. SQL yazmak yerine Python kodu yazarız.
  O bunu SQL'e çevirir.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import get_settings

settings = get_settings()

# Veritabanı motoru — bağlantıyı kurar
# SQLite için özel ayar: check_same_thread=False (test sırasında gerekli)
if settings.database_url.startswith("sqlite"):
    engine = create_engine(
        settings.database_url,
        connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.database_url)

# Her API isteği için ayrı bir veritabanı oturumu oluşturur
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Tüm modellerimizin miras alacağı temel sınıf
Base = declarative_base()


def get_db():
    """
    FastAPI Dependency (bağımlılık) fonksiyonu.
    
    Her API isteği geldiğinde çalışır:
    1. Veritabanı bağlantısı açar
    2. İsteği işler
    3. Bağlantıyı kapatır (finally bloğu)
    
    Bu "context manager" (with bloğu gibi) mantığıyla çalışır.
    """
    db = SessionLocal()
    try:
        yield db  # Buraya kadar aç, yield'den sonra kapat
    finally:
        db.close()
