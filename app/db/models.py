"""
Modelos ORM de SQLAlchemy para la base de datos SQLite.

Tres entidades principales:
  - Upload:   registro de cada CSV subido al sistema
  - Forecast: resultado de cada ejecución del pipeline
  - Insight:  resultado de cada ejecución del agente LangGraph
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, relationship


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _new_uuid() -> str:
    return str(uuid.uuid4())


class Base(DeclarativeBase):
    pass


class Upload(Base):
    """Registro de cada CSV subido via POST /upload."""

    __tablename__ = "uploads"

    id = Column(String, primary_key=True, default=_new_uuid)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    # Metadatos del fichero
    filename = Column(String, nullable=False)
    row_count = Column(Integer, nullable=False)
    date_min = Column(String, nullable=True)   # ISO date string
    date_max = Column(String, nullable=True)
    sales_mean = Column(Float, nullable=True)
    sales_std = Column(Float, nullable=True)

    # Ruta donde se persisten los datos procesados
    data_path = Column(String, nullable=True)

    # Relaciones
    forecasts = relationship("Forecast", back_populates="upload", cascade="all, delete-orphan")


class Forecast(Base):
    """Resultado de cada ejecución del pipeline POST /forecast."""

    __tablename__ = "forecasts"

    id = Column(String, primary_key=True, default=_new_uuid)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    upload_id = Column(String, ForeignKey("uploads.id"), nullable=False)

    # Modelo ganador
    best_model = Column(String, nullable=True)   # "prophet" | "lightgbm"

    # Métricas Prophet
    prophet_mae = Column(Float, nullable=True)
    prophet_mape = Column(Float, nullable=True)
    prophet_rmse = Column(Float, nullable=True)

    # Métricas LightGBM
    lgbm_mae = Column(Float, nullable=True)
    lgbm_mape = Column(Float, nullable=True)
    lgbm_rmse = Column(Float, nullable=True)

    # Predicciones serializadas como JSON string
    predictions_json = Column(Text, nullable=True)

    # Drift
    drift_detected = Column(Boolean, nullable=True)
    drift_report_path = Column(String, nullable=True)

    # Relaciones
    upload = relationship("Upload", back_populates="forecasts")
    insights = relationship("Insight", back_populates="forecast", cascade="all, delete-orphan")


class Insight(Base):
    """Resultado de cada ejecución del agente POST /insight."""

    __tablename__ = "insights"

    id = Column(String, primary_key=True, default=_new_uuid)
    created_at = Column(DateTime, default=_utcnow, nullable=False)

    forecast_id = Column(String, ForeignKey("forecasts.id"), nullable=False)

    # Texto del insight generado
    insight_text = Column(Text, nullable=True)

    # Trazabilidad del agente (JSON serializado)
    trace_json = Column(Text, nullable=True)

    # LLM utilizado
    llm_model = Column(String, nullable=True)
    tokens_used = Column(Integer, nullable=True)

    # Relaciones
    forecast = relationship("Forecast", back_populates="insights")
