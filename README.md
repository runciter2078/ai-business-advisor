# AI Business Advisor

> Servicio de forecasting semanal de ventas para pequeños negocios de hostelería.
> Pipeline ML con Prophet y LightGBM, drift monitoring con Evidently y capa de
> interpretación agentic con LangGraph.

[![CI](https://github.com/tu-usuario/ai-business-advisor/actions/workflows/deploy.yml/badge.svg)](https://github.com/tu-usuario/ai-business-advisor/actions)
[![Python](https://img.shields.io/badge/python-3.11-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green.svg)](https://fastapi.tiangolo.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

---

## ¿Qué hace este proyecto?

Un restaurante o bar sube su histórico diario de ventas (CSV). El sistema:

1. **Genera una previsión semanal** para las próximas 4 semanas
2. **Compara dos modelos** — Prophet (base) vs LightGBM (challenger) — y selecciona el mejor
3. **Detecta drift** automáticamente comparando la distribución de los datos nuevos con el histórico
4. **Genera recomendaciones operativas** contextualizadas con festivos y notas sectoriales (vía agente LangGraph)

Todo accesible por API REST, contenerizado con Docker y desplegado en Azure Container Apps.

---

## Stack tecnológico

| Capa | Tecnología | Por qué |
|------|-----------|---------|
| API | FastAPI 0.115 | Estándar serving ML. Swagger automático. Async nativo. |
| Validación | Pydantic v2 | Integrado con FastAPI. Validación de esquemas robusta. |
| Forecasting base | Prophet (Meta) | Estacionalidad múltiple y festivos nativos. Interpretable. |
| Forecasting challenger | LightGBM | GBDT rápido con features tabulares. Complementa Prophet. |
| Drift monitoring | Evidently | Específico para ML monitoring. Genera artefactos HTML. |
| Agente | LangGraph | Workflows con estado explícito y trazabilidad. No LangChain legacy. |
| BD | SQLite + SQLAlchemy | Cero dependencias externas en el MVP. Decisión consciente. |
| Contenedor | Docker | python:3.11-slim. Reproducibilidad total. |
| CI/CD | GitHub Actions | Test → Build → Deploy automatizados. |
| Cloud | Azure Container Apps | Escala a cero. Gap Azure cubierto. |

---

## Arranque rápido

### Prerrequisitos

- Python 3.11+
- Docker y docker-compose (para el stack contenerizado)

### Desarrollo local

```bash
# 1. Clonar y configurar entorno
git clone https://github.com/tu-usuario/ai-business-advisor.git
cd ai-business-advisor
make setup          # instala dependencias y crea .env desde .env.example

# 2. Generar datos sintéticos de demo
make data           # crea data/sample_data.csv

# 3. Arrancar el servidor
make run            # http://localhost:8000

# 4. Abrir Swagger UI
open http://localhost:8000/docs
```

### Con Docker

```bash
make docker-run     # docker-compose up --build
# o
docker-compose up --build
```

---

## Endpoints

| Endpoint | Método | Descripción |
|----------|--------|-------------|
| `/health` | GET | Health check del servicio |
| `/upload` | POST | Sube CSV con histórico de ventas |
| `/forecast` | POST | Ejecuta pipeline ML, devuelve predicciones + métricas |
| `/forecast/{id}` | GET | Recupera un forecast guardado |
| `/forecast/{id}/drift` | GET | Reporte Evidently HTML del drift |
| `/insight` | POST | Agente LangGraph: insight + recomendaciones |
| `/docs` | GET | Swagger UI (generado automáticamente) |

---

## Datos de ejemplo

El fichero `data/sample_data.csv` es el CSV de demo. Generado con:

```bash
python data/generate_sample.py --years 2 --seed 42
```

Formato mínimo válido para el endpoint `/upload`:

```csv
date,sales
2024-01-01,712.50
2024-01-02,698.30
...
```

Los campos `weekday` e `is_holiday` son opcionales — el pipeline los deriva automáticamente.

---

## Tests

```bash
make test           # suite completa con cobertura
make test-fast      # sin reporte de cobertura
make test-api       # solo tests de API
make test-pipeline  # solo tests del pipeline ML
```

---

## Decisiones de diseño

Principales decisiones arquitectónicas y su justificación:

- **SQLite sobre PostgreSQL**: Cero dependencias externas en el MVP. En producción real se sustituiría por PostgreSQL en Azure con pool de conexiones.
- **Prophet + LightGBM**: Prophet por interpretabilidad y manejo nativo de estacionalidad. LightGBM como challenger por su potencia con features tabulares.
- **LangGraph sobre LangChain legacy**: Estado explícito, flujos auditables, sin magia implícita.
- **Contexto fijo (JSON) sobre RAG**: Misma señal técnica del agente, complejidad radicalmente menor. RAG queda documentado como evolución futura.
- **Azure Container Apps**: Escala a cero (coste cero sin tráfico). Si genera fricción en despliegue, alternativa con Render/Railway.

---

## Roadmap

- [x] Semana 1 — Cimientos: estructura, entorno, `/health`, datos sintéticos
- [ ] Semana 2 — Pipeline de forecasting: `/upload`, Prophet, métricas
- [ ] Semana 3 — Challenger y evaluación: LightGBM, comparativa, `/forecast/{id}`
- [ ] Semana 4 — Contenedorización y tests: Docker, cobertura >70%
- [ ] Semana 5 — CI/CD y Evidently: GitHub Actions, drift monitoring
- [ ] Semana 6 — Agente LangGraph: `/insight`, demo pública

---

## Autor

**Pablo Beret** · Data Scientist / AI Engineer  
[LinkedIn](https://linkedin.com/in/tu-perfil) · [GitHub](https://github.com/tu-usuario)
