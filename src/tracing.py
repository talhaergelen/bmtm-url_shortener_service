"""
tracing.py — OpenTelemetry Distributed Tracing (Bonus +5 puan)

Nedir?
  Uygulamadaki her HTTP isteği, DB sorgusu izlenir.
  Jaeger UI'da görselleştirilir: http://localhost:16686

Kullanım:
  1. setup_tracing()   → Provider'ı başlat (app oluşmadan önce)
  2. instrument_fastapi(app) → app oluştuktan hemen sonra çağır
"""

import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource, SERVICE_NAME

logger = logging.getLogger(__name__)


def setup_tracing(db_engine=None) -> trace.Tracer:
    """
    OpenTelemetry tracing'i başlatır.
    Lifespan DIŞINDA çağrılmalı (app oluşmadan önce).
    """
    resource = Resource(attributes={
        SERVICE_NAME: "url-shortener-service",
        "service.version": "1.0.0",
        "deployment.environment": "development",
    })

    provider = TracerProvider(resource=resource)

    # OTLP (Jaeger) dene, yoksa Console'a yaz
    try:
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        exporter = OTLPSpanExporter(endpoint="http://localhost:4318/v1/traces")
        provider.add_span_processor(BatchSpanProcessor(exporter))
        logger.info("✅ OTLP/Jaeger exporter aktif")
    except Exception:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
        logger.info("📺 Console span exporter aktif (Jaeger yok)")

    # SQLAlchemy instrumentation
    if db_engine is not None:
        try:
            from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
            SQLAlchemyInstrumentor().instrument(engine=db_engine)
            logger.info("✅ SQLAlchemy OTel instrumentation aktif")
        except Exception as e:
            logger.warning(f"⚠️  SQLAlchemy instrumentation başarısız: {e}")

    trace.set_tracer_provider(provider)
    logger.info("🔭 OpenTelemetry tracing başlatıldı")
    return trace.get_tracer("url-shortener")


def instrument_fastapi(app) -> None:
    """
    FastAPI'yi OTel ile instrument eder.
    App yaratıldıktan hemen sonra, lifespan BAŞLAMADAN çağrılmalı.
    """
    try:
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        FastAPIInstrumentor.instrument_app(app)
        logger.info("✅ FastAPI OTel instrumentation aktif")
    except Exception as e:
        logger.warning(f"⚠️  FastAPI instrumentation başarısız: {e}")


def get_tracer() -> trace.Tracer:
    """Mevcut tracer'ı döndürür."""
    return trace.get_tracer("url-shortener")
