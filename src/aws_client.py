"""
aws_client.py — AWS S3 İstemcisi (LocalStack ile)

Bu dosya ne işe yarar?
  URL istatistiklerini AWS S3'e yazar.
  
AWS S3 nedir?
  Amazon'un bulut depolama servisi (Simple Storage Service).
  Google Drive'a benzer ama programcılar için.
  Dosya (JSON, resim, video vb.) saklayabiliriz.

LocalStack nedir?
  AWS'yi bilgisayarında taklit eden (emüle eden) bir araç.
  Gerçek AWS hesabı ve para gerekmez!
  Docker ile çalışır, tüm AWS servisleri yerel makinende çalışır.

Bu dosyada ne yapıyoruz?
  Her gün URL istatistiklerini JSON olarak S3'e yüklüyoruz.
  "Bugün kaç URL kısaltıldı, kaç tıklama oldu?" gibi verileri saklıyoruz.
"""

import boto3
import json
import logging
from typing import List
from datetime import datetime
from botocore.exceptions import ClientError, EndpointResolutionError
from .config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


def get_s3_client():
    """
    S3 istemcisi oluşturur.
    
    endpoint_url neden var?
      Normalde AWS'ye bağlanır. 
      endpoint_url=http://localhost:4566 ile LocalStack'e bağlanır.
    """
    from botocore.config import Config
    return boto3.client(
        "s3",
        endpoint_url=settings.aws_endpoint_url,
        aws_access_key_id=settings.aws_access_key_id,
        aws_secret_access_key=settings.aws_secret_access_key,
        region_name=settings.aws_default_region,
        config=Config(
            connect_timeout=2,   # 2 saniyede bağlanamazsa vazgeç
            read_timeout=2,
            retries={"max_attempts": 1}
        )
    )


def ensure_bucket_exists() -> bool:
    """
    S3 bucket (klasör gibi) yoksa oluşturur.
    
    Bucket nedir?
      S3'te dosyaların saklandığı "konteyner".
      Google Drive'daki bir klasör gibi düşünebilirsin.
    
    Returns:
        True → Başarılı
        False → LocalStack çalışmıyor (hata)
    """
    try:
        s3 = get_s3_client()
        # Bucket var mı?
        s3.head_bucket(Bucket=settings.s3_bucket_name)
        logger.info(f"S3 bucket mevcut: {settings.s3_bucket_name}")
        return True
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            # Bucket yok, oluştur
            try:
                s3 = get_s3_client()
                s3.create_bucket(Bucket=settings.s3_bucket_name)
                logger.info(f"S3 bucket oluşturuldu: {settings.s3_bucket_name}")
                return True
            except Exception as create_err:
                logger.warning(f"S3 bucket oluşturulamadı: {create_err}")
                return False
    except Exception as e:
        logger.warning(f"LocalStack bağlantısı yok, S3 devre dışı: {e}")
        return False


def upload_stats_to_s3(stats: dict) -> bool:
    """
    İstatistikleri JSON olarak S3'e yükler.
    
    Args:
        stats: Yüklenecek istatistik verisi (Python dict)
    
    Returns:
        True → Başarıyla yüklendi
        False → Hata oluştu (LocalStack çalışmıyor olabilir)
    
    Örnek stats:
    {
      "date": "2024-01-15",
      "total_urls": 42,
      "total_clicks": 150,
      "most_clicked": "abc123"
    }
    """
    try:
        s3 = get_s3_client()

        # Dosya adı: tarih/saat bazlı (her istatistik ayrı dosya)
        timestamp = datetime.utcnow().strftime("%Y-%m-%d_%H-%M-%S")
        file_key = f"stats/{timestamp}.json"

        # Python dict → JSON string
        json_data = json.dumps(stats, indent=2, default=str)

        # S3'e yükle
        s3.put_object(
            Bucket=settings.s3_bucket_name,
            Key=file_key,
            Body=json_data.encode("utf-8"),
            ContentType="application/json"
        )

        logger.info(f"İstatistikler S3'e yüklendi: s3://{settings.s3_bucket_name}/{file_key}")
        return True

    except Exception as e:
        logger.warning(f"S3 yükleme başarısız (LocalStack çalışmıyor olabilir): {e}")
        return False


def get_stats_from_s3(date: str) -> List[dict]:
    """
    Belirli bir tarihe ait istatistikleri S3'ten çeker.
    
    Args:
        date: "2024-01-15" formatında tarih
    
    Returns:
        İstatistik listesi
    """
    try:
        s3 = get_s3_client()

        # O tarihe ait tüm dosyaları listele
        response = s3.list_objects_v2(
            Bucket=settings.s3_bucket_name,
            Prefix=f"stats/{date}"
        )

        stats_list = []
        for obj in response.get("Contents", []):
            # Her dosyayı indir ve parse et
            file_response = s3.get_object(
                Bucket=settings.s3_bucket_name,
                Key=obj["Key"]
            )
            content = file_response["Body"].read().decode("utf-8")
            stats_list.append(json.loads(content))

        return stats_list

    except Exception as e:
        logger.warning(f"S3'ten veri çekilemedi: {e}")
        return []
