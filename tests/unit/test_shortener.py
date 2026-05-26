"""
test_shortener.py — URL Kısaltma Algoritması Unit Testleri

Bu dosya ne işe yarar?
  src/shortener.py dosyasındaki fonksiyonları test eder.

Unit Test nedir?
  En küçük kod parçasını (fonksiyon veya sınıf) izole ederek test etmek.
  Veritabanına, ağa, dış servislere bağımlılık olmadan çalışır.
  
  Mantık: "Bu fonksiyona şu girişi versem, şu çıkışı almalıyım."

Test fonksiyon isimleri:
  test_ ile başlar.
  "test_ne_test_ediyoruz_hangi_durum_beklenen_sonuç" formatı kullanılır.
"""

import pytest
import string

from src.shortener import generate_short_code, is_valid_url


# ─────────────────────────────────────────────────────────
# generate_short_code() FONKSİYON TESTLERİ
# ─────────────────────────────────────────────────────────

class TestGenerateShortCode:
    """generate_short_code() fonksiyonu için test grubu."""

    def test_returns_six_characters(self):
        """Üretilen kod tam 6 karakter olmalı."""
        code = generate_short_code()
        assert len(code) == 6, f"Beklenen 6, alınan: {len(code)}"

    def test_uses_only_alphanumeric_characters(self):
        """
        Kod sadece harf ve rakam içermeli (özel karakter yok).
        
        Neden önemli?
          URL'de özel karakterler sorun çıkarabilir.
          'abc-def' yerine 'abcdef' daha güvenli.
        """
        allowed_chars = set(string.ascii_letters + string.digits)
        
        for _ in range(20):  # 20 kez dene, her seferinde kontrol et
            code = generate_short_code()
            assert all(c in allowed_chars for c in code), \
                f"Geçersiz karakter bulundu: {code}"

    def test_generates_unique_codes(self):
        """
        Ardarda üretilen kodlar benzersiz olmalı.
        
        Not: Teorik olarak çakışma mümkün ama 62^6 = 56 milyar ihtimalle
             10 kod üretiminde çakışma pratikte imkansız.
        """
        codes = {generate_short_code() for _ in range(10)}
        assert len(codes) == 10, "10 kod üretiminde tekrar var!"

    def test_code_is_string_type(self):
        """Dönen değer string olmalı."""
        code = generate_short_code()
        assert isinstance(code, str)

    def test_code_not_empty(self):
        """Dönen değer boş olmamalı."""
        code = generate_short_code()
        assert code  # boş string False döner


# ─────────────────────────────────────────────────────────
# is_valid_url() FONKSİYON TESTLERİ
# ─────────────────────────────────────────────────────────

class TestIsValidUrl:
    """is_valid_url() fonksiyonu için test grubu."""

    # GEÇERLİ URL'LER — True dönmeli
    @pytest.mark.parametrize("url", [
        "https://google.com",
        "http://example.com",
        "https://www.github.com/python/cpython",
        "http://localhost:8000",
        "https://api.example.com/v1/endpoint?q=test&page=1",
        "http://192.168.1.1:8080",
        "https://sub.domain.co.uk/path/to/page",
    ])
    def test_valid_urls_return_true(self, url):
        """
        Geçerli URL'ler True dönmeli.
        
        @pytest.mark.parametrize nedir?
          Aynı testi farklı verilerle birden fazla kez çalıştırır.
          7 URL → 7 ayrı test çalışır.
        """
        assert is_valid_url(url) is True, f"Geçerli URL reddedildi: {url}"

    # GEÇERSİZ URL'LER — False dönmeli
    @pytest.mark.parametrize("url", [
        "merhaba",
        "google.com",           # http/https yok
        "ftp://example.com",    # ftp desteklenmez
        "",                     # boş string
        "not a url at all",
        "javascript:alert(1)",  # XSS girişimi
        "//example.com",        # protokol eksik
    ])
    def test_invalid_urls_return_false(self, url):
        """Geçersiz URL'ler False dönmeli."""
        assert is_valid_url(url) is False, f"Geçersiz URL kabul edildi: {url}"

    def test_http_prefix_accepted(self):
        """http:// ile başlayan URL kabul edilmeli."""
        assert is_valid_url("http://example.com") is True

    def test_https_prefix_accepted(self):
        """https:// ile başlayan URL kabul edilmeli."""
        assert is_valid_url("https://example.com") is True

    def test_no_prefix_rejected(self):
        """Protokol olmayan URL reddedilmeli."""
        assert is_valid_url("example.com") is False

    def test_localhost_with_port_accepted(self):
        """localhost:port formatı kabul edilmeli."""
        assert is_valid_url("http://localhost:8000") is True

    def test_localhost_accepted(self):
        """Sadece localhost kabul edilmeli."""
        assert is_valid_url("http://localhost") is True
