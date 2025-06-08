"""
Test fixtures and data for security middleware tests.
"""
import pytest
from typing import Dict, Any, Generator
import os
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mcp.api.middleware.security import SecurityMiddleware

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

@pytest.fixture(scope="module")
def test_app() -> Generator[FastAPI, None, None]:
    """Create a test FastAPI app with security middleware."""
    app = FastAPI(
        title="MCP Backend API (Test)",
        description="API for managing MCP workflows and executions (Test Mode).",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "Test successful"}
    
    @app.post("/test")
    async def test_post_endpoint(data: dict):
        return {"received": data}
    
    @app.get("/protected")
    async def protected_endpoint():
        return {"message": "Protected endpoint"}
    
    yield app
    
    # Cleanup
    del app

@pytest.fixture(scope="module")
def test_client(test_app: FastAPI) -> Generator[TestClient, None, None]:
    """Create a test client with security middleware."""
    middleware = SecurityMiddleware(test_app)
    client = TestClient(middleware)
    yield client
    
    # Cleanup
    del client
    del middleware

@pytest.fixture(scope="function")
def test_settings() -> Dict[str, Any]:
    """Test settings fixture."""
    return {
        "ALLOWED_HOSTS": ["localhost", "127.0.0.1"],
        "CSP_POLICY": "default-src 'self'; frame-ancestors 'none';",
        "XSS_PROTECTION": "1; mode=block",
        "RATE_LIMIT_WINDOW": 60,
        "RATE_LIMIT_MAX_REQUESTS": 10,
        "IP_BLACKLIST": ["192.168.1.100"],
        "IP_WHITELIST": ["127.0.0.1"],
        "TESTING": True
    }

@pytest.fixture(scope="function")
def test_headers() -> Dict[str, str]:
    """Base test headers fixture."""
    return {
        "Host": "localhost",
        "X-Forwarded-For": "127.0.0.1",
        "User-Agent": "TestClient/1.0",
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

@pytest.fixture(scope="function")
def test_security_headers() -> Dict[str, str]:
    """Security-related test headers fixture."""
    return {
        "X-CSRF-Token": "test-token",
        "Authorization": "Bearer test-token",
        "X-Request-ID": "test-request-id"
    }
