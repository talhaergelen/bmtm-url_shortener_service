"""
shortener.py — URL Kısaltma Algoritması

Bu dosya ne işe yarar?
  Uzun bir URL'den kısa bir kod (short_code) üretir.
  Örnek: "https://google.com/çok/uzun/bir/link" → "abc123"

Nasıl çalışır?
  Python'un "secrets" kütüphanesi ile rastgele karakterler seçeriz.
  Karakterler: harfler + rakamlar (a-z, A-Z, 0-9)
  Uzunluk: 6 karakter (64^6 = 68 milyar farklı kombinasyon!)

URL Doğrulama nedir?
  Kullanıcı bize bir URL verdiğinde "bu gerçekten URL mi?" diye kontrol ederiz.
  "merhaba" gibi bir şey URL değil, geçersiz sayarız.
"""

import secrets
import string
import re
from sqlalchemy.orm import Session
from . import models


# Kısa kodda kullanılacak karakterler: a-z, A-Z, 0-9
ALPHABET = string.ascii_letters + string.digits  # 62 karakter
CODE_LENGTH = 6  # 6 karakterlik kısa kod


def generate_short_code() -> str:
    """
    Rastgele 6 karakterlik kısa kod üretir.
    
    Örnek çıktılar: "xK2mN9", "aBc123", "Zy7pQr"
    
    secrets.choice() neden kullandık?
      random.choice() tahmin edilebilir olabilir.
      secrets.choice() kriptografik olarak güvenli rastgelelik kullanır.
    """
    return "".join(secrets.choice(ALPHABET) for _ in range(CODE_LENGTH))


def generate_unique_short_code(db: Session) -> str:
    """
    Veritabanında henüz kullanılmayan bir kısa kod üretir.
    
    Neden benzersizlik kontrolü?
      İki farklı URL aynı kısa koda sahip olursa, hangi URL'ye gideceğimizi bilemeyiz!
      Bu yüzden her ürettiğimiz kodu veritabanında kontrol ederiz.
    
    Ne kadar deneme yapar?
      Sonsuz döngü ama teorik olarak 62^6 = 56 milyar ihtimal var,
      dolması neredeyse imkansız.
    """
    while True:
        code = generate_short_code()
        # Bu kod daha önce kullanılmış mı?
        existing = db.query(models.URL).filter(models.URL.short_code == code).first()
        if not existing:
            return code  # Kullanılmamış, bu kodu kullan!
        # Zaten kullanılmış, yeni kod dene...


def is_valid_url(url: str) -> bool:
    """
    Verilen string'in geçerli bir URL olup olmadığını kontrol eder.
    
    Geçerli: "https://google.com", "http://example.com/path?q=1"
    Geçersiz: "merhaba", "google", "ftp://..."
    
    Regex nedir?
      "Regular Expression" — metin içinde desen aramak için kullanılır.
      Örneğin: "http veya https ile başlayıp, domain adı ve devamı var mı?"
    """
    # URL formatı için regex deseni
    url_pattern = re.compile(
        r'^https?://'           # http:// veya https:// ile başlamalı
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'           # veya localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # veya IP adresi
        r'(?::\d+)?'            # opsiyonel port numarası (:8080 gibi)
        r'(?:/?|[/?]\S+)$',    # path, query string vb.
        re.IGNORECASE
    )
    return bool(url_pattern.match(url))
