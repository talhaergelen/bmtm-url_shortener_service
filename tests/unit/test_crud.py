"""
test_crud.py — Veritabanı CRUD İşlemleri Unit Testleri

Bu dosya ne işe yarar?
  src/crud.py dosyasındaki fonksiyonları test eder.
  
Mock nedir?
  Gerçek bir nesnenin yerine geçen sahte nesne.
  Örneğin: Gerçek veritabanı yerine sahte veritabanı kullanmak.
  
Neden mock kullanırız?
  - Testler hızlı çalışsın (gerçek DB yavaş)
  - Dış bağımlılık olmadan test edilebilsin
  - Hata senaryoları kolayca simüle edilsin
"""

import pytest
from unittest.mock import MagicMock, patch

from src import crud, schemas
from src.models import URL


# ─────────────────────────────────────────────────────────
# create_short_url() TESTLERİ
# ─────────────────────────────────────────────────────────

class TestCreateShortUrl:
    """Yeni URL oluşturma fonksiyonu testleri."""

    def test_creates_url_with_valid_data(self, db_session):
        """
        Geçerli URL verisi ile yeni kayıt oluşturulabilmeli.
        
        db_session: conftest.py'den gelen fixture (test veritabanı).
        """
        url_data = schemas.URLCreate(original_url="https://google.com")
        
        result = crud.create_short_url(db_session, url_data)
        
        # Sonuçları doğrula
        assert result.id is not None, "ID atanmış olmalı"
        assert result.original_url == "https://google.com"
        assert result.short_code is not None
        assert len(result.short_code) == 6
        assert result.click_count == 0  # Başlangıçta sıfır

    def test_generated_short_code_is_unique(self, db_session):
        """İki farklı URL farklı short_code almalı."""
        url1 = crud.create_short_url(
            db_session, 
            schemas.URLCreate(original_url="https://google.com")
        )
        url2 = crud.create_short_url(
            db_session,
            schemas.URLCreate(original_url="https://github.com")
        )
        
        assert url1.short_code != url2.short_code

    def test_raises_value_error_for_invalid_url(self, db_session):
        """
        Geçersiz URL geldiğinde ValueError fırlatılmalı.
        
        pytest.raises() nedir?
          "Bu kod çalışınca şu exception fırlatılmalı" diye test eder.
        """
        url_data = schemas.URLCreate.__new__(schemas.URLCreate)
        object.__setattr__(url_data, 'original_url', 'merhaba-gecersiz-url')
        
        with pytest.raises(ValueError, match="Geçersiz URL"):
            crud.create_short_url(db_session, url_data)

    def test_url_is_persisted_in_database(self, db_session):
        """Oluşturulan URL veritabanına kaydedilmeli."""
        url_data = schemas.URLCreate(original_url="https://example.com")
        created = crud.create_short_url(db_session, url_data)
        
        # Veritabanından tekrar sorgula
        found = db_session.query(URL).filter(URL.id == created.id).first()
        assert found is not None
        assert found.original_url == "https://example.com"


# ─────────────────────────────────────────────────────────
# get_url_by_short_code() TESTLERİ
# ─────────────────────────────────────────────────────────

class TestGetUrlByShortCode:
    """Kısa koda göre URL bulma fonksiyonu testleri."""

    def test_returns_url_when_found(self, db_session, sample_url):
        """
        Var olan short_code ile URL bulunabilmeli.
        
        sample_url: conftest.py'deki fixture — hazır URL kaydı.
        """
        result = crud.get_url_by_short_code(db_session, "abc123")
        
        assert result is not None
        assert result.short_code == "abc123"
        assert result.original_url == "https://google.com"

    def test_returns_none_when_not_found(self, db_session):
        """Olmayan short_code için None dönmeli."""
        result = crud.get_url_by_short_code(db_session, "yok999")
        
        assert result is None

    def test_case_sensitive_lookup(self, db_session, sample_url):
        """
        Kısa kodlar büyük/küçük harf duyarlı olmalı.
        "abc123" ile "ABC123" farklı şeyler.
        """
        result = crud.get_url_by_short_code(db_session, "ABC123")
        assert result is None  # Büyük harf versiyonu yok


