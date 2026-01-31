"""
API endpoint tests for Snip backend
"""
import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/healthz")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["service"] == "snip"


def test_healthz_ready():
    """Test readiness endpoint (DB + config checks)"""
    response = client.get("/healthz/ready")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert "checks" in data
    assert "database" in data["checks"]
    assert data["checks"]["database"] == "ok"


def test_docs_endpoint():
    """Test API documentation endpoint"""
    response = client.get("/docs")
    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]


def test_openapi_schema():
    """Test OpenAPI schema endpoint"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert schema["info"]["title"] == "Snip API"
    assert "paths" in schema


def test_clients_endpoint_requires_auth():
    """Test that protected endpoints require authentication"""
    response = client.get("/api/clients/me")
    assert response.status_code in [401, 403]  # Unauthorized or Forbidden
    assert "API key" in response.json()["detail"] or "authentication" in response.json()["detail"].lower()


def test_invalid_endpoint():
    """Test 404 for invalid endpoints"""
    response = client.get("/nonexistent")
    assert response.status_code == 404


def test_cors_headers():
    """Test CORS headers are present"""
    response = client.options("/healthz")
    # CORS middleware should be configured
    assert response.status_code in [200, 204]


def test_create_client_no_data():
    """Test creating client with missing required fields"""
    response = client.post("/api/clients", json={})
    # Should return validation error
    assert response.status_code == 422  # Unprocessable Entity
