"""
Test suite for workflow definition routes.

This module contains comprehensive unit and integration tests for the workflow definition routes,
covering CRUD operations, validation, error handling, and performance.
"""
import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from mcp.api.routers import workflow_definition_routes
from mcp.schemas import workflow as workflow_schemas
from mcp.core.config import settings
from typing import Dict, Any, List
import json
import os
import time
from datetime import datetime

# Set TESTING environment variable before any imports
os.environ['TESTING'] = 'true'

# Import after setting TESTING
class MockWorkflowValidator:
    """Mock workflow validator for testing."""
    def validate_workflow(self, workflow_data: Dict[str, Any]) -> Dict[str, Any]:
        """Mock validation method."""
        if not workflow_data.get("name"):
            raise ValueError("Workflow name is required")
        if not workflow_data.get("components"):
            raise ValueError("At least one component is required")
        return workflow_data

class MockWorkflowService:
    """Mock workflow service for testing."""
    def __init__(self):
        self.workflows = {}
        self.last_id = 0
        
    async def create_workflow(self, workflow: workflow_schemas.WorkflowCreate):
        """Mock create workflow."""
        self.last_id += 1
        workflow_id = self.last_id
        workflow_data = workflow.dict()
        workflow_data["id"] = workflow_id
        workflow_data["created_at"] = datetime.now().isoformat()
        workflow_data["updated_at"] = datetime.now().isoformat()
        self.workflows[workflow_id] = workflow_data
        return workflow_data
        
    async def get_workflow(self, workflow_id: int):
        """Mock get workflow."""
        return self.workflows.get(workflow_id)
        
    async def update_workflow(self, workflow_id: int, workflow: workflow_schemas.WorkflowUpdate):
        """Mock update workflow."""
        if workflow_id not in self.workflows:
            return None
        
        workflow_data = self.workflows[workflow_id]
        update_data = workflow.dict(exclude_unset=True)
        workflow_data.update(update_data)
        workflow_data["updated_at"] = datetime.now().isoformat()
        return workflow_data
        
    async def delete_workflow(self, workflow_id: int):
        """Mock delete workflow."""
        if workflow_id not in self.workflows:
            return False
        
        del self.workflows[workflow_id]
        return True

