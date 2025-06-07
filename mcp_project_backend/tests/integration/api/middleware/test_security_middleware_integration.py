"""
Integration tests for the security middleware using FastAPI TestClient.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.middleware import Middleware
from mcp.api.middleware.security import SecurityMiddleware
from mcp.core.config import settings
from mcp.core.monitoring import monitor

@pytest.fixture
def app():
    """Create a FastAPI app instance for testing."""
    app = FastAPI()
    app.add_middleware(SecurityMiddleware)
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "Test successful"}
    
    @app.post("/test")
    async def test_post_endpoint(data: dict):
        return {"received": data}
    
    return app

@pytest.fixture
def client(app):
    """Create a TestClient instance for testing."""
    return TestClient(app)

def test_valid_request(client):
    """Test a valid request with proper headers."""
    response = client.get(
        "/test",
        headers={
            "Host": "localhost",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'"
        }
    )
    
    assert response.status_code == 200
    assert response.json() == {"message": "Test successful"}

def test_invalid_host(client):
    """Test request with invalid host header."""
    response = client.get(
        "/test",
        headers={
            "Host": "invalid-host",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'"
        }
    )
    
    assert response.status_code == 400

def test_invalid_xss_protection(client):
    """Test request with invalid XSS protection header."""
    response = client.get(
        "/test",
        headers={
            "Host": "localhost",
            "X-XSS-Protection": "0",
            "Content-Security-Policy": "default-src 'self'"
        }
    )
    
    assert response.status_code == 400

def test_invalid_csp(client):
    """Test request with invalid Content Security Policy."""
    response = client.get(
        "/test",
        headers={
            "Host": "localhost",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src *"
        }
    )
    
    assert response.status_code == 400

def test_rate_limiting(client):
    """Test rate limiting functionality."""
    # First request should succeed
    response = client.get(
        "/test",
        headers={
            "Host": "localhost",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'"
        }
    )
    
    assert response.status_code == 200
    
    # Mock rate limiter to fail
    with patch("mcp.core.config.settings.RATE_LIMITER") as mock_rate_limiter:
        mock_rate_limiter.side_effect = Exception("Rate limit exceeded")
        
        response = client.get(
            "/test",
            headers={
                "Host": "localhost",
                "X-XSS-Protection": "1; mode=block",
                "Content-Security-Policy": "default-src 'self'"
            }
        )
        
        assert response.status_code == 429

def test_input_sanitization(client):
    """Test input sanitization for POST requests."""
    response = client.post(
        "/test",
        headers={
            "Host": "localhost",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'"
        },
        json={"data": "<script>alert('xss')</script>"}
    )
    
    assert response.status_code == 200
    assert response.json() == {"received": {"data": "&lt;script&gt;alert('xss')&lt;/script&gt;"}}

def test_security_headers(client):
    """Test security headers in response."""
    response = client.get(
        "/test",
        headers={
            "Host": "localhost",
            "X-XSS-Protection": "1; mode=block",
            "Content-Security-Policy": "default-src 'self'"
        }
    )
    
    assert response.status_code == 200
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "max-age=31536000" in response.headers["Strict-Transport-Security"]
    assert "default-src 'self'" in response.headers["Content-Security-Policy"]
    assert "strict-origin-when-cross-origin" in response.headers["Referrer-Policy"]
    assert "no-store" in response.headers["Cache-Control"]
    assert response.headers["Pragma"] == "no-cache"
    assert response.headers["Expires"] == "0"
    assert "request-id" in response.headers["X-Request-ID"]

def test_ip_blacklist(client):
    """Test IP blacklist functionality."""
    # Mock settings to include test IP in blacklist
    with patch("mcp.core.config.settings.IP_BLACKLIST", ["127.0.0.1"]):
        response = client.get(
            "/test",
            headers={
                "Host": "localhost",
                "X-XSS-Protection": "1; mode=block",
                "Content-Security-Policy": "default-src 'self'"
            }
        )
        
        assert response.status_code == 403

def test_ip_whitelist(client):
    """Test IP whitelist functionality."""
    # Mock settings to include test IP in whitelist
    with patch("mcp.core.config.settings.IP_WHITELIST", ["127.0.0.1"]):
        response = client.get(
            "/test",
            headers={
                "Host": "localhost",
                "X-XSS-Protection": "1; mode=block",
                "Content-Security-Policy": "default-src 'self'"
            }
        )
        
        assert response.status_code == 200
        
        # Test non-whitelisted IP
        with patch("mcp.core.config.settings.IP_WHITELIST", ["192.168.1.1"]):
            response = client.get(
                "/test",
                headers={
                    "Host": "localhost",
                    "X-XSS-Protection": "1; mode=block",
                    "Content-Security-Policy": "default-src 'self'"
                }
            )
            
            assert response.status_code == 403

def test_monitoring_integration(client):
    """Test monitoring integration with actual requests."""
    with patch("mcp.core.monitoring.monitor.increment_event") as mock_increment:
        response = client.get(
            "/test",
            headers={
                "Host": "localhost",
                "X-XSS-Protection": "1; mode=block",
                "Content-Security-Policy": "default-src 'self'"
            }
        )
        
        assert response.status_code == 200
        
        # Verify security request processed event
        mock_increment.assert_any_call('security_request_processed')
        
        # Verify security headers added event
        mock_increment.assert_any_call('security_headers_added')
