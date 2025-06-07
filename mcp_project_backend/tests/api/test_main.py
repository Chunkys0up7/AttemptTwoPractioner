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

def test_metrics_report_and_reset(client):
    # Test /metrics/report returns metrics and alerts
    response = client.get("/api/v1/metrics/report")
    assert response.status_code == 200
    data = response.json()
    assert "metrics" in data
    assert "alerts" in data

    # Test /metrics/reset resets metrics (should always succeed)
    response = client.post("/api/v1/metrics/reset")
    assert response.status_code == 200
    assert response.json()["message"] == "Performance metrics reset."

def test_change_password_success_and_failure(client, db_session):
    # Create a test user with a known password
    from mcp.core.core_security import hash_password
    from mcp.db.models.user import User
    test_user = User(email="test@example.com", hashed_password=hash_password("oldpass"))
    db_session.add(test_user)
    db_session.commit()

    # Patch dependency to use test_user
    import mcp.api.services.auth_service as auth_service
    auth_service.Depends = lambda x: (lambda: test_user) if x.__name__ == '<lambda>' else x

    # Test successful password change
    response = client.post("/api/v1/auth/change-password", json={"current_password": "oldpass", "new_password": "newpass"})
    assert response.status_code == 200
    assert response.json()["message"] == "Password changed successfully"

    # Test failure with wrong current password
    response = client.post("/api/v1/auth/change-password", json={"current_password": "wrongpass", "new_password": "newpass2"})
    assert response.status_code == 401
    assert response.json()["detail"] == "Current password is incorrect" 