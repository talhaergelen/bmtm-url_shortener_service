"""
test_api.py — FastAPI Endpoint Integration Testleri

Bu dosya ne işe yarar?
  Tüm API endpoint'lerini HTTP seviyesinde test eder.
  
Integration Test nedir?
  Birden fazla katmanın birlikte çalışmasını test eder.
  API → CRUD → Veritabanı zinciri bir bütün olarak test edilir.
  
  Unit test: "Bu fonksiyon doğru çalışıyor mu?"
  Integration test: "Tüm parçalar birlikte doğru çalışıyor mu?"
  
HTTP Durum Kodları:
  200 → OK (başarılı)
  201 → Created (yeni kayıt oluşturuldu)
  301 → Moved Permanently (redirect)
  404 → Not Found (bulunamadı)
  422 → Unprocessable Entity (geçersiz veri)
"""

import pytest


# ─────────────────────────────────────────────────────────
# HEALTH CHECK ENDPOİNT
# ─────────────────────────────────────────────────────────

class TestHealthCheck:
    """GET /health endpoint testleri."""

    def test_health_returns_200(self, client):
        """
        Sağlık endpoint'i 200 dönmeli.
        
        client: conftest.py'deki FastAPI test istemcisi.
        client.get("/health") → GET /health isteği simüle eder.
        """
        response = client.get("/health")
        assert response.status_code == 200

    def test_health_returns_healthy_status(self, client):
        """Yanıt 'healthy' durumu içermeli."""
        response = client.get("/health")
        data = response.json()
        
        assert data["status"] == "healthy"

    def test_health_returns_version(self, client):
        """Yanıt versiyon bilgisi içermeli."""
        response = client.get("/health")
        data = response.json()
        
        assert "version" in data
        assert data["version"] == "1.0.0"

    def test_health_returns_message(self, client):
        """Yanıt mesaj alanı içermeli."""
        response = client.get("/health")
        data = response.json()
        
        assert "message" in data


# ─────────────────────────────────────────────────────────
# SHORTEN ENDPOİNT — URL Kısaltma
# ─────────────────────────────────────────────────────────

class TestShortenEndpoint:
    """POST /shorten endpoint testleri."""

    def test_creates_short_url_successfully(self, client):
        """Geçerli URL ile POST /shorten → 201 Created dönmeli."""
        payload = {"original_url": "https://google.com"}
        
        response = client.post("/shorten", json=payload)
        
        assert response.status_code == 201

    def test_response_contains_short_code(self, client):
        """Yanıt short_code içermeli."""
        response = client.post(
            "/shorten",
            json={"original_url": "https://github.com"}
        )
        data = response.json()
        
        assert "short_code" in data
        assert len(data["short_code"]) == 6

    def test_response_contains_short_url(self, client):
        """Yanıt tam kısa URL (short_url) içermeli."""
        response = client.post(
            "/shorten",
            json={"original_url": "https://python.org"}
        )
        data = response.json()
        
        assert "short_url" in data
        assert data["short_url"].startswith("http")

    def test_response_contains_original_url(self, client):
        """Yanıt orijinal URL'yi içermeli."""
        original = "https://stackoverflow.com"
        response = client.post("/shorten", json={"original_url": original})
        data = response.json()
        
        assert data["original_url"] == original

    def test_click_count_starts_at_zero(self, client):
        """Yeni URL'nin tıklama sayısı 0 olmalı."""
        response = client.post(
            "/shorten",
            json={"original_url": "https://example.com"}
        )
        data = response.json()
        
        assert data["click_count"] == 0

    def test_rejects_invalid_url_no_protocol(self, client):
        """
        http:// veya https:// olmayan URL reddedilmeli.
        422 Unprocessable Entity dönmeli.
        """
        response = client.post(
            "/shorten",
            json={"original_url": "google.com"}
        )
        
        assert response.status_code in [400, 422]

    def test_rejects_empty_url(self, client):
        """Boş URL reddedilmeli."""
        response = client.post(
            "/shorten",
            json={"original_url": ""}
        )
        
        assert response.status_code in [400, 422]

    def test_rejects_non_http_protocol(self, client):
        """ftp:// gibi desteklenmeyen protokoller reddedilmeli."""
        response = client.post(
            "/shorten",
            json={"original_url": "ftp://example.com"}
        )
        
        assert response.status_code in [400, 422]

    def test_two_different_urls_get_different_codes(self, client):
        """İki farklı URL farklı short_code almalı."""
        r1 = client.post("/shorten", json={"original_url": "https://site1.com"})
        r2 = client.post("/shorten", json={"original_url": "https://site2.com"})
        
        assert r1.json()["short_code"] != r2.json()["short_code"]


