"""
Global pytest configuration and fixtures.
"""
import pytest
import pytest
import os
from pathlib import Path
from typing import Dict, Any

# Environment Setup
os.environ['TESTING'] = 'true'

# Core Imports
from fastapi import FastAPI, Request
from fastapi.testclient import TestClient
from starlette.datastructures import Headers
from starlette.middleware.base import BaseHTTPMiddleware
from tests.config.env_config import TEST_CONFIG

# Mocks
from unittest.mock import Mock, patch, MagicMock

# Application Imports
from mcp.api.middleware.security import SecurityMiddleware

# Test Configuration
from tests.utils.test_utils import get_test_data

# Mock SecurityMiddleware
SecurityMiddleware = MagicMock()

# Mock security middleware
class MockSecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        return await call_next(request)

# Configuration Fixtures

@pytest.fixture(scope="session")
def test_config():
    """Return test configuration."""
    return TEST_CONFIG

@pytest.fixture(scope="session")
def test_settings():
    """Return test settings."""
    return {
        "RATE_LIMIT_MAX_REQUESTS": 100,
        "RATE_LIMIT_WINDOW": 60,
        "SECURITY_HEADERS": {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
    }

@pytest.fixture(scope="session")
def test_settings():
    """Return test settings."""
    return {
        "RATE_LIMIT_MAX_REQUESTS": 100,
        "RATE_LIMIT_WINDOW": 60,
        "SECURITY_HEADERS": {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains"
        }
    }

# Request Fixtures

@pytest.fixture(scope="session")
def test_headers():
    """Return test request headers."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Host": "localhost",
        "Origin": "http://localhost",
        "Referer": "http://localhost"
    }

@pytest.fixture(scope="session")
def test_security_headers():
    """Return test security headers."""
    return {
        "X-CSRF-Token": "test-token",
        "Authorization": "Bearer test-token"
    }

@pytest.fixture(scope="session")
def test_security_headers():
    """Return test security headers."""
    return {
        "X-CSRF-Token": "test-token",
        "Authorization": "Bearer test-token"
    }

# Mock Fixtures

@pytest.fixture(scope="session")
def mock_monitor():
    """Mock monitoring instance for testing."""
    class MockMonitor:
        def __getattr__(self, name):
            return lambda *args, **kwargs: None
    
    return MockMonitor()

@pytest.fixture(scope="session")
def mock_security_middleware():
    """Mock security middleware."""
    class MockSecurityMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            return await call_next(request)
    
    return MockSecurityMiddleware()

# Application Fixtures

@pytest.fixture(scope="session")
def mock_app(test_config, test_settings, mock_monitor):
    """Mock FastAPI app for testing."""
    app = FastAPI(
        title="MCP Backend API (Test)",
        description="API for managing MCP workflows and executions (Test Mode).",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
        openapi_url=None
    )
    
    # Add middleware
    app.add_middleware(mock_security_middleware)
    
    # Add test routes
    @app.get("/test")
    async def test_endpoint():
        return {"message": "Test successful"}
    
    @app.post("/test")
    async def test_post_endpoint(request: Request):
        return {"received": await request.json()}
    
    @app.get("/protected")
    async def protected_endpoint():
        return {"message": "Protected endpoint"}
    
    return app

@pytest.fixture(scope="session")
def test_client(mock_app):
    """Create a TestClient instance for testing."""
    return TestClient(mock_app)

@pytest.fixture(scope="session")
def test_client(mock_app):
    """Create a TestClient instance for testing."""
    return TestClient(mock_app)

# Helper Fixtures

@pytest.fixture(scope="session")
def test_request(test_client, test_headers, test_security_headers):
    """Create a test request helper."""
    def _test_request(method, path, headers=None, json=None):
        """Helper function to make test requests."""
        if headers is None:
            headers = Headers({
                **test_headers,
                **test_security_headers
            })
        
        if method.lower() == "get":
            return test_client.get(path, headers=headers)
        elif method.lower() == "post":
            return test_client.post(path, headers=headers, json=json)
        elif method.lower() == "put":
            return test_client.put(path, headers=headers, json=json)
        elif method.lower() == "delete":
            return test_client.delete(path, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
    
    return _test_request

@pytest.fixture(scope="session")
def test_data_dir():
    """Return test data directory path."""
    return Path(os.getenv('TEST_DATA_DIR', 'tests/data'))

@pytest.fixture(scope="session")
def test_reports_dir():
    """Return test reports directory path."""
    return Path(os.getenv('TEST_REPORTS_DIR', 'tests/reports'))

# Helper function for accessing request in route handlers
def get_request():
    """Helper to get the request object."""
    return request

@pytest.fixture(scope="session")
def test_request(test_client, test_headers, test_security_headers):
    """Create a test request helper."""
    def _test_request(method, path, headers=None, json=None):
        """Helper function to make test requests."""
        if headers is None:
            headers = Headers({
                **test_headers,
                **test_security_headers
            })
        
        if method.lower() == "get":
            return test_client.get(path, headers=headers)
        elif method.lower() == "post":
            return test_client.post(path, headers=headers, json=json)
        elif method.lower() == "put":
            return test_client.put(path, headers=headers, json=json)
        elif method.lower() == "delete":
            return test_client.delete(path, headers=headers)
        else:
            raise ValueError(f"Unsupported method: {method}")
    
    return _test_request

@pytest.fixture(scope="session")
def test_data_dir():
    """Return test data directory path."""
    return Path("tests/data")
    return Path(os.getenv('TEST_DATA_DIR', 'tests/data'))

@pytest.fixture(scope="session")
def test_reports_dir():
    """Return test reports directory path."""
    return Path(os.getenv('TEST_REPORTS_DIR', 'tests/reports'))
