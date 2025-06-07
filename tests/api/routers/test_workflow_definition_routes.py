"""
Test suite for workflow definition routes.

This module contains unit and integration tests for the workflow definition routes,
covering CRUD operations and validation.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mcp.api.routers import workflow_definition_routes
from mcp.schemas import workflow as workflow_schemas
from mcp.core.config import settings
from typing import Dict, Any
import json
import os

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

# Import after setting TESTING
class MockWorkflowValidator:
    """Mock workflow validator for testing."""
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock validation method."""
        return workflow_data

class MockWorkflowService:
    """Mock workflow service for testing."""
    def __init__(self):
        self.workflows = {}
        
    async def create_workflow(self, workflow: workflow_schemas.WorkflowCreate):
        """Mock create workflow."""
        workflow_id = len(self.workflows) + 1
        workflow_data = workflow.dict()
        workflow_data["id"] = workflow_id
        self.workflows[workflow_id] = workflow_data
        return workflow_data
        
    async def get_workflow(self, workflow_id: int):
        """Mock get workflow."""
        return self.workflows.get(workflow_id)
        
    async def update_workflow(self, workflow_id: int, workflow: workflow_schemas.WorkflowUpdate):
        """Mock update workflow."""
        if workflow_id in self.workflows:
            self.workflows[workflow_id].update(workflow.dict(exclude_unset=True))
            return self.workflows[workflow_id]
        return None
        
    async def delete_workflow(self, workflow_id: int):
        """Mock delete workflow."""
        if workflow_id in self.workflows:
            del self.workflows[workflow_id]
            return True
        return False

def create_test_app():
    """Create a test FastAPI app with workflow routes."""
    app = FastAPI(
        title="MCP Backend API (Test)",
        description="API for managing MCP workflows and executions (Test Mode).",
        version="1.0.0",
        docs_url=None,  # Disable docs in test mode
        redoc_url=None,
        openapi_url=None
    )
    workflow_service = MockWorkflowService()
    workflow_validator = MockWorkflowValidator()
    
    app.include_router(
        workflow_definition_routes.router,
        prefix="/workflows",
        tags=["workflows"]
    )
    
    # Mock dependencies
    app.dependency_overrides = {
        workflow_definition_routes.get_workflow_service: lambda: workflow_service,
        workflow_definition_routes.get_workflow_validator: lambda: workflow_validator
    }
    return app

@pytest.fixture
def test_client():
    """Create a test client with workflow routes."""
    app = create_test_app()
    return TestClient(app)

@pytest.fixture
def sample_workflow():
    """Sample workflow data for testing."""
    return {
        "name": "Test Workflow",
        "description": "A test workflow",
        "components": [
            {
                "type": "input",
                "name": "input1",
                "properties": {
                    "label": "Input 1"
                }
            }
        ]
    }

@pytest.mark.unit
def test_create_workflow(test_client, sample_workflow):
    """Test creating a workflow."""
    response = test_client.post("/workflows/", json=sample_workflow)
    assert response.status_code == 201
    assert "id" in response.json()
    assert response.json()["name"] == sample_workflow["name"]

@pytest.mark.unit
def test_get_workflow(test_client, sample_workflow):
    """Test getting a workflow."""
    # Create a workflow first
    create_response = test_client.post("/workflows/", json=sample_workflow)
    workflow_id = create_response.json()["id"]
    
    # Get the workflow
    response = test_client.get(f"/workflows/{workflow_id}")
    assert response.status_code == 200
    assert response.json()["id"] == workflow_id
    assert response.json()["name"] == sample_workflow["name"]

@pytest.mark.unit
def test_update_workflow(test_client, sample_workflow):
    """Test updating a workflow."""
    # Create a workflow first
    create_response = test_client.post("/workflows/", json=sample_workflow)
    workflow_id = create_response.json()["id"]
    
    # Update the workflow
    update_data = {
        "name": "Updated Workflow",
        "description": "Updated description"
    }
    response = test_client.put(f"/workflows/{workflow_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Workflow"
    assert response.json()["description"] == "Updated description"

@pytest.mark.unit
def test_delete_workflow(test_client, sample_workflow):
    """Test deleting a workflow."""
    # Create a workflow first
    create_response = test_client.post("/workflows/", json=sample_workflow)
    workflow_id = create_response.json()["id"]
    
    # Delete the workflow
    response = test_client.delete(f"/workflows/{workflow_id}")
    assert response.status_code == 200
    assert response.json()["success"] is True

@pytest.mark.unit
def test_list_workflows(test_client, sample_workflow):
    """Test listing workflows."""
    # Create multiple workflows
    for i in range(3):
        workflow_data = sample_workflow.copy()
        workflow_data["name"] = f"Test Workflow {i}"
        test_client.post("/workflows/", json=workflow_data)
    
    # List workflows
    response = test_client.get("/workflows/")
    assert response.status_code == 200
    assert len(response.json()) == 3

@pytest.mark.unit
def test_workflow_validation(test_client, sample_workflow):
    """Test workflow validation."""
    # Test invalid workflow
    invalid_workflow = sample_workflow.copy()
    invalid_workflow["components"] = []  # Empty components should be invalid
    response = test_client.post("/workflows/", json=invalid_workflow)
    assert response.status_code == 422
    assert "detail" in response.json()

@pytest.mark.unit
def test_workflow_pagination(test_client, sample_workflow):
    """Test workflow pagination."""
    # Create more workflows than page size
    for i in range(20):
        workflow_data = sample_workflow.copy()
        workflow_data["name"] = f"Test Workflow {i}"
        test_client.post("/workflows/", json=workflow_data)
    
    # Test pagination
    response = test_client.get("/workflows/?page=1&size=10")
    assert response.status_code == 200
    assert len(response.json()["items"]) == 10
    assert response.json()["total"] == 20
    assert response.json()["page"] == 1
    assert response.json()["size"] == 10
