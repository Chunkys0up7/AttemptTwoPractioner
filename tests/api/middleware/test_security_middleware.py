"""
Comprehensive test suite for Security Middleware.

This module contains unit and integration tests for the Security Middleware component.
It covers all security features including host validation, XSS protection,
rate limiting, IP blacklisting/whitelisting, and monitoring integration.
"""
import pytest
import os

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

# Import after setting TESTING
from mcp.api.middleware.security import SecurityMiddleware
from mcp.core.config import settings
from mcp.core.monitoring import monitor
from fastapi import FastAPI
from fastapi.testclient import TestClient
from .test_utils import (
    TestRequest,
    create_test_headers,
    assert_security_headers,
    assert_rate_limit_headers,
    create_test_client,
    create_test_app,
    create_test_settings
)

@pytest.fixture
def test_client() -> TestClient:
    """Create a test client with security middleware."""
    app = create_test_app()
    return create_test_client(app)

@pytest.fixture
def test_request(test_client: TestClient) -> TestRequest:
    """Create a test request helper."""
    return TestRequest(test_client)

@pytest.fixture
def test_settings() -> dict:
    """Test settings fixture."""
    return create_test_settings()

@pytest.mark.unit
@pytest.mark.security
def test_valid_host_header(test_request: TestRequest, test_settings: dict):
    """Test valid host header.
    
    This test verifies that requests with valid host headers are allowed through.
    """
    headers = create_test_headers(host="localhost")
    response = test_request.get("/", headers=headers)
    assert response["status_code"] == 200
    assert response["json"] == {"message": "Test successful"}

@pytest.mark.unit
@pytest.mark.security
def test_invalid_host_header(test_request: TestRequest, test_settings: dict):
    """Test invalid host header.
    
    This test verifies that requests with invalid host headers are blocked.
    """
    headers = create_test_headers(host="malicious.com")
    response = test_request.get("/", headers=headers)
    assert response["status_code"] == 400
    assert "invalid host" in str(response["content"]).lower()

@pytest.mark.unit
@pytest.mark.security
def test_csp_headers(test_request: TestRequest, test_settings: dict):
    """Test CSP headers.
    
    This test verifies that Content Security Policy headers are properly set.
    """
    response = test_request.get("/")
    expected_headers = {
        "Content-Security-Policy": test_settings["CSP_POLICY"]
    }
    assert_security_headers(response, expected_headers)

@pytest.mark.unit
@pytest.mark.security
def test_xss_protection(test_request: TestRequest, test_settings: dict):
    """Test XSS protection.
    
    This test verifies that XSS protection headers are properly set.
    """
    response = test_request.get("/")
    expected_headers = {
        "X-XSS-Protection": test_settings["XSS_PROTECTION"]
    }
    assert_security_headers(response, expected_headers)

@pytest.mark.unit
@pytest.mark.security
def test_rate_limiting(test_request: TestRequest, test_settings: dict):
    """Test rate limiting.
    
    This test verifies that rate limiting is properly enforced.
    """
    # Make 11 requests to trigger rate limiting
    for i in range(11):
        response = test_request.get("/")
        if response["status_code"] == 429:
            break
    
    assert response["status_code"] == 429
    assert "rate limit" in str(response["content"]).lower()
    assert_rate_limit_headers(response)

@pytest.mark.unit
@pytest.mark.security
def test_ip_blacklisting(test_request: TestRequest, test_settings: dict):
    """Test IP blacklisting.
    
    This test verifies that requests from blacklisted IPs are blocked.
    """
    headers = create_test_headers(ip="192.168.1.100")
    response = test_request.get("/", headers=headers)
    assert response["status_code"] == 403
    assert "blacklisted" in str(response["content"]).lower()

@pytest.mark.unit
@pytest.mark.security
def test_ip_whitelisting(test_request: TestRequest, test_settings: dict):
    """Test IP whitelisting.
    
    This test verifies that whitelisting works correctly.
    """
    # Blacklisted IP should be blocked
    headers = create_test_headers(ip="192.168.1.100")
    response = test_request.get("/", headers=headers)
    assert response["status_code"] == 403

    # Whitelisted IP should be allowed
    headers = create_test_headers(ip="127.0.0.1")
    response = test_request.get("/", headers=headers)
    assert response["status_code"] == 200

@pytest.mark.unit
@pytest.mark.security
def test_input_sanitization(test_request: TestRequest, test_settings: dict):
    """Test input sanitization.
    
    This test verifies that potentially malicious input is properly sanitized.
    """
    # Test with potentially malicious input
    response = test_request.post("/test", data={"data": "<script>alert('xss')</script>"})
    assert response["status_code"] == 200
    assert "<script>" not in str(response["content"])

@pytest.mark.integration
@pytest.mark.security
def test_monitoring_integration(test_request: TestRequest, test_settings: dict):
    """Test monitoring integration.
    
    This test verifies that security events are properly monitored.
    """
    response = test_request.get("/")
    assert response["status_code"] == 200
    # Verify monitoring metrics are collected
    assert monitor.metrics
    assert "security" in str(monitor.metrics)

@pytest.mark.performance
def test_performance(test_request: TestRequest, test_settings: dict):
    """Test performance characteristics.
    
    This test verifies that the middleware doesn't introduce significant latency.
    """
    import time
    start = time.time()
    response = test_request.get("/")
    end = time.time()
    assert response["status_code"] == 200
    # Ensure response time is within acceptable limit
    assert (end - start) < 0.1  # 100ms response time
    # Verify response content
    assert response["json"] == {"message": "Test successful"}
