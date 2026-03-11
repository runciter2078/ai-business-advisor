# =============================================================================
# AI Business Advisor — Dockerfile
# Base: python:3.11-slim (imagen oficial, mínima, reproducible)
# =============================================================================

FROM python:3.11-slim

# Metadatos
LABEL maintainer="Pablo Beret"
LABEL description="AI Business Advisor — Forecasting API"
LABEL version="1.0.0"

# Variables de entorno de Python
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Dependencias del sistema necesarias para Prophet y LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libgomp1 \
    && rm -rf /var/lib/apt/lists/*

# Instalar dependencias Python (capa separada para cache eficiente)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Copiar código fuente
COPY app/ ./app/
COPY data/ ./data/

# Crear directorios de datos en tiempo de build
RUN mkdir -p data/drift_reports

# Usuario no-root por seguridad
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Puerto expuesto
EXPOSE 8000

# Health check incorporado
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Comando de arranque
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
