import pytest
from unittest.mock import patch, AsyncMock

from fastapi.testclient import TestClient


class TestAPIRoutes:
    """Test API route registration and basic responses."""

    @pytest.fixture
    def client(self, monkeypatch):
        monkeypatch.setattr("app.core.database.init_db", AsyncMock())
        monkeypatch.setattr("app.core.minio_client.ensure_all_buckets", lambda x: None)

        from app.main import app
        app.dependency_overrides = {}
        with TestClient(app) as c:
            yield c

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert "service" in data
        assert "endpoints" in data

    def test_health(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "healthy", "service": "Data Core Platform"}

    def test_docs_available(self, client):
        response = client.get("/docs")
        assert response.status_code == 200

    def test_openapi_available(self, client):
        response = client.get("/api/openapi.json")
        assert response.status_code == 200
        spec = response.json()
        assert "paths" in spec
        assert "/api/v1/datasets" in spec["paths"]
        assert "/api/v1/files/upload" in spec["paths"]
        assert "/api/v1/raw/store" in spec["paths"]
        assert "/api/v1/validation/check" in spec["paths"]
        assert "/api/v1/cleaning/{file_id}" in spec["paths"]
        assert "/api/v1/transformation/{file_id}/transform" in spec["paths"]
        assert "/api/v1/quality/rules/{dataset_id}" in spec["paths"]
        assert "/api/v1/metadata/{dataset_id}/record" in spec["paths"]
        assert "/api/v1/audit/" in spec["paths"]
        assert "/api/v1/monitor/status" in spec["paths"]
        assert "/api/v1/lineage/events" in spec["paths"]
        assert "/api/v1/serve/query" in spec["paths"]
