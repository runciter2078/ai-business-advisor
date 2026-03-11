# =============================================================================
# AI Business Advisor — Makefile
# =============================================================================

.PHONY: help run test lint format build docker-run docker-stop clean data

# Variables
APP_MODULE := app.main:app
DOCKER_IMAGE := ai-business-advisor
DOCKER_TAG := latest

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# ---- Desarrollo local -------------------------------------------------------

run: ## Arranca el servidor FastAPI en modo desarrollo (hot-reload)
	uvicorn $(APP_MODULE) --host 0.0.0.0 --port 8000 --reload

run-prod: ## Arranca el servidor en modo producción
	uvicorn $(APP_MODULE) --host 0.0.0.0 --port 8000 --workers 2

# ---- Tests ------------------------------------------------------------------

test: ## Ejecuta la suite completa de tests con cobertura
	pytest tests/ -v --cov=app --cov-report=term-missing --cov-report=html:coverage_html

test-fast: ## Ejecuta tests sin reporte de cobertura (más rápido)
	pytest tests/ -v

test-pipeline: ## Ejecuta solo los tests del pipeline ML
	pytest tests/test_pipeline.py -v

test-api: ## Ejecuta solo los tests de la API
	pytest tests/test_api.py -v

# ---- Calidad de código ------------------------------------------------------

lint: ## Ejecuta ruff (linter)
	ruff check app/ tests/

lint-fix: ## Ejecuta ruff con auto-fix
	ruff check app/ tests/ --fix

format: ## Formatea con black
	black app/ tests/ data/

format-check: ## Comprueba formato sin modificar
	black app/ tests/ data/ --check

check: lint format-check ## lint + format-check (usado en CI)

# ---- Docker -----------------------------------------------------------------

build: ## Construye la imagen Docker
	docker build -t $(DOCKER_IMAGE):$(DOCKER_TAG) .

docker-run: ## Levanta el stack con docker-compose
	docker-compose up --build

docker-run-detach: ## Levanta el stack en background
	docker-compose up --build -d

docker-stop: ## Para y elimina los contenedores
	docker-compose down

docker-logs: ## Muestra logs del contenedor
	docker-compose logs -f

# ---- Datos ------------------------------------------------------------------

data: ## Genera el CSV de datos sintéticos
	python data/generate_sample.py

# ---- Limpieza ---------------------------------------------------------------

clean: ## Elimina artefactos generados
	find . -type f -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null; true
	find . -type d -name "coverage_html" -exec rm -rf {} + 2>/dev/null; true
	rm -f .coverage
	@echo "Limpieza completada."

# ---- Setup inicial ----------------------------------------------------------

setup: ## Instala dependencias y crea .env desde .env.example
	pip install -r requirements.txt
	@if [ ! -f .env ]; then cp .env.example .env; echo ".env creado. Rellena las variables."; fi
	mkdir -p data/drift_reports
	@echo "Setup completado."
