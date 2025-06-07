"""
Global pytest configuration and fixtures.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from starlette.datastructures import Headers
from mcp_project_backend.mcp.api.middleware.security import SecurityMiddleware
from mcp_project_backend.mcp.core.config import settings
from mcp_project_backend.mcp.core.monitoring import monitor
from unittest.mock import Mock, patch

@pytest.fixture
def mock_settings():
    """Mock settings for testing."""
    class MockSettings:
        ALLOWED_HOSTS = ["localhost", "127.0.0.1"]
        CONTENT_SECURITY_POLICY = "default-src 'self'"
        XSS_PROTECTION = True
        RATE_LIMITING = True
        RATE_LIMIT_WINDOW = 60
        RATE_LIMIT_COUNT = 100
        INPUT_SANITIZATION = True
        IP_BLACKLIST = ["192.168.1.1"]
        IP_WHITELIST = ["192.168.1.2"]
        
    return MockSettings()

@pytest.fixture
def mock_monitor():
    """Mock monitoring instance for testing."""
    class MockMonitor:
        def increment_event(self, event: str, labels: dict = None) -> None:
            pass
    
    return MockMonitor()

@pytest.fixture
def mock_app():
    """Mock FastAPI app for testing."""
    app = FastAPI()
    
    @app.get("/test")
    async def test_endpoint():
        return {"message": "Test successful"}
    
    @app.post("/test")
    async def test_post_endpoint(data: dict):
        return {"received": data}
    
    return app

@pytest.fixture
def security_middleware(mock_app, mock_settings, mock_monitor):
    """Create an instance of SecurityMiddleware for testing."""
    return SecurityMiddleware(mock_app)

@pytest.fixture
def test_client(security_middleware):
    """Create a TestClient instance for testing."""
    return TestClient(security_middleware)

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
