import pytest
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp.core.security.middleware import (
    SecurityHeadersMiddleware,
    RateLimitMiddleware,
    setup_security_middleware
)

# Test app for middleware testing
app = FastAPI()

@app.get("/test-endpoint")
async def test_endpoint():
    return {"message": "success"}

# Add middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RateLimitMiddleware, rate_limit=2, window=1)  # 2 requests per second

client = TestClient(app)

def test_security_headers():
    """Test that security headers are added to responses."""
    response = client.get("/test-endpoint")
    
    # Check security headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert response.headers["X-Frame-Options"] == "DENY"
    assert response.headers["X-XSS-Protection"] == "1; mode=block"
    assert "Strict-Transport-Security" in response.headers
    assert "Content-Security-Policy" in response.headers
    assert "Referrer-Policy" in response.headers
    assert "Permissions-Policy" in response.headers

def test_rate_limiting():
    """Test rate limiting functionality."""
    # Make requests within rate limit
    response1 = client.get("/test-endpoint")
    response2 = client.get("/test-endpoint")
    assert response1.status_code == 200
    assert response2.status_code == 200
    
    # Exceed rate limit
    response3 = client.get("/test-endpoint")
    assert response3.status_code == 429
    assert response3.text == "Rate limit exceeded"
    
    # Wait for rate limit window to expire
    time.sleep(1)
    
    # Should be able to make requests again
    response4 = client.get("/test-endpoint")
    assert response4.status_code == 200

def test_setup_security_middleware():
    """Test the setup_security_middleware function."""
    app = FastAPI()
    setup_security_middleware(app)
    
    # Verify middleware are added
    middleware_classes = [m.__class__.__name__ for m in app.user_middleware]
    assert "SecurityHeadersMiddleware" in middleware_classes
    assert "RateLimitMiddleware" in middleware_classes
    assert "CORSMiddleware" in middleware_classes
    assert "TrustedHostMiddleware" in middleware_classes
    assert "GZipMiddleware" in middleware_classes 