"""
Tests for the security middleware functionality.
"""
import pytest
from fastapi import Request, Response
from fastapi.testclient import TestClient
from starlette.datastructures import Headers
from mcp.api.middleware.security import SecurityMiddleware
from mcp.core.config import settings
from mcp.core.monitoring import monitor

@pytest.fixture
def test_request(test_client):
    """Create a test request helper."""
    def create_request(
        method: str = "GET",
        path: str = "/test",
        headers: dict = None,
        body: bytes = None
    ):
        if headers is None:
            headers = {"Host": "localhost"}
        
        return test_client.request(
            method=method,
            url=path,
            headers=headers,
            content=body
        )
    
    return create_request

def test_host_header_validation(test_request):
    """Test host header validation."""
    # Valid host
    response = test_request(headers={"host": "localhost"})
    assert response.status_code == 200
    
    # Invalid host
    response = test_request(headers={"host": "invalid-host"})
    assert response.status_code == 400

def test_xss_protection(security_middleware: SecurityMiddleware):
    """Test XSS protection header validation."""
    # Valid XSS protection
    response = test_request(headers={
        "host": "localhost",
        "x-xss-protection": "1; mode=block"
    })
    assert response.status_code == 200
    
    # Invalid XSS protection
    response = test_request(headers={
        "host": "localhost",
        "x-xss-protection": "0"
    })
    assert response.status_code == 400

def test_content_security_policy(security_middleware: SecurityMiddleware):
    """Test Content Security Policy validation."""
    # Valid CSP
    response = test_request(headers={
        "host": "localhost",
        "content-security-policy": "default-src 'self'"
    })
    assert response.status_code == 200
    
    # Invalid CSP
    response = test_request(headers={
        "host": "localhost",
        "content-security-policy": "default-src *"
    })
    assert response.status_code == 400

def test_rate_limiting(security_middleware: SecurityMiddleware):
    """Test rate limiting functionality."""
    # First request should succeed
    response = test_request(headers={"host": "localhost"})
    assert response.status_code == 200
    
    # Mock rate limiter to fail
    with patch("mcp.core.config.settings.RATE_LIMITER") as mock_rate_limiter:
        mock_rate_limiter.side_effect = Exception("Rate limit exceeded")
        
        response = test_request(headers={"host": "localhost"})
        assert response.status_code == 429

def test_input_sanitization(security_middleware: SecurityMiddleware):
    """Test input sanitization functionality."""
    # Request should succeed with sanitized body
    response = test_request(
        method="POST",
        path="/test",
        headers={"host": "localhost"},
        body=b"<script>alert('xss')</script>"
    )
    assert response.status_code == 200
    
    # Verify body was sanitized
    assert b"&lt;script&gt;alert('xss')&lt;/script&gt;" in response.content

def test_security_headers(security_middleware: SecurityMiddleware):
    """Test security headers are added to response."""
    response = test_request(headers={"host": "localhost"})
    
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

def test_edge_cases(security_middleware: SecurityMiddleware):
    """Test edge cases for security middleware."""
    # Test with no headers
    request = Request(
        scope={
            "type": "http",
            "headers": Headers().raw,
            "client": ("127.0.0.1", 8080)
        }
    )
    
    response = security_middleware(request, security_middleware.app)
    assert response.status_code == 400
    
    # Test with malformed headers
    request = Request(
        scope={
            "type": "http",
            "headers": Headers({"host": ""}).raw,
            "client": ("127.0.0.1", 8080)
        }
    )
    
    with pytest.raises(Exception):
        security_middleware(request, security_middleware.app)
    
    # Test with invalid IP format
    request = Request(
        scope={
            "type": "http",
            "headers": Headers({"host": "localhost"}).raw,
            "client": ("invalid-ip", 8080)
        }
    )
    
    with pytest.raises(Exception):
        security_middleware(request, security_middleware.app)
    
    # Test with oversized request body
    large_body = "A" * (1024 * 1024 * 10)  # 10MB
    request = Request(
        scope={
            "type": "http",
            "headers": Headers({"host": "localhost"}).raw,
            "client": ("127.0.0.1", 8080),
            "method": "POST",
            "body": large_body.encode()
        }
    )
    
    with pytest.raises(Exception):
        security_middleware(request, security_middleware.app)
    
    # Test with invalid Content-Length
    request = Request(
        scope={
            "type": "http",
            "headers": Headers({
                "host": "localhost",
                "content-length": "invalid"
            }).raw,
            "client": ("127.0.0.1", 8080)
        }
    )
    
    with pytest.raises(Exception):
        security_middleware(request, security_middleware.app)
    
    # Test with invalid encoding
    request = Request(
        scope={
            "type": "http",
            "headers": Headers({
                "host": "localhost",
                "content-encoding": "invalid"
            }).raw,
            "client": ("127.0.0.1", 8080)
        }
    )
    
    with pytest.raises(Exception):
        security_middleware(request, security_middleware.app)
    
    # Test with invalid Content-Type
    request = Request(
        scope={
            "type": "http",
            "headers": Headers({
                "host": "localhost",
                "content-type": "invalid/type"
            }).raw,
            "client": ("127.0.0.1", 8080)
        }
    )
    
    with pytest.raises(Exception):
        security_middleware(request, security_middleware.app)
    
    # Test with invalid method
    request = Request(
        scope={
            "type": "http",
            "headers": Headers({"host": "localhost"}).raw,
            "client": ("127.0.0.1", 8080),
            "method": "INVALID"
        }
    )
    
    with pytest.raises(Exception):
        security_middleware(request, security_middleware.app)

def test_ip_blacklist(security_middleware: SecurityMiddleware):
    """Test IP blacklist functionality."""
    response = test_request(headers={"host": "localhost"}, client=("192.168.1.1", 8080))
    assert response.status_code == 403

def test_ip_whitelist(security_middleware: SecurityMiddleware):
    """Test IP whitelist functionality."""
    response = test_request(headers={"host": "localhost"}, client=("192.168.1.2", 8080))
    assert response.status_code == 200
    
    # Test non-whitelisted IP
    response = test_request(headers={"host": "localhost"}, client=("192.168.1.3", 8080))
    assert response.status_code == 403

def test_monitoring_integration(security_middleware: SecurityMiddleware):
    """Test monitoring integration."""
    with patch("mcp.core.monitoring.monitor.increment_event") as mock_increment:
        response = test_request(headers={"host": "localhost"})
        
        # Verify security request processed event
        mock_increment.assert_any_call('security_request_processed')
        
        # Verify security headers added event
        mock_increment.assert_any_call('security_headers_added')
