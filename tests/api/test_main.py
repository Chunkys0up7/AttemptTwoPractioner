"""
Tests for the main API endpoints.
"""
import pytest
from pathlib import Path
from fastapi.testclient import TestClient
import sys
import os

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

@pytest.fixture
def test_data():
    """Test data fixture."""
    return {
        "mcp": {
            "name": "test_mcp",
            "description": "test description"
        },
        "workflow": {
            "name": "test_workflow",
            "steps": []
        }
    }

def test_health_check(test_client):
    """Test the health check endpoint."""
    response = test_client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "app_name": settings.APP_NAME}
    print("Health check endpoint verified")

def test_mcp_crud_routes(test_client, test_data):
    """Test MCP CRUD routes."""
    # Test list endpoint
    response = test_client.get("/api/v1/mcp-definitions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test create endpoint with valid data
    test_data = test_data["mcp"]
    response = test_client.post("/api/v1/mcp-definitions/", json=test_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == test_data["name"]
    assert response.json()["description"] == test_data["description"]
    mcp_id = response.json()["id"]
    
    # Test create with duplicate name (should fail)
    response = test_client.post("/api/v1/mcp-definitions/", json=test_data)
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"]
    
    # Test create with invalid data
    invalid_data = {"name": "", "description": "invalid"}
    response = test_client.post("/api/v1/mcp-definitions/", json=invalid_data)
    assert response.status_code == 400
    assert "required" in response.json()["detail"]
    
    # Test get endpoint
    response = test_client.get(f"/api/v1/mcp-definitions/{mcp_id}")
    assert response.status_code == 200
    assert response.json()["id"] == mcp_id
    assert response.json()["name"] == test_data["name"]
    assert response.json()["description"] == test_data["description"]
    
    # Test get non-existent MCP
    response = test_client.get("/api/v1/mcp-definitions/nonexistent")
    assert response.status_code == 404
    
    # Test update endpoint
    update_data = {
        "description": "updated description",
        "name": "updated name"
    }
    response = test_client.put(f"/api/v1/mcp-definitions/{mcp_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["description"] == "updated description"
    assert response.json()["name"] == "updated name"
    
    # Test update with invalid data
    invalid_update = {"name": ""}
    response = test_client.put(f"/api/v1/mcp-definitions/{mcp_id}", json=invalid_update)
    assert response.status_code == 400
    
    # Test update non-existent MCP
    response = test_client.put("/api/v1/mcp-definitions/nonexistent", json=update_data)
    assert response.status_code == 404
    
    # Test delete endpoint
    response = test_client.delete(f"/api/v1/mcp-definitions/{mcp_id}")
    assert response.status_code == 204
    
    # Verify deletion
    response = test_client.get(f"/api/v1/mcp-definitions/{mcp_id}")
    assert response.status_code == 404
    
    # Test delete non-existent MCP
    response = test_client.delete("/api/v1/mcp-definitions/nonexistent")
    assert response.status_code == 404
    
    print("MCP CRUD routes verified with comprehensive test cases")

def test_mcp_version_routes(test_client, test_data):
    """Test MCP version CRUD routes."""
    # Create a MCP first
    test_data = test_data["mcp"]
    response = test_client.post("/api/v1/mcp-definitions/", json=test_data)
    assert response.status_code == 201
    mcp_id = response.json()["id"]
    
    # Test create version
    version_data = {
        "mcp_type": "test_type",
        "config_payload_data": {"key": "value"}
    }
    response = test_client.post(f"/api/v1/mcp-definitions/{mcp_id}/versions/", json=version_data)
    assert response.status_code == 201
    assert "id" in response.json()
    assert "version_number" in response.json()
    version_id = response.json()["id"]
    
    # Test create version with invalid MCP
    response = test_client.post("/api/v1/mcp-definitions/nonexistent/versions/", json=version_data)
    assert response.status_code == 404
    
    # Test create version with invalid data
    invalid_version = {"mcp_type": ""}
    response = test_client.post(f"/api/v1/mcp-definitions/{mcp_id}/versions/", json=invalid_version)
    assert response.status_code == 400
    
    # Test list versions
    response = test_client.get(f"/api/v1/mcp-definitions/{mcp_id}/versions/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test list versions for non-existent MCP
    response = test_client.get("/api/v1/mcp-definitions/nonexistent/versions/")
    assert response.status_code == 404
    
    # Test get version
    response = test_client.get(f"/api/v1/mcp-definitions/versions/{version_id}")
    assert response.status_code == 200
    assert response.json()["id"] == version_id
    
    # Test get non-existent version
    response = test_client.get("/api/v1/mcp-definitions/versions/nonexistent")
    assert response.status_code == 404
    
    # Test update version
    update_version = {
        "mcp_type": "updated_type",
        "config_payload_data": {"updated": "value"}
    }
    response = test_client.put(f"/api/v1/mcp-definitions/{mcp_id}/versions/{version_id}", json=update_version)
    assert response.status_code == 200
    assert response.json()["mcp_type"] == "updated_type"
    
    # Test update version with invalid MCP
    response = test_client.put("/api/v1/mcp-definitions/nonexistent/versions/{version_id}", json=update_version)
    assert response.status_code == 404
    
    # Test update non-existent version
    response = test_client.put(f"/api/v1/mcp-definitions/{mcp_id}/versions/nonexistent", json=update_version)
    assert response.status_code == 404
    
    # Test delete version
    response = test_client.delete(f"/api/v1/mcp-definitions/{mcp_id}/versions/{version_id}")
    assert response.status_code == 204
    
    # Test delete non-existent version
    response = test_client.delete("/api/v1/mcp-definitions/{mcp_id}/versions/nonexistent")
    assert response.status_code == 404
    
    print("MCP version routes verified with comprehensive test cases")

def test_workflow_execution_routes(test_client, test_data):
    """Test workflow execution routes."""
    # Test list workflows
    response = test_client.get("/api/v1/workflows/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test create workflow
    test_data = test_data["workflow"]
    response = test_client.post("/api/v1/workflows/", json=test_data)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == test_data["name"]
    assert response.json()["steps"] == test_data["steps"]
    
    # Test get workflow
    workflow_id = response.json()["id"]
    response = test_client.get(f"/api/v1/workflows/{workflow_id}")
    assert response.status_code == 200
    assert response.json()["id"] == workflow_id
    assert response.json()["name"] == test_data["name"]
    assert response.json()["steps"] == test_data["steps"]
    
    # Test delete workflow
    response = test_client.delete(f"/api/v1/workflows/{workflow_id}")
    assert response.status_code == 200
    
    # Verify deletion
    response = test_client.get(f"/api/v1/workflows/{workflow_id}")
    assert response.status_code == 404
    
    print("Workflow execution routes verified")

def test_external_db_config_routes(test_client):
    """Test external database configuration routes."""
    # Test list configs
    response = test_client.get("/api/v1/db-configs/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)
    
    # Test create config
    test_config = {
        "name": "test_db",
        "type": "postgresql",
        "connection_string": "postgresql://user:pass@localhost/test"
    }
    response = test_client.post("/api/v1/db-configs/", json=test_config)
    assert response.status_code == 200
    assert "id" in response.json()
    assert response.json()["name"] == test_config["name"]
    assert response.json()["type"] == test_config["type"]
    
    # Test get config
    config_id = response.json()["id"]
    response = test_client.get(f"/api/v1/db-configs/{config_id}")
    assert response.status_code == 200
    assert response.json()["id"] == config_id
    assert response.json()["name"] == test_config["name"]
    assert response.json()["type"] == test_config["type"]
    
    # Test delete config
    response = test_client.delete(f"/api/v1/db-configs/{config_id}")
    assert response.status_code == 200
    
    # Verify deletion
    response = test_client.get(f"/api/v1/db-configs/{config_id}")
    assert response.status_code == 404
    
    print("External DB config routes verified")

def test_dashboard_routes(test_client):
    """Test dashboard routes."""
    # Test dashboard data
    response = test_client.get("/api/v1/dashboard/")
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    
    # Verify dashboard data structure
    dashboard_data = response.json()
    assert "mcp_count" in dashboard_data
    assert "workflow_count" in dashboard_data
    assert "recent_workflows" in dashboard_data
    assert isinstance(dashboard_data["mcp_count"], int)
    assert isinstance(dashboard_data["workflow_count"], int)
    assert isinstance(dashboard_data["recent_workflows"], list)
    
    print("Dashboard routes verified")
