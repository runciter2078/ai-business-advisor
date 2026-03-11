"""
Endpoint GET /health

Health check del servicio. Usado por CI/CD, load balancers y Azure Container Apps.
Devuelve estado del servicio y versión.
"""

from datetime import datetime, timezone

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    version: str
    timestamp: str
    environment: str


@router.get("/health", response_model=HealthResponse, summary="Health check")
async def health_check() -> HealthResponse:
    """
    Verifica que el servicio está operativo.

    Retorna:
      - **status**: "ok" si el servicio está funcionando
      - **version**: versión semántica del servicio
      - **timestamp**: ISO 8601 UTC del momento de la consulta
      - **environment**: entorno de ejecución (development | production)
    """
    from app.core.config import settings

    return HealthResponse(
        status="ok",
        version="1.0.0",
        timestamp=datetime.now(timezone.utc).isoformat(),
        environment=settings.app_env,
    )
