"""
Tests for the main FastAPI application, specifically health checks and basic startup.
"""
from fastapi.testclient import TestClient
# Adjust the import path based on your project structure and how you run tests
# This assumes 'mcp_project_backend' is on the PYTHONPATH or you run pytest from there.
from mcp.api.main import app, settings

client = TestClient(app)

def test_health_check():
    """Test the /health endpoint for a successful response and correct content."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app_name": settings.APP_NAME}

# Example of how to potentially test with a different .env for tests if needed
# You might use pytest fixtures or a conftest.py to manage settings for tests.
def test_health_check_debug_mode(monkeypatch):
    """
    Test the /health endpoint behavior when application settings (e.g., APP_NAME via settings)
    are modified at runtime using monkeypatching.

    This demonstrates how tests can alter configurations for specific scenarios.
    Note: Monkeypatching settings that are used at module import time or by FastAPI
    during its instantiation might require re-initialization of the TestClient or app
    if those settings are not read dynamically per request by the endpoint logic.
    """
    # This is just an example, actual modification of settings post-import can be tricky.
    # Better to use environment variables or .env files specific to test environments.
    monkeypatch.setattr(settings, 'APP_NAME', "MCP Backend - Test Mode")
    
    # Re-initialize client if app definition depends on settings at import time
    # For this simple case, it might not be necessary if settings are read dynamically by endpoint
    # test_client = TestClient(app) 
    
    response = client.get("/health")
    assert response.status_code == 200
    # Note: The app_name might still be the original one if FastAPI captures it at startup
    # and doesn't re-evaluate settings.APP_NAME per request for the title.
    # The endpoint itself, however, should read the current settings.APP_NAME.
    assert response.json() == {"status": "ok", "app_name": "MCP Backend - Test Mode"}

    # Clean up monkeypatch or ensure settings are reset if they affect other tests.
    # Pytest typically handles this for function-scoped fixtures. 