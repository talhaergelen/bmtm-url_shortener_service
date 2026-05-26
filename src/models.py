"""
models.py — Veritabanı Tabloları (Modeller)

Bu dosya ne işe yarar?
  Veritabanındaki tabloları Python sınıfları olarak tanımlar.
  Her sınıf = 1 tablo.
  Her sınıf değişkeni = 1 sütun (column).

Model nedir?
  Gerçek dünyadaki bir şeyin dijital temsili.
  Örneğin: URL modeli → her kısa URL kaydının hangi bilgileri saklayacağını tanımlar.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from .database import Base


class URL(Base):
    """
    URL Tablosu

    Her satır = 1 kısa URL kaydı

    Örnek bir satır:
    id=1, short_code="abc123", original_url="https://google.com", click_count=42
    """
    __tablename__ = "urls"  # Veritabanındaki tablo adı

    id = Column(Integer, primary_key=True, index=True)
    # primary_key=True → Bu sütun her satırı benzersiz tanımlar (1, 2, 3, ...)
    # index=True → Hızlı arama için indeks oluşturur

    short_code = Column(String(10), unique=True, index=True, nullable=False)
    # unique=True → Aynı kısa kod iki kez olamaz
    # nullable=False → Bu alan boş olamaz

    original_url = Column(Text, nullable=False)
    # Text → Uzun string için (URL'ler çok uzun olabilir)

    click_count = Column(Integer, default=0)
    # Kaç kez tıklandı — başlangıçta 0

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # Kayıt ne zaman oluşturuldu — otomatik olarak şu anki zamanı yazar

    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    # Son ne zaman güncellendi

    # Bir URL'nin tıklamalarıyla ilişkisi (1 URL → çok tıklama)
    clicks = relationship("Click", back_populates="url", cascade="all, delete-orphan")

    def __repr__(self):
        """Bu objeyi print ettiğimizde ne gösterir?"""
        return f"<URL id={self.id} short_code={self.short_code}>"


class Click(Base):
    """
    Click (Tıklama) Tablosu

    Her kısa URL tıklandığında buraya bir kayıt eklenir.
    Bu sayede "bu linke ne zaman tıklandı?" gibi istatistikler tutabiliriz.

    Örnek:
    id=1, url_id=1, clicked_at=2024-01-15 10:30:00
    id=2, url_id=1, clicked_at=2024-01-15 11:45:00
    → URL id=1, 2 kez tıklandı
    """
    __tablename__ = "clicks"

    id = Column(Integer, primary_key=True, index=True)

    url_id = Column(Integer, ForeignKey("urls.id"), nullable=False)
    # ForeignKey → "Bu url_id, urls tablosundaki id sütununa referans verir"
    # Tablolar arası ilişki kurar

    clicked_at = Column(DateTime(timezone=True), server_default=func.now())

    # Hangi URL'ye ait olduğu (Click → URL ilişkisi)
    url = relationship("URL", back_populates="clicks")

    def __repr__(self):
        return f"<Click id={self.id} url_id={self.url_id}>"
