"""
Comprehensive test suite for Security Middleware.

This module contains unit and integration tests for the Security Middleware component.
It covers all security features including host validation, XSS protection,
rate limiting, IP blacklisting/whitelisting, and monitoring integration.
"""
import pytest
from mcp.api.middleware.security import SecurityMiddleware
from mcp.core.config import settings
from mcp.core.monitoring import monitor
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.datastructures import Headers
from typing import Generator
import time
from unittest.mock import Mock, patch

@pytest.fixture
def test_client() -> Generator[TestClient, None, None]:
    """Create a test client with security middleware."""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "Test successful"}
    
    @app.post("/test")
    async def test_post_endpoint(data: dict):
        return {"received": data}
    
    middleware = SecurityMiddleware(app)
    client = TestClient(middleware)
    yield client
    # Cleanup if needed

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    class MockSettings:
        ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
        CSP_POLICY = "default-src 'self'; frame-ancestors 'none';"
        XSS_PROTECTION = "1; mode=block"
        RATE_LIMIT_WINDOW = 60
        RATE_LIMIT_MAX_REQUESTS = 10
        IP_BLACKLIST = ["192.168.1.100"]
        IP_WHITELIST = ["127.0.0.1"]
        
    return MockSettings()

@pytest.fixture
def mock_monitor():
    """Mock monitor fixture."""
    return Mock()

@pytest.fixture
def app():
    """FastAPI app fixture."""
    return FastAPI()

@pytest.fixture
def middleware(app, mock_settings, mock_monitor):
    """Security middleware fixture."""
    return SecurityMiddleware(app, mock_settings, mock_monitor)

@pytest.fixture
def test_client(middleware):
    """Test client fixture."""
    return TestClient(middleware.app)

@patch('mcp.api.middleware.security.settings', new_callable=Mock)
def test_valid_host_header(mock_settings, test_client):
    """Test valid host header."""
    mock_settings.ALLOWED_HOSTS = ['localhost', '127.0.0.1']
    response = test_client.get('/', headers={'Host': 'localhost'})
    assert response.status_code == 200

@patch('mcp.api.middleware.security.settings', new_callable=Mock)
def test_invalid_host_header(mock_settings, test_client):
    """Test invalid host header."""
    mock_settings.ALLOWED_HOSTS = ['localhost']
    response = test_client.get('/', headers={'Host': 'malicious.com'})
    assert response.status_code == 400

@patch('mcp.api.middleware.security.settings', new_callable=Mock)
def test_csp_headers(mock_settings, test_client):
    """Test CSP headers."""
    mock_settings.CSP_POLICY = 'default-src \'self\'; frame-ancestors \'none\';'
    response = test_client.get('/')
    assert 'Content-Security-Policy' in response.headers
    assert response.headers['Content-Security-Policy'] == mock_settings.CSP_POLICY

@patch('mcp.api.middleware.security.settings', new_callable=Mock)
def test_xss_protection(mock_settings, test_client):
    """Test XSS protection."""
    mock_settings.XSS_PROTECTION = '1; mode=block'
    response = test_client.get('/')
    assert 'X-XSS-Protection' in response.headers
    assert response.headers['X-XSS-Protection'] == mock_settings.XSS_PROTECTION

@patch('mcp.api.middleware.security.settings', new_callable=Mock)
def test_rate_limiting(mock_settings, test_client):
    """Test rate limiting."""
    mock_settings.RATE_LIMIT_WINDOW = 60
    mock_settings.RATE_LIMIT_MAX_REQUESTS = 10
    
    # Make 11 requests to trigger rate limiting
    for _ in range(11):
        response = test_client.get('/')
        if response.status_code == 429:
            break
    
    assert response.status_code == 429

@patch('mcp.api.middleware.security.settings', new_callable=Mock)
def test_ip_blacklisting(mock_settings, test_client):
    """Test IP blacklisting."""
    mock_settings.IP_BLACKLIST = ['192.168.1.100']
    headers = Headers({'X-Forwarded-For': '192.168.1.100'})
    response = test_client.get('/', headers=headers)
    assert response.status_code == 403

@patch('mcp.api.middleware.security.settings', new_callable=Mock)
def test_ip_whitelisting(mock_settings, test_client):
    """Test IP whitelisting."""
    mock_settings.IP_WHITELIST = ['127.0.0.1']
    headers = Headers({'X-Forwarded-For': '192.168.1.100'})
    response = test_client.get('/', headers=headers)
    assert response.status_code == 403

    headers = Headers({'X-Forwarded-For': '127.0.0.1'})
    response = test_client.get('/', headers=headers)
    assert response.status_code == 200
