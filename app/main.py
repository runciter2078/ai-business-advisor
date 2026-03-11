"""
AI Business Advisor — Aplicación principal FastAPI.

Punto de entrada del servicio. Registra routers, configura middleware,
inicializa la base de datos y expone el health check.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import health, upload, forecast, insight
from app.core.config import settings
from app.db.session import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida de la aplicación: startup y shutdown."""
    # Startup: inicializar base de datos
    await init_db()
    yield
    # Shutdown: aquí irían cierres de conexiones si fueran necesarios


app = FastAPI(
    title="AI Business Advisor",
    description=(
        "Servicio de forecasting semanal de ventas para pequeños negocios de hostelería. "
        "Pipeline ML con Prophet y LightGBM, drift monitoring con Evidently "
        "y capa de interpretación agentic con LangGraph."
    ),
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — permisivo en desarrollo, restringir en producción
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.app_env == "development" else settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(health.router, tags=["Health"])
app.include_router(upload.router, prefix="/upload", tags=["Data"])
app.include_router(forecast.router, prefix="/forecast", tags=["Forecast"])
app.include_router(insight.router, prefix="/insight", tags=["Agent"])
