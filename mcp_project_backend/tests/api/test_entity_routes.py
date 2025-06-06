"""
Tests for the heterogeneous entity details endpoint.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from mcp.db.models import MCPDefinition, MCPVersion, WorkflowRun
from mcp.db.models.workflow import WorkflowRunStatus

# Helper functions to create test data
def create_test_mcp_definition(db: Session, name: str = "Test MCP") -> MCPDefinition:
    mcp_def = MCPDefinition(name=name, description="A test MCP definition")
    db.add(mcp_def)
    db.commit()
    db.refresh(mcp_def)
    return mcp_def

def create_test_mcp_version(db: Session, mcp_def_id: int) -> MCPVersion:
    mcp_version = MCPVersion(
        mcp_definition_id=mcp_def_id,
        version="1.0.0",
        description="Test version"
    )
    db.add(mcp_version)
    db.commit()
    db.refresh(mcp_version)
    return mcp_version

def create_test_workflow_run(db: Session) -> WorkflowRun:
    run = WorkflowRun(
        workflow_definition_id=1,  # Placeholder ID
        status=WorkflowRunStatus.RUNNING,
        created_at=datetime.utcnow()
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

def test_get_mcp_version_details(test_client: TestClient, db_session: Session):
    """Test getting details for an MCP version."""
    # Create test data
    mcp_def = create_test_mcp_definition(db_session)
    mcp_version = create_test_mcp_version(db_session, mcp_def.id)
    
    # Get entity details
    response = test_client.get(f"/api/v1/entities/mcp_version/{mcp_version.id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == mcp_version.id
    assert data["version"] == mcp_version.version
    assert data["mcp_definition_id"] == mcp_def.id

def test_get_workflow_run_details(test_client: TestClient, db_session: Session):
    """Test getting details for a workflow run."""
    # Create test data
    workflow_run = create_test_workflow_run(db_session)
    
    # Get entity details
    response = test_client.get(f"/api/v1/entities/workflow_run/{workflow_run.id}")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["id"] == workflow_run.id
    assert data["status"] == workflow_run.status.value
    assert "created_at" in data

def test_get_nonexistent_entity(test_client: TestClient):
    """Test getting details for a nonexistent entity."""
    response = test_client.get("/api/v1/entities/mcp_version/999")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "not found" in response.json()["detail"].lower()

def test_get_invalid_entity_type(test_client: TestClient):
    """Test getting details with an invalid entity type."""
    response = test_client.get("/api/v1/entities/invalid_type/1")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "invalid entity type" in response.json()["detail"].lower()

def test_get_entity_with_invalid_id(test_client: TestClient):
    """Test getting details with an invalid entity ID."""
    response = test_client.get("/api/v1/entities/mcp_version/invalid_id")
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert "validation error" in response.json()["detail"][0]["msg"].lower() 