# ─────────────────────────────────────────────────────────
# REDIRECT ENDPOİNT
# ─────────────────────────────────────────────────────────

class TestRedirectEndpoint:
    """GET /{short_code} endpoint testleri."""

    def test_redirects_to_original_url(self, client):
        """
        Geçerli kısa kod → orijinal URL'ye yönlendirme.
        
        allow_redirects=False: Redirect'i takip etme, sadece yanıtı al.
        """
        # Önce URL oluştur
        response = client.post(
            "/shorten",
            json={"original_url": "https://google.com"}
        )
        short_code = response.json()["short_code"]
        
        # Redirect isteği gönder
        redirect_response = client.get(f"/{short_code}", follow_redirects=False)
        
        assert redirect_response.status_code == 301
        assert redirect_response.headers["location"] == "https://google.com"

    def test_returns_404_for_unknown_code(self, client):
        """Olmayan short_code → 404 Not Found."""
        response = client.get("/yok999", follow_redirects=False)
        
        assert response.status_code == 404

    def test_click_count_increases_after_redirect(self, client):
        """Redirect sonrası tıklama sayısı artmalı."""
        # URL oluştur
        create_response = client.post(
            "/shorten",
            json={"original_url": "https://example.com"}
        )
        short_code = create_response.json()["short_code"]
        
        # 2 kez redirect yap
        client.get(f"/{short_code}", follow_redirects=False)
        client.get(f"/{short_code}", follow_redirects=False)
        
        # İstatistikleri kontrol et
        stats_response = client.get(f"/stats/{short_code}")
        assert stats_response.json()["click_count"] == 2


# ─────────────────────────────────────────────────────────
# LIST ENDPOİNT
# ─────────────────────────────────────────────────────────

class TestListEndpoint:
    """GET /urls/list endpoint testleri."""

    def test_returns_empty_list_when_no_urls(self, client):
        """Hiç URL yokken boş liste dönmeli."""
        response = client.get("/urls/list")
        
        assert response.status_code == 200
        assert response.json() == []

    def test_returns_created_urls(self, client):
        """Oluşturulan URL'ler listede görünmeli."""
        client.post("/shorten", json={"original_url": "https://url1.com"})
        client.post("/shorten", json={"original_url": "https://url2.com"})
        
        response = client.get("/urls/list")
        data = response.json()
        
        assert len(data) == 2

    def test_pagination_limit_parameter(self, client):
        """limit parametresi çalışmalı."""
        # 5 URL oluştur
        for i in range(5):
            client.post("/shorten", json={"original_url": f"https://site{i}.com"})
        
        response = client.get("/urls/list?limit=3")
        assert len(response.json()) == 3

    def test_pagination_skip_parameter(self, client):
        """skip parametresi çalışmalı."""
        for i in range(5):
            client.post("/shorten", json={"original_url": f"https://site{i}.com"})
        
        response = client.get("/urls/list?skip=3&limit=100")
        assert len(response.json()) == 2  # 5-3=2


# ─────────────────────────────────────────────────────────
# STATS ENDPOİNT
# ─────────────────────────────────────────────────────────

