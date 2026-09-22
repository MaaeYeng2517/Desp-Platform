# Data Engineering Workflow Platform - Makefile
# Common development tasks

.PHONY: help install test lint format typecheck up down logs clean dbt-run dbt-test

# Default target
help:
	@echo "Data Engineering Workflow Platform - Development Commands"
	@echo ""
	@echo "Environment:"
	@echo "  make install        Install Python dependencies"
	@echo "  make install-dev    Install with dev dependencies"
	@echo ""
	@echo "Testing:"
	@echo "  make test           Run all tests"
	@echo "  make test-unit      Run unit tests only"
	@echo "  make test-integration  Run integration tests (requires services)"
	@echo "  make test-coverage  Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  make lint           Run ruff linter"
	@echo "  make format         Format code with black and isort"
	@echo "  make typecheck      Run mypy type checking"
	@echo ""
	@echo "Docker:"
	@echo "  make up             Start all services"
	@echo "  make down           Stop all services"
	@echo "  make logs           View service logs"
	@echo "  make ps             List running services"
	@echo "  make clean          Remove all containers and volumes"
	@echo ""
	@echo "dbt:"
	@echo "  make dbt-deps       Install dbt dependencies"
	@echo "  make dbt-run        Run dbt models"
	@echo "  make dbt-test       Run dbt tests"
	@echo "  make dbt-docs       Generate dbt documentation"
	@echo ""
	@echo "Pipeline:"
	@echo "  make ingest         Run ingestion pipeline"
	@echo "  make transform      Run transformation pipeline"
	@echo "  make quality        Run quality checks"
	@echo "  make full-pipeline  Run complete pipeline"
	@echo ""

# =============================================================================
# Environment
# =============================================================================

install:
	uv pip install -r requirements.txt

install-dev:
	uv pip install -r requirements.txt
	uv pip install pytest pytest-cov pytest-mock ruff black isort mypy dbt-postgres dbt-expectations

# =============================================================================
# Testing
# =============================================================================

test: test-unit test-integration

test-unit:
	pytest tests/unit/ -v

test-integration:
	@echo "Starting test services..."
	docker compose up -d datawarehouse minio minio-init
	@echo "Waiting for services..."
	@sleep 10
	TEST_DB_HOST=localhost TEST_DB_PORT=5432 TEST_DB_USER=dataeng TEST_DB_PASSWORD=dataeng TEST_DB_NAME=datawarehouse \
	TEST_MINIO_ENDPOINT=localhost:9000 TEST_MINIO_ACCESS_KEY=minioadmin TEST_MINIO_SECRET_KEY=minioadmin \
	pytest tests/integration/ -v -s

test-coverage:
	pytest tests/unit/ -v --cov=ingestion --cov=transformation --cov=quality --cov-report=html --cov-report=term

# =============================================================================
# Code Quality
# =============================================================================

lint:
	ruff check .

format:
	black .
	isort .

typecheck:
	mypy --ignore-missing-imports ingestion/ transformation/ quality/ dags/ || true

# =============================================================================
# Docker
# =============================================================================

up:
	docker compose up -d

down:
	docker compose down

down-v:
	docker compose down -v

logs:
	docker compose logs -f

ps:
	docker compose ps

clean:
	docker compose down -v --remove-orphans
	docker system prune -f

# =============================================================================
# dbt
# =============================================================================

dbt-deps:
	cd dbt && dbt deps

dbt-run:
	cd dbt && dbt run --profiles-dir .

dbt-test:
	cd dbt && dbt test --profiles-dir .

dbt-docs:
	cd dbt && dbt docs generate --profiles-dir .

dbt-docs-serve:
	cd dbt && dbt docs serve --profiles-dir .

# =============================================================================
# Pipeline
# =============================================================================

ingest:
	PGPASSWORD=dataeng DB_HOST=localhost MINIO_ENDPOINT=localhost:9000 \
	MINIO_ACCESS_KEY=minioadmin MINIO_SECRET_KEY=minioadmin \
	python ingestion/sales_pipeline_minio.py

transform:
	MINIO_ENDPOINT=localhost:9000 MINIO_ACCESS_KEY=minioadmin \
	MINIO_SECRET_KEY=minioadmin \
	python transformation/sales_silver_minio.py

quality:
	PGPASSWORD=dataeng DB_HOST=localhost python quality/sales_quality.py
	PGPASSWORD=dataeng DB_HOST=localhost python quality/gold_quality.py

full-pipeline: ingest transform quality
	@echo "Full pipeline completed!"

# =============================================================================
# Airflow
# =============================================================================

airflow-init:
	docker compose up airflow-init

airflow-up:
	docker compose up -d airflow-apiserver airflow-scheduler airflow-worker airflow-triggerer airflow-dag-processor

airflow-logs:
	docker compose logs -f airflow-scheduler airflow-worker

# =============================================================================
# Spark
# =============================================================================

spark-submit:
	./scripts/submit_spark_job.sh full

spark-submit-silver:
	./scripts/submit_spark_job.sh silver

spark-submit-gold:
	./scripts/submit_spark_job.sh gold

# =============================================================================
# Database
# =============================================================================

db-init:
	PGPASSWORD=dataeng psql -h localhost -U dataeng -d datawarehouse -f sql/init_schema.sql

db-shell:
	PGPASSWORD=dataeng psql -h localhost -U dataeng -d datawarehouse

# =============================================================================
# MinIO
# =============================================================================

minio-init:
	docker compose up minio-init

minio-shell:
	mc alias set local http://localhost:9000 minioadmin minioadmin