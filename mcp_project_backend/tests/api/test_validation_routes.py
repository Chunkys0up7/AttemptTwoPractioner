import pytest
from fastapi.testclient import TestClient
from mcp.api.main import app

client = TestClient(app)

# --- Syntax Validation ---
def test_validate_syntax_valid():
    response = client.post("/api/v1/validation/validate/syntax", json={"code": "print('hello')"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["errors"] == []

def test_validate_syntax_invalid():
    response = client.post("/api/v1/validation/validate/syntax", json={"code": "print('hello'"})
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert data["errors"]

# --- Type Validation (placeholder) ---
def test_validate_type():
    response = client.post("/api/v1/validation/validate/type", json={"code": "x = 1"})
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data

# --- Security Validation (placeholder) ---
def test_validate_security():
    response = client.post("/api/v1/validation/validate/security", json={"code": "import os"})
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data

# --- Performance Validation (placeholder) ---
def test_validate_performance():
    response = client.post("/api/v1/validation/validate/performance", json={"code": "for i in range(10): pass"})
    assert response.status_code == 200
    data = response.json()
    assert "valid" in data 