class TestStatsEndpoint:
    """GET /stats/{short_code} endpoint testleri."""

    def test_returns_stats_for_existing_url(self, client):
        """Var olan URL'nin istatistikleri döndürülmeli."""
        create_response = client.post(
            "/shorten",
            json={"original_url": "https://google.com"}
        )
        short_code = create_response.json()["short_code"]
        
        stats_response = client.get(f"/stats/{short_code}")
        
        assert stats_response.status_code == 200

    def test_stats_contains_required_fields(self, client):
        """İstatistik yanıtı gerekli alanları içermeli."""
        create_response = client.post(
            "/shorten",
            json={"original_url": "https://example.com"}
        )
        short_code = create_response.json()["short_code"]
        
        stats = client.get(f"/stats/{short_code}").json()
        
        assert "short_code" in stats
        assert "original_url" in stats
        assert "click_count" in stats
        assert "created_at" in stats

    def test_stats_returns_404_for_unknown(self, client):
        """Olmayan URL istatistik endpoint'i 404 dönmeli."""
        response = client.get("/stats/yok999")
        assert response.status_code == 404


# ─────────────────────────────────────────────────────────
# DELETE ENDPOİNT
# ─────────────────────────────────────────────────────────

class TestDeleteEndpoint:
    """DELETE /urls/{short_code} endpoint testleri."""

    def test_deletes_existing_url(self, client):
        """Var olan URL silinebilmeli."""
        create_response = client.post(
            "/shorten",
            json={"original_url": "https://todelete.com"}
        )
        short_code = create_response.json()["short_code"]
        
        delete_response = client.delete(f"/urls/{short_code}")
        
        assert delete_response.status_code == 200

    def test_url_not_accessible_after_deletion(self, client):
        """Silinen URL artık erişilebilir olmamalı."""
        create_response = client.post(
            "/shorten",
            json={"original_url": "https://todelete2.com"}
        )
        short_code = create_response.json()["short_code"]
        
        # Sil
        client.delete(f"/urls/{short_code}")
        
        # Tekrar erişmeye çalış
        response = client.get(f"/{short_code}", follow_redirects=False)
        assert response.status_code == 404

    def test_delete_nonexistent_url_returns_404(self, client):
        """Olmayan URL silme → 404 dönmeli."""
        response = client.delete("/urls/yok999")
        assert response.status_code == 404


# ─────────────────────────────────────────────────────────
# FACTORY BOY İLE ENTEGRASYON TESTLERİ
# Şartname: "Factory Boy + Faker ile en az 1 model factory"
# ─────────────────────────────────────────────────────────

class TestWithFactoryBoy:
    """
    Factory Boy kullanarak oluşturulan test verileriyle entegrasyon testleri.
    
    URLFactory ve ClickFactory gerçekçi, rastgele test verisi üretir.
    Bu yaklaşım birim test verilerini daha güvenilir ve bakımı kolay yapar.
    """

    def test_factory_creates_url_with_valid_short_code(self, factory_url, client):
        """Factory ile oluşturulan URL veritabanında doğrulanabilmeli."""
        # factory_url fixture'ı zaten DB'ye kaydetmiş
        response = client.get(f"/urls/{factory_url.short_code}")
        assert response.status_code == 200
        assert response.json()["short_code"] == factory_url.short_code

    def test_factory_url_has_realistic_original_url(self, factory_url):
        """Factory Faker ile gerçekçi URL üretmeli (https:// ile başlamalı)."""
        assert factory_url.original_url.startswith("https://")

    def test_factory_batch_creates_multiple_urls(self, factory_urls, client):
        """Factory batch ile 5 URL oluşturulabilmeli."""
        assert len(factory_urls) == 5
        response = client.get("/urls/list?limit=100")
        assert len(response.json()) >= 5

    def test_factory_url_click_count_in_valid_range(self, factory_url):
        """Factory'nin ürettiği click_count 0-50 aralığında olmalı."""
        assert 0 <= factory_url.click_count <= 50

    def test_factory_each_url_has_unique_short_code(self, factory_urls):
        """Factory batch ile üretilen her URL benzersiz short_code'a sahip olmalı."""
        codes = [u.short_code for u in factory_urls]
        assert len(codes) == len(set(codes))  # Duplicate yok

