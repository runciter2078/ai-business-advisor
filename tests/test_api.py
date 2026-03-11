"""
Tests de la API — Semana 1.

Cubre el endpoint GET /health. Los tests de /upload, /forecast e /insight
se añaden en las semanas correspondientes.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def client():
    """Cliente HTTP async para tests de la API FastAPI."""
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac


class TestHealth:
    async def test_health_returns_200(self, client):
        response = await client.get("/health")
        assert response.status_code == 200

    async def test_health_response_schema(self, client):
        response = await client.get("/health")
        data = response.json()
        assert data["status"] == "ok"
        assert "version" in data
        assert "timestamp" in data
        assert "environment" in data

    async def test_health_version_format(self, client):
        response = await client.get("/health")
        version = response.json()["version"]
        parts = version.split(".")
        assert len(parts) == 3
        assert all(p.isdigit() for p in parts)

    async def test_health_timestamp_is_iso(self, client):
        from datetime import datetime
        response = await client.get("/health")
        ts = response.json()["timestamp"]
        # No lanza excepción si es ISO 8601 válido
        dt = datetime.fromisoformat(ts)
        assert dt is not None

    async def test_docs_accessible(self, client):
        """Swagger UI generado automáticamente por FastAPI."""
        response = await client.get("/docs")
        assert response.status_code == 200
