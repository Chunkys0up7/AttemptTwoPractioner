import pytest
from fastapi.testclient import TestClient
from mcp.api.main import app

client = TestClient(app)

def test_format_code_valid():
    response = client.post("/api/v1/formatting/format/code", json={"code": "def foo():\n  return 1"})
    assert response.status_code == 200
    data = response.json()
    assert "formatted_code" in data
    assert data["errors"] == []

def test_format_code_invalid():
    response = client.post("/api/v1/formatting/format/code", json={"code": "def foo(\nreturn 1"})
    assert response.status_code == 200
    data = response.json()
    assert "formatted_code" in data
    assert data["errors"]

def test_format_batch():
    response = client.post("/api/v1/formatting/format/batch", json={"batch": ["def a():\n return 1", "def b():\n return 2"]})
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert isinstance(data["results"], list)

# Config endpoint (placeholder)
def test_format_config():
    response = client.get("/api/v1/formatting/format/config")
    assert response.status_code == 200
    data = response.json()
    assert "config" in data 