# ─────────────────────────────────────────────────────────
# get_all_urls() TESTLERİ
# ─────────────────────────────────────────────────────────

class TestGetAllUrls:
    """Tüm URL'leri listeleme fonksiyonu testleri."""

    def test_returns_empty_list_when_no_urls(self, db_session):
        """Veritabanı boşsa boş liste dönmeli."""
        result = crud.get_all_urls(db_session)
        assert result == []

    def test_returns_all_urls(self, db_session, multiple_urls):
        """
        Tüm URL'ler listelenebilmeli.
        
        multiple_urls: conftest.py'den 3 URL içeren fixture.
        """
        result = crud.get_all_urls(db_session)
        assert len(result) == 3

    def test_pagination_with_limit(self, db_session, multiple_urls):
        """limit parametresi çalışmalı."""
        result = crud.get_all_urls(db_session, skip=0, limit=2)
        assert len(result) == 2

    def test_pagination_with_skip(self, db_session, multiple_urls):
        """skip parametresi çalışmalı."""
        result = crud.get_all_urls(db_session, skip=2, limit=100)
        assert len(result) == 1  # 3 URL'den 2'sini atladık, 1 kaldı


# ─────────────────────────────────────────────────────────
# record_click() TESTLERİ
# ─────────────────────────────────────────────────────────

class TestRecordClick:
    """Tıklama kaydı fonksiyonu testleri."""

    def test_increments_click_count(self, db_session, sample_url):
        """Tıklandığında click_count bir artmalı."""
        initial_count = sample_url.click_count  # 0
        
        crud.record_click(db_session, sample_url)
        
        db_session.refresh(sample_url)
        assert sample_url.click_count == initial_count + 1

    def test_creates_click_record(self, db_session, sample_url):
        """Click tablosuna yeni kayıt eklenmeli."""
        from src.models import Click
        
        click = crud.record_click(db_session, sample_url)
        
        assert click.id is not None
        assert click.url_id == sample_url.id

    def test_multiple_clicks_increment_correctly(self, db_session, sample_url):
        """3 tıklama → click_count = 3 olmalı."""
        for _ in range(3):
            crud.record_click(db_session, sample_url)
        
        db_session.refresh(sample_url)
        assert sample_url.click_count == 3


# ─────────────────────────────────────────────────────────
# delete_url() TESTLERİ
# ─────────────────────────────────────────────────────────

class TestDeleteUrl:
    """URL silme fonksiyonu testleri."""

    def test_deletes_existing_url(self, db_session, sample_url):
        """Var olan URL silinebilmeli."""
        result = crud.delete_url(db_session, "abc123")
        
        assert result is True  # Başarılı silme

    def test_url_not_found_after_deletion(self, db_session, sample_url):
        """Silindikten sonra URL bulunamalı."""
        crud.delete_url(db_session, "abc123")
        
        found = crud.get_url_by_short_code(db_session, "abc123")
        assert found is None

    def test_returns_false_for_nonexistent_url(self, db_session):
        """Olmayan URL silmeye çalışınca False dönmeli."""
        result = crud.delete_url(db_session, "yok999")
        
        assert result is False


# ─────────────────────────────────────────────────────────
# build_short_url() TESTLERİ
# ─────────────────────────────────────────────────────────

class TestBuildShortUrl:
    """Tam URL oluşturma fonksiyonu testleri."""

    def test_builds_correct_url(self):
        """short_code → tam URL dönüşümü doğru olmalı."""
        result = crud.build_short_url("abc123")
        
        # base_url + "/" + short_code formatı
        assert "abc123" in result
        assert result.startswith("http")

    def test_url_contains_short_code(self):
        """Dönen URL short_code'u içermeli."""
        result = crud.build_short_url("xK2mN9")
        assert "xK2mN9" in result
