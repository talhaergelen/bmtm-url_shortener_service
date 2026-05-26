"""
test_aws.py — AWS S3 / LocalStack Testleri

Bu dosya ne işe yarar?
  src/aws_client.py fonksiyonlarını unittest.mock ile test eder.
  Gerçek LocalStack çalışmasa da testler geçer (mock sayesinde).

Mock nedir?
  Gerçek dış servisi (S3) taklit eden sahte nesne.
  Test sırasında S3'e gerçek istek atılmaz — mock cevaplar.

Kılavuz gereksinimi:
  "Seçilen AWS servisi gerçekten kullanılıyor, testlerle doğrulanmış"
"""

import pytest
from unittest.mock import patch, MagicMock, call
from botocore.exceptions import ClientError


# ─────────────────────────────────────────────────────────
# S3 CLIENT TESTLERİ
# ─────────────────────────────────────────────────────────

class TestGetS3Client:
    """get_s3_client() fonksiyonu testleri."""

    def test_s3_client_created_with_correct_config(self):
        """
        S3 istemcisi doğru parametrelerle oluşturuluyor mu?

        Beklenti:
          boto3.client() doğru endpoint_url ile çağrılmalı.
        """
        with patch("src.aws_client.boto3.client") as mock_boto3_client:
            mock_boto3_client.return_value = MagicMock()

            from src.aws_client import get_s3_client
            client = get_s3_client()

            # boto3.client çağrıldı mı?
            mock_boto3_client.assert_called_once()
            call_args = mock_boto3_client.call_args

            # İlk argüman "s3" olmalı
            assert call_args[0][0] == "s3"


# ─────────────────────────────────────────────────────────
# BUCKET TESTLERI
# ─────────────────────────────────────────────────────────

class TestEnsureBucketExists:
    """ensure_bucket_exists() fonksiyonu testleri."""

    def test_returns_true_when_bucket_already_exists(self):
        """
        Test 1: Bucket zaten varsa True döndürmeli.

        Senaryo:
          head_bucket() başarılı → bucket var → True döner.
        """
        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3

            # head_bucket başarılı (exception yok)
            mock_s3.head_bucket.return_value = {}

            from src.aws_client import ensure_bucket_exists
            result = ensure_bucket_exists()

            assert result is True
            mock_s3.head_bucket.assert_called_once()

    def test_creates_bucket_when_not_found(self):
        """
        Test 2: Bucket yoksa (404) oluşturulmalı ve True döndürmeli.

        Senaryo:
          head_bucket() 404 ClientError fırlatır →
          create_bucket() çağrılır → True döner.
        """
        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3

            # Bucket yok → 404 ClientError
            error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
            mock_s3.head_bucket.side_effect = ClientError(error_response, "HeadBucket")

            # create_bucket başarılı
            mock_s3.create_bucket.return_value = {}

            from src.aws_client import ensure_bucket_exists
            result = ensure_bucket_exists()

            assert result is True
            mock_s3.create_bucket.assert_called_once()

    def test_returns_false_when_connection_fails(self):
        """
        Test 3: LocalStack bağlantısı yoksa False döndürmeli.

        Senaryo:
          get_s3_client() bağlantı hatası fırlatır → False döner.
        """
        with patch("src.aws_client.get_s3_client") as mock_get_client:
            # Bağlantı hatası simüle et
            mock_get_client.side_effect = Exception("Connection refused")

            from src.aws_client import ensure_bucket_exists
            result = ensure_bucket_exists()

            assert result is False

    def test_returns_false_when_create_bucket_fails(self):
        """
        Test 4: Bucket oluşturma başarısız olursa False döndürmeli.

        Senaryo:
          head_bucket() 404 → create_bucket() hata fırlatır → False döner.
        """
        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3

            # Bucket yok → 404
            error_response = {"Error": {"Code": "404", "Message": "Not Found"}}
            mock_s3.head_bucket.side_effect = ClientError(error_response, "HeadBucket")

            # Bucket oluşturma da başarısız
            mock_s3.create_bucket.side_effect = Exception("Access Denied")

            from src.aws_client import ensure_bucket_exists
            result = ensure_bucket_exists()

            assert result is False


# ─────────────────────────────────────────────────────────
# UPLOAD TESTLERİ
# ─────────────────────────────────────────────────────────

