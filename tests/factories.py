"""
factories.py — Factory Boy + Faker ile Test Verisi Üretimi

Bu dosya ne işe yarar?
  Gerçekçi test verisi otomatik üretmek için "fabrika" sınıfları tanımlar.
  
Factory Boy nedir?
  Django/SQLAlchemy modelleri için test verisi üretme kütüphanesi.
  Her çağrıda yeni, benzersiz veriler üretir.
  
Faker nedir?
  Sahte ama gerçekçi veriler üretir: isim, email, URL, tarih vb.
  
Neden kullanıyoruz?
  Manuel test verisi yazmak yerine (url1, url2, url3 gibi),
  fabrikalar otomatik gerçekçi veri üretir.
  
Örnek kullanım:
  url = URLFactory()  → random URL kaydı
  url = URLFactory(click_count=10)  → click_count=10 olan URL
  urls = URLFactory.create_batch(5)  → 5 adet URL
"""

import factory
from faker import Faker
from factory.alchemy import SQLAlchemyModelFactory

from src.models import URL, Click

fake = Faker("tr_TR")  # Türkçe locale — Türk URL'leri üretebilir


class URLFactory(SQLAlchemyModelFactory):
    """
    URL modeli için fabrika.
    
    Her çağrıda otomatik olarak:
    - Benzersiz short_code üretir (ör: "xK2mN9")
    - Gerçek bir web adresi üretir
    - click_count 0 ile 100 arasında rastgele değer alır
    """

    class Meta:
        model = URL
        sqlalchemy_session = None  # conftest'te set edilir
        sqlalchemy_session_persistence = "commit"

    # sequence() — her çağrıda n artar: url001, url002, ...
    short_code = factory.Sequence(lambda n: f"url{n:03d}")
    
    # fake.url() → "https://www.example.com/path"
    original_url = factory.LazyAttribute(lambda _: fake.url(schemes=["https"]))
    
    # randint ile 0-50 arası tıklama
    click_count = factory.LazyAttribute(lambda _: fake.random_int(min=0, max=50))


class ClickFactory(SQLAlchemyModelFactory):
    """
    Click modeli için fabrika.
    
    url_id verilen URL'ye tıklama kaydı oluşturur.
    """

    class Meta:
        model = Click
        sqlalchemy_session = None
        sqlalchemy_session_persistence = "commit"

    url = factory.SubFactory(URLFactory)


def configure_factories(db_session):
    """
    Fabrikaları veritabanı session'ı ile yapılandırır.
    
    conftest.py'deki fixture'larda çağrılır.
    Böylece factory'ler doğru DB'ye kayıt eder.
    """
    URLFactory._meta.sqlalchemy_session = db_session
    ClickFactory._meta.sqlalchemy_session = db_session
