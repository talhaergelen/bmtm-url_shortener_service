"""
test_database.py — Veritabanı Integration Testleri

Bu dosya ne işe yarar?
  Veritabanı ile doğrudan etkileşim testleri yapar.
  Kılavuz: "Testcontainers ile en az 2 test" istiyor.
  
Testcontainers nedir?
  Test sırasında Docker ile gerçek bir PostgreSQL başlatır.
  Test biter → Docker otomatik kapatılır.
  
  Neden kullanırız?
  - Gerçek PostgreSQL davranışını test etmek için
  - SQLite ile PostgreSQL bazen farklı davranır
  - Üretim ortamına daha yakın test
  
Not: Bu testler Docker çalışırken çalışır.
     Docker yoksa skip edilir (@pytest.mark.skipif ile).
"""

import pytest
import os

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from src.models import Base, URL, Click
from src import crud, schemas


# ─────────────────────────────────────────────────────────
# TESTCONTAINERS KURULUMU
# ─────────────────────────────────────────────────────────

def is_docker_available():
    """Docker çalışıyor mu kontrol eder."""
    import subprocess
    try:
        result = subprocess.run(
            ["docker", "info"],
            capture_output=True,
            timeout=5
        )
        return result.returncode == 0
    except Exception:
        return False


# Docker yoksa bu testleri atla
pytestmark = pytest.mark.skipif(
    not is_docker_available(),
    reason="Docker çalışmıyor — Testcontainers testleri atlanıyor"
)


@pytest.fixture(scope="module")
def postgres_container():
    """
    Module kapsamında bir PostgreSQL container başlatır.
    
    scope="module" → Tüm test modülü için tek container.
    Daha hızlı: Her test için ayrı container başlatmak yerine
    bir kere başlatıp paylaştırırız.
    """
    try:
        from testcontainers.postgres import PostgresContainer
        
        with PostgresContainer("postgres:16-alpine") as postgres:
            yield postgres
    except Exception as e:
        pytest.skip(f"Testcontainers başlatılamadı: {e}")


@pytest.fixture(scope="module")
def postgres_engine(postgres_container):
    """PostgreSQL bağlantı motoru."""
    engine = create_engine(
        postgres_container.get_connection_url(),
        poolclass=NullPool
    )
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture(scope="function")
def postgres_session(postgres_engine):
    """Her test için temiz bir PostgreSQL session."""
    SessionLocal = sessionmaker(bind=postgres_engine)
    session = SessionLocal()
    
    yield session
    
    session.rollback()
    session.close()


# ─────────────────────────────────────────────────────────
# TESTCONTAINERS TESTLERİ — EN AZ 2 TEST GEREKLİ
# ─────────────────────────────────────────────────────────

class TestPostgresDatabase:
    """Gerçek PostgreSQL ile integration testler."""

    def test_can_create_and_retrieve_url(self, postgres_session):
        """
        Test 1: URL oluşturma ve geri alma.
        
        PostgreSQL'de de SQLite'daki gibi URL oluşturulabilmeli.
        """
        url_data = schemas.URLCreate(original_url="https://postgres-test.com")
        
        created = crud.create_short_url(postgres_session, url_data)
        
        assert created.id is not None
        assert created.short_code is not None
        assert created.original_url == "https://postgres-test.com"
        
        # Tekrar sorgula
        found = crud.get_url_by_short_code(postgres_session, created.short_code)
        assert found is not None
        assert found.id == created.id

    def test_click_tracking_with_postgres(self, postgres_session):
        """
        Test 2: Tıklama takibi PostgreSQL'de doğru çalışmalı.
        
        Click tablosuna kayıt eklenmeli, URL'nin click_count artmalı.
        """
        # URL oluştur
        url_data = schemas.URLCreate(original_url="https://click-test.com")
        url = crud.create_short_url(postgres_session, url_data)
        
        # 3 kez tıkla
        for _ in range(3):
            crud.record_click(postgres_session, url)
        
        # Sonuçları kontrol et
        postgres_session.refresh(url)
        assert url.click_count == 3
        
        # Click tablosunu kontrol et
        clicks = postgres_session.query(Click).filter(
            Click.url_id == url.id
        ).all()
        assert len(clicks) == 3

    def test_cascade_delete_removes_clicks(self, postgres_session):
        """
        Test 3: URL silinince ilişkili tıklamalar da silinmeli.
        
        Cascade delete: Ana kayıt silinince alt kayıtlar da silinir.
        """
        url_data = schemas.URLCreate(original_url="https://cascade-test.com")
        url = crud.create_short_url(postgres_session, url_data)
        
        # Tıklama kayıtları ekle
        for _ in range(2):
            crud.record_click(postgres_session, url)
        
        url_id = url.id
        short_code = url.short_code
        
        # URL'yi sil
        crud.delete_url(postgres_session, short_code)
        
        # Click kayıtları da silinmeli
        remaining_clicks = postgres_session.query(Click).filter(
            Click.url_id == url_id
        ).all()
        assert len(remaining_clicks) == 0

    def test_unique_constraint_on_short_code(self, postgres_session):
        """
        Test 4: Aynı short_code iki kez kullanılamaz.
        
        Unique constraint: Veritabanı seviyesinde benzersizlik garantisi.
        """
        from sqlalchemy.exc import IntegrityError
        
        # İlk URL oluştur
        url1 = URL(short_code="uniq01", original_url="https://first.com")
        postgres_session.add(url1)
        postgres_session.commit()
        
        # Aynı short_code ile ikinci URL oluşturmaya çalış
        url2 = URL(short_code="uniq01", original_url="https://second.com")
        postgres_session.add(url2)
        
        with pytest.raises(IntegrityError):
            postgres_session.commit()
        
        postgres_session.rollback()

    def test_database_connection_is_healthy(self, postgres_engine):
        """
        Test 5: Veritabanı bağlantısı sağlıklı olmalı.
        
        Basit bir SELECT 1 sorgusu çalıştır.
        """
        with postgres_engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            assert result.scalar() == 1


# ─────────────────────────────────────────────────────────
# SQLITE TESTLERİ (Docker gerektirmez)
# ─────────────────────────────────────────────────────────

class TestSQLiteDatabase:
    """SQLite veritabanı ile basit testler — Docker gerekmez."""

    def test_url_table_exists(self, db_session):
        """
        URL tablosu mevcut olmalı.
        conftest.py'deki db_session fixture kullanılır.
        """
        # Basit bir sorgu ile tablonun var olduğunu doğrula
        result = db_session.query(URL).all()
        assert isinstance(result, list)

    def test_click_table_exists(self, db_session):
        """Click tablosu mevcut olmalı."""
        result = db_session.query(Click).all()
        assert isinstance(result, list)

    def test_url_model_fields(self, db_session):
        """URL modeli gerekli alanları içermeli."""
        url = URL(short_code="test01", original_url="https://test.com")
        db_session.add(url)
        db_session.commit()
        db_session.refresh(url)
        
        # Gerekli alanları kontrol et
        assert url.id is not None
        assert url.short_code == "test01"
        assert url.original_url == "https://test.com"
        assert url.click_count == 0  # Default değer
        assert url.created_at is not None  # Otomatik set edilmeli
