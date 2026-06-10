.PHONY: help install lint format test run dev docker-up docker-down migrate migration-clean db-shell clean

APP_NAME = gestion-beneficiarios-be
PYTHON = python

help: ## Muestra esta ayuda
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

install: ## Instala dependencias del proyecto
	pip install -r requirements.txt
	pip install -r requirements-dev.txt

lint: ## Ejecuta linters (ruff)
	ruff check app/ tests/
	ruff format --check app/ tests/

format: ## Formatea el código automáticamente
	ruff check --fix app/ tests/
	ruff format app/ tests/

test: ## Ejecuta tests con pytest
	python -m pytest tests/ -v --tb=short --maxfail=3

test-cov: ## Ejecuta tests con cobertura
	python -m pytest tests/ -v --tb=short --maxfail=3 --cov=app --cov-report=term --cov-report=html

run: ## Ejecuta la API localmente (sin Docker)
	uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

dev: docker-up ## Alias para docker-up

docker-up: ## Levanta servicios con Docker Compose
	docker compose up --build -d

docker-down: ## Detiene servicios Docker
	docker compose down

docker-logs: ## Muestra logs de Docker
	docker compose logs -f

migrate: ## Aplica migraciones pendientes (en orden)
	@bash scripts/apply_migrations.sh

migration: ## Crea una nueva migración. Uso: make migration name="descripcion_del_cambio"
	@bash scripts/create_migration.sh "$(name)"

migration-clean: ## Revierte la última migración
	@echo "⚠️  No hay rollback automático. Revertir manualmente usando scripts/migrations/rollback/"

db-shell: ## Abre shell interactivo de PostgreSQL
	docker compose exec db psql -U root -d gestion_beneficiarios

clean: ## Limpia archivos temporales y cachés
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	rm -rf .coverage htmlcov/
	echo "✅ Limpieza completada"