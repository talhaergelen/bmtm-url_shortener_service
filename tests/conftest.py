"""
conftest.py — Pytest Yapılandırması ve Fixtures

Bu dosya ne işe yarar?
  pytest'in her test dosyasında kullanabileceği "hazır kaynaklar" (fixtures) tanımlar.
  
Fixture nedir?
  Her test fonksiyonuna otomatik verilen hazır nesne.
  Örnek: Her testte veritabanı bağlantısı açıp kapatmak zorunda kalmak yerine,
         conftest'teki fixture bunu otomatik yapar.

@pytest.fixture nedir?
  Bir fonksiyonu "fixture" olarak işaretler.
  Test fonksiyonu parametre olarak fixture adını yazarsa, pytest otomatik çağırır.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.main import app
from src.database import Base, get_db
from src.models import URL, Click

# ─────────────────────────────────────────────────────────
# TEST VERİTABANI KURULUMU
# ─────────────────────────────────────────────────────────

# Test için bellekte (in-memory) SQLite veritabanı kullan
# Her test temiz bir veritabanı ile başlar
TEST_DATABASE_URL = "sqlite:///:memory:"


@pytest.fixture(scope="function")
def db_engine():
    """
    Her test fonksiyonu için ayrı bir veritabanı motoru oluşturur.
    
    scope="function" → Her test ayrı veritabanı kullanır (izolasyon sağlar).
    
    StaticPool nedir?
      SQLite in-memory DB'nin thread'ler arası paylaşılabilmesi için.
    """
    engine = create_engine(
        TEST_DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    # Test tablolarını oluştur
    Base.metadata.create_all(bind=engine)
    
    yield engine  # Testi çalıştır
    
    # Tablo temizliği
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def db_session(db_engine):
    """
    Test için veritabanı session'ı (bağlantı oturumu).
    
    Her test sonunda rollback yapılır — testler birbirini etkilemez.
    """
    TestingSessionLocal = sessionmaker(
        autocommit=False, 
        autoflush=False, 
        bind=db_engine
    )
    session = TestingSessionLocal()
    
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    """
    FastAPI test istemcisi.
    
    TestClient nedir?
      Gerçek HTTP sunucusu başlatmadan API'yi test etmemizi sağlar.
      httpx kütüphanesini kullanır.
    
    override_get_db nedir?
      Normalde uygulama gerçek DB kullanır.
      Test sırasında test DB'sini kullanması için dependency'yi değiştiririz.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    # Test sonunda override'ı temizle
    app.dependency_overrides.clear()


# ─────────────────────────────────────────────────────────
# HAZIR TEST VERİLERİ
# ─────────────────────────────────────────────────────────

@pytest.fixture
def sample_url(db_session):
    """
    Testlerde kullanmak için hazır bir URL kaydı oluşturur.
    
    Birçok test "önce URL oluştur, sonra test et" yapmak ister.
    Bu fixture bunu otomatik yapar.
    """
    url = URL(
        short_code="abc123",
        original_url="https://google.com",
        click_count=0
    )
    db_session.add(url)
    db_session.commit()
    db_session.refresh(url)
    return url


@pytest.fixture
def multiple_urls(db_session):
    """Birden fazla URL fixture'ı — liste testleri için."""
    urls = []
    test_data = [
        ("xK2mN9", "https://github.com"),
        ("aBc456", "https://stackoverflow.com"),
        ("Zy7pQr", "https://python.org"),
    ]
    
    for short_code, original_url in test_data:
        url = URL(
            short_code=short_code,
            original_url=original_url,
            click_count=0
        )
        db_session.add(url)
    
    db_session.commit()
    
    for short_code, _ in test_data:
        url = db_session.query(URL).filter(URL.short_code == short_code).first()
        urls.append(url)
    
    return urls
