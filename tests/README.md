# Data Engineering Workflow Platform - Testing Guide

## Test Structure

```
tests/
├── unit/              # Fast unit tests (no external dependencies)
│   ├── test_ingestion.py
│   ├── test_transformation.py
│   └── test_quality.py
└── integration/       # Integration tests (require PostgreSQL, MinIO)
    └── test_pipeline.py
```

## Running Tests

### Unit Tests (Fast, No External Dependencies)

```bash
# Run all unit tests
pytest tests/unit/ -v

# Run with coverage
pytest tests/unit/ -v --cov=ingestion --cov=transformation --cov=quality

# Run specific test file
pytest tests/unit/test_ingestion.py -v

# Run specific test
pytest tests/unit/test_ingestion.py::TestValidate::test_validate_passes_valid_data -v
```

### Integration Tests (Require PostgreSQL & MinIO)

Start required services:
```bash
docker compose up -d datawarehouse minio minio-init
```

Wait for services to be healthy:
```bash
docker compose ps
```

Run integration tests:
```bash
# Set test environment variables
export TEST_DB_HOST=localhost
export TEST_DB_PORT=5432
export TEST_DB_USER=dataeng
export TEST_DB_PASSWORD=dataeng
export TEST_DB_NAME=datawarehouse
export TEST_MINIO_ENDPOINT=localhost:9000
export TEST_MINIO_ACCESS_KEY=minioadmin
export TEST_MINIO_SECRET_KEY=minioadmin

# Run integration tests
pytest tests/integration/ -v -s
```

### All Tests

```bash
pytest tests/ -v
```

## Test Configuration

Tests are configured via `pyproject.toml`:
- Unit tests run by default
- Integration tests marked with `@pytest.mark.integration`
- Coverage configured for source packages

## Writing New Tests

### Unit Test Example

```python
import pytest
from unittest.mock import Mock, patch

def test_my_function():
    with patch("module.external_dependency") as mock:
        mock.return_value = "expected"
        result = my_function()
        assert result == "expected"
```

### Integration Test Example

```python
import pytest
from sqlalchemy import create_engine, text

@pytest.fixture
def db_engine():
    engine = create_engine("postgresql://user:pass@localhost/db")
    yield engine
    engine.dispose()

def test_database_operation(db_engine):
    with db_engine.connect() as conn:
        result = conn.execute(text("SELECT 1")).scalar()
        assert result == 1
```

## CI/CD

Tests run automatically on:
- Every push to main/develop
- Every pull request
- Manual workflow dispatch

See `.github/workflows/ci-cd.yml` for details.