"""
Test utility functions and helpers for security middleware tests.
"""
import os
import sys
from typing import Dict, Optional, Any
from fastapi.testclient import TestClient
from starlette.datastructures import Headers

# Add project root to PYTHONPATH
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

# Import FastAPI after setting TESTING
from fastapi import FastAPI

# Import security middleware after setting TESTING
from mcp.api.middleware.security import SecurityMiddleware

class TestRequest:
    """Helper class for creating test requests."""
    def __init__(self, client: TestClient):
        self.client = client
        
    def get(self, path: str, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Send a GET request."""
        response = self.client.get(path, headers=headers)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.content,
            "json": response.json() if response.status_code != 400 else None
        }
    
    def post(self, path: str, data: dict, headers: Optional[Dict[str, str]] = None) -> Dict[str, Any]:
        """Send a POST request."""
        response = self.client.post(path, json=data, headers=headers)
        return {
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.content,
            "json": response.json() if response.status_code != 400 else None
        }

def create_test_headers(
    host: Optional[str] = None,
    ip: Optional[str] = None,
    xss_payload: Optional[str] = None,
    sql_injection: Optional[str] = None,
    csrf_token: Optional[str] = None,
    auth_token: Optional[str] = None
) -> Dict[str, str]:
    """Create test headers with various security-related parameters."""
    headers = {
        'Host': host or 'test.local',
        'X-Forwarded-For': ip or '127.0.0.1',
        'User-Agent': 'TestClient/1.0',
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    
    if xss_payload:
        headers['X-XSS-Payload'] = xss_payload
    
    if sql_injection:
        headers['X-SQL-Injection'] = sql_injection
    
    if csrf_token:
        headers['X-CSRF-Token'] = csrf_token
    
    if auth_token:
        headers['Authorization'] = f'Bearer {auth_token}'
    
    return headers

def assert_security_headers(response: dict, expected_headers: Dict[str, str]):
    """Assert that security headers are present and correct."""
    for header, value in expected_headers.items():
        assert header in response["headers"]
        assert response["headers"][header] == value

def assert_rate_limit_headers(response: dict):
    """Assert that rate limit headers are present."""
    assert "X-RateLimit-Limit" in response["headers"]
    assert "X-RateLimit-Remaining" in response["headers"]
    assert "X-RateLimit-Reset" in response["headers"]

def create_test_client(app) -> TestClient:
    """Create a test client with security middleware."""
    from mcp.api.middleware.security import SecurityMiddleware
    middleware = SecurityMiddleware(app)
    return TestClient(middleware)

def create_test_app() -> FastAPI:
    """Create a test FastAPI app with test endpoints."""
    app = FastAPI(
        title="MCP Backend API (Test)",
        description="API for managing MCP workflows and executions (Test Mode).",
        version="1.0.0",
        docs_url=None,  # Disable docs in test mode
        redoc_url=None,
        openapi_url=None
    )
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "Test successful"}
    
    @app.post("/test")
    async def test_post_endpoint(data: dict):
        return {"received": data}
    
    return app

def create_test_settings() -> Dict[str, str]:
    """Create test settings dictionary."""
    return {
        "ALLOWED_HOSTS": ["localhost", "127.0.0.1"],
        "CSP_POLICY": "default-src 'self'; frame-ancestors 'none';",
        "XSS_PROTECTION": "1; mode=block",
        "RATE_LIMIT_WINDOW": 60,
        "RATE_LIMIT_MAX_REQUESTS": 10,
        "IP_BLACKLIST": ["192.168.1.100"],
        "IP_WHITELIST": ["127.0.0.1"]
    }
