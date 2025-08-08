import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_read_main():
    """Тест главной страницы"""
    response = client.get("/")
    assert response.status_code == 200
    assert "Pair Helper API" in response.json()["message"]


def test_health_check():
    """Тест проверки здоровья"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_api_docs():
    """Тест доступности документации API"""
    response = client.get("/docs")
    assert response.status_code == 200


def test_openapi_schema():
    """Тест схемы OpenAPI"""
    response = client.get("/openapi.json")
    assert response.status_code == 200
    schema = response.json()
    assert "openapi" in schema
    assert "info" in schema
    assert "paths" in schema
