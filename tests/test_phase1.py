"""
Phase 1 automated tests: Config loading, FastAPI application, and /health endpoint.
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.config import get_settings


def test_settings_loaded():
    """Verify that settings are loaded with valid defaults."""
    settings = get_settings()
    assert settings.BACKEND_HOST == "127.0.0.1"
    assert settings.BACKEND_PORT == 8000
    assert settings.DB_NAME == "business_analytics"
    assert settings.database_url.startswith("mysql+pymysql://")


def test_health_endpoint():
    """Verify that GET /health returns 200 OK and valid status."""
    client = TestClient(app)
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"