def create_test_app():
    """Create a test FastAPI app with workflow routes."""
    app = FastAPI(
        title="MCP Backend API (Test)",
        description="API for managing MCP workflows and executions (Test Mode).",
        version="1.0.0",
        docs_url=None,
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

@pytest.fixture(scope="module")
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
                    "label": "Input 1",
                    "required": True
                }
            },
            {
                "type": "filter",
                "name": "filter1",
                "properties": {
                    "type": "text",
                    "pattern": ".*"
                }
            },
            {
                "type": "output",
                "name": "output1",
                "properties": {
                    "type": "console"
                }
            }
        ],
        "connections": [
            {
                "source": "input1",
                "target": "filter1"
            },
            {
                "source": "filter1",
                "target": "output1"
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
    assert response.json()["description"] == sample_workflow["description"]
    assert len(response.json()["components"]) == 3
    assert len(response.json()["connections"]) == 2
    assert "created_at" in response.json()
    assert "updated_at" in response.json()

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
    assert response.json()["description"] == sample_workflow["description"]
    assert len(response.json()["components"]) == 3
    assert len(response.json()["connections"]) == 2

@pytest.mark.unit
def test_get_nonexistent_workflow(test_client):
    """Test getting a non-existent workflow."""
    response = test_client.get("/workflows/99999")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.unit
def test_update_workflow(test_client, sample_workflow):
    """Test updating a workflow."""
    # Create a workflow first
    create_response = test_client.post("/workflows/", json=sample_workflow)
    workflow_id = create_response.json()["id"]
    
    # Update the workflow
    update_data = {
        "name": "Updated Workflow",
        "description": "Updated description",
        "components": [
            {
                "type": "input",
                "name": "input1",
                "properties": {
                    "label": "Updated Input"
                }
            }
        ]
    }
    response = test_client.put(f"/workflows/{workflow_id}", json=update_data)
    assert response.status_code == 200
    assert response.json()["name"] == "Updated Workflow"
    assert response.json()["description"] == "Updated description"
    assert len(response.json()["components"]) == 1
    assert response.json()["components"][0]["properties"]["label"] == "Updated Input"
    assert response.json()["updated_at"] > response.json()["created_at"]

@pytest.mark.unit
def test_update_nonexistent_workflow(test_client):
    """Test updating a non-existent workflow."""
    update_data = {
        "name": "Updated Workflow",
        "description": "Updated description"
    }
    response = test_client.put("/workflows/99999", json=update_data)
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"].lower()

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
    
    # Verify it's actually deleted
    response = test_client.get(f"/workflows/{workflow_id}")
    assert response.status_code == 404

@pytest.mark.unit
def test_delete_nonexistent_workflow(test_client):
    """Test deleting a non-existent workflow."""
    response = test_client.delete("/workflows/99999")
    assert response.status_code == 404
    assert "detail" in response.json()
    assert "not found" in response.json()["detail"].lower()

@pytest.mark.unit
def test_list_workflows(test_client, sample_workflow):
    """Test listing workflows."""
    # Create multiple workflows
    workflow_ids = []
    for i in range(3):
        workflow_data = sample_workflow.copy()
        workflow_data["name"] = f"Test Workflow {i}"
        response = test_client.post("/workflows/", json=workflow_data)
        workflow_ids.append(response.json()["id"])
    
    # List workflows
    response = test_client.get("/workflows/")
    assert response.status_code == 200
    workflows = response.json()
    assert len(workflows) == 3
    
    # Verify workflow data
    for workflow in workflows:
        assert "id" in workflow
        assert "name" in workflow
        assert "created_at" in workflow
        assert "updated_at" in workflow
        assert workflow["id"] in workflow_ids

@pytest.mark.unit
def test_workflow_validation(test_client, sample_workflow):
    """Test workflow validation."""
    # Test invalid workflow (no name)
    invalid_workflow = sample_workflow.copy()
    invalid_workflow["name"] = ""
    response = test_client.post("/workflows/", json=invalid_workflow)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "Workflow name is required" in response.json()["detail"]
    
    # Test invalid workflow (no components)
    invalid_workflow = sample_workflow.copy()
    invalid_workflow["components"] = []
    response = test_client.post("/workflows/", json=invalid_workflow)
    assert response.status_code == 422
    assert "detail" in response.json()
    assert "At least one component is required" in response.json()["detail"]

@pytest.mark.unit
def test_workflow_pagination(test_client, sample_workflow):
    """Test workflow pagination."""
    # Create more workflows than page size
    workflow_ids = []
    for i in range(25):
        workflow_data = sample_workflow.copy()
        workflow_data["name"] = f"Test Workflow {i}"
        response = test_client.post("/workflows/", json=workflow_data)
        workflow_ids.append(response.json()["id"])
    
    # Test pagination
    response = test_client.get("/workflows/?page=1&size=10")
    assert response.status_code == 200
    pagination = response.json()
    assert len(pagination["items"]) == 10
    assert pagination["total"] == 25
    assert pagination["page"] == 1
    assert pagination["size"] == 10
    assert pagination["pages"] == 3
    
    # Test second page
    response = test_client.get("/workflows/?page=2&size=10")
    assert response.status_code == 200
    pagination = response.json()
    assert len(pagination["items"]) == 10
    assert pagination["total"] == 25
    assert pagination["page"] == 2
    assert pagination["size"] == 10
    assert pagination["pages"] == 3

@pytest.mark.unit
def test_workflow_performance(test_client, sample_workflow):
    """Test workflow performance."""
    # Create multiple workflows
    num_workflows = 100
    start_time = time.time()
    
    for i in range(num_workflows):
        workflow_data = sample_workflow.copy()
        workflow_data["name"] = f"Performance Test {i}"
        response = test_client.post("/workflows/", json=workflow_data)
        assert response.status_code == 201
    
    total_time = time.time() - start_time
    avg_time = total_time / num_workflows
    
    assert avg_time < 0.01  # Should take less than 10ms per workflow on average
    
    # Test listing performance
    start_time = time.time()
    response = test_client.get("/workflows/")
    total_time = time.time() - start_time
    
    assert response.status_code == 200
    assert total_time < 0.1  # Should take less than 100ms to list all workflows

@pytest.mark.unit
def test_workflow_concurrency(test_client, sample_workflow):
    """Test workflow concurrency."""
    import threading
    from queue import Queue
    
    # Create multiple workflows concurrently
    num_threads = 10
    results = Queue()
    
    def create_workflow():
        workflow_data = sample_workflow.copy()
        workflow_data["name"] = f"Concurrent Test {threading.get_ident()}"
        response = test_client.post("/workflows/", json=workflow_data)
        results.put(response)
    
    threads = []
    for _ in range(num_threads):
        thread = threading.Thread(target=create_workflow)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    # Verify results
    while not results.empty():
        response = results.get()
        assert response.status_code == 201
        assert "id" in response.json()
        assert "name" in response.json()

@pytest.mark.unit
def test_workflow_error_handling(test_client, sample_workflow):
    """Test workflow error handling."""
    # Test invalid JSON
    response = test_client.post("/workflows/", data="invalid json")
    assert response.status_code == 422
    assert "detail" in response.json()
    
    # Test invalid method
    response = test_client.delete("/workflows/")
    assert response.status_code == 405
    assert "detail" in response.json()
    
    # Test invalid path
    response = test_client.get("/workflows/invalid")
    assert response.status_code == 422
    assert "detail" in response.json()