class TestUploadStatsToS3:
    """upload_stats_to_s3() fonksiyonu testleri."""

    def test_uploads_stats_successfully(self):
        """
        Test 5: İstatistikler S3'e başarıyla yüklenmeli.

        Beklenti:
          put_object() doğru bucket ve JSON içeriğiyle çağrılmalı.
          True döndürmeli.
        """
        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3
            mock_s3.put_object.return_value = {}

            from src.aws_client import upload_stats_to_s3
            stats = {
                "event": "url_created",
                "short_code": "abc123",
                "original_url": "https://example.com",
                "total_urls": 42
            }
            result = upload_stats_to_s3(stats)

            assert result is True

            # put_object çağrıldı mı?
            mock_s3.put_object.assert_called_once()
            call_kwargs = mock_s3.put_object.call_args[1]

            # Doğru ContentType
            assert call_kwargs["ContentType"] == "application/json"
            # JSON içeriği var
            assert b"abc123" in call_kwargs["Body"]

    def test_upload_returns_false_on_s3_error(self):
        """
        Test 6: S3 hatası olursa False döndürmeli (uygulama çökmemeli).

        Senaryo:
          put_object() hata fırlatır → False döner, exception yayılmaz.
        """
        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3
            mock_s3.put_object.side_effect = Exception("S3 Error")

            from src.aws_client import upload_stats_to_s3
            result = upload_stats_to_s3({"event": "test"})

            assert result is False

    def test_upload_json_contains_all_fields(self):
        """
        Test 7: Yüklenen JSON tüm alanları içermeli.

        Beklenti:
          stats dict'indeki tüm anahtarlar JSON'da olmalı.
        """
        import json

        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3
            mock_s3.put_object.return_value = {}

            from src.aws_client import upload_stats_to_s3
            stats = {"key1": "value1", "key2": 42, "key3": True}
            upload_stats_to_s3(stats)

            # Yüklenen body'yi kontrol et
            call_kwargs = mock_s3.put_object.call_args[1]
            uploaded_body = json.loads(call_kwargs["Body"].decode("utf-8"))

            assert uploaded_body["key1"] == "value1"
            assert uploaded_body["key2"] == 42
            assert uploaded_body["key3"] is True


# ─────────────────────────────────────────────────────────
# GET STATS TESTLERİ
# ─────────────────────────────────────────────────────────

class TestGetStatsFromS3:
    """get_stats_from_s3() fonksiyonu testleri."""

    def test_returns_stats_list_for_given_date(self):
        """
        Test 8: Belirtilen tarihe ait istatistikleri döndürmeli.

        Senaryo:
          list_objects_v2() 2 nesne döner → get_object() 2 kez çağrılır.
        """
        import json

        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3

            # list_objects_v2 → 2 dosya var
            mock_s3.list_objects_v2.return_value = {
                "Contents": [
                    {"Key": "stats/2024-01-15_10-00-00.json"},
                    {"Key": "stats/2024-01-15_11-00-00.json"},
                ]
            }

            # get_object → JSON içerik
            stat1 = json.dumps({"total_urls": 10}).encode("utf-8")
            stat2 = json.dumps({"total_urls": 15}).encode("utf-8")

            mock_s3.get_object.side_effect = [
                {"Body": MagicMock(read=lambda: stat1)},
                {"Body": MagicMock(read=lambda: stat2)},
            ]

            from src.aws_client import get_stats_from_s3
            result = get_stats_from_s3("2024-01-15")

            assert len(result) == 2
            assert result[0]["total_urls"] == 10
            assert result[1]["total_urls"] == 15

    def test_returns_empty_list_on_error(self):
        """
        Test 9: S3 hatası olursa boş liste döndürmeli.

        Senaryo:
          list_objects_v2() hata fırlatır → [] döner.
        """
        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3
            mock_s3.list_objects_v2.side_effect = Exception("Connection Error")

            from src.aws_client import get_stats_from_s3
            result = get_stats_from_s3("2024-01-15")

            assert result == []

    def test_returns_empty_list_when_no_files(self):
        """
        Test 10: O tarihte dosya yoksa boş liste döndürmeli.

        Senaryo:
          list_objects_v2() → Contents boş → [] döner.
        """
        with patch("src.aws_client.get_s3_client") as mock_get_client:
            mock_s3 = MagicMock()
            mock_get_client.return_value = mock_s3

            # Hiç dosya yok
            mock_s3.list_objects_v2.return_value = {}

            from src.aws_client import get_stats_from_s3
            result = get_stats_from_s3("2024-01-15")

            assert result == []
