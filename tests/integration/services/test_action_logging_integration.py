"""
Integration tests for action logging in CRUD operations and workflow engine.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime

from mcp.db.models import MCPDefinition, WorkflowRun
from mcp.db.models.action_log import ActionLog, ActionType, EntityType
from mcp.db.models.workflow import WorkflowRunStatus

# Helper functions to create test data
def create_test_mcp_definition(db: Session, name: str = "Test MCP") -> MCPDefinition:
    mcp_def = MCPDefinition(name=name, description="A test MCP definition")
    db.add(mcp_def)
    db.commit()
    db.refresh(mcp_def)
    return mcp_def

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

def test_mcp_definition_crud_logging(test_client: TestClient, db_session: Session):
    """Test action logging for MCP definition CRUD operations."""
    # Create MCP definition
    response = test_client.post(
        "/api/v1/mcp-definitions/",
        json={"name": "Test MCP", "description": "Test description"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    mcp_id = response.json()["id"]
    
    # Verify create log entry
    create_log = db_session.query(ActionLog).filter_by(
        action_type=ActionType.CREATE,
        entity_type=EntityType.MCP_DEFINITION,
        entity_id=mcp_id
    ).first()
    assert create_log is not None
    assert create_log.details["name"] == "Test MCP"
    
    # Update MCP definition
    response = test_client.put(
        f"/api/v1/mcp-definitions/{mcp_id}",
        json={"name": "Updated MCP", "description": "Updated description"}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify update log entry
    update_log = db_session.query(ActionLog).filter_by(
        action_type=ActionType.UPDATE,
        entity_type=EntityType.MCP_DEFINITION,
        entity_id=mcp_id
    ).first()
    assert update_log is not None
    assert update_log.details["name"] == "Updated MCP"
    
    # Delete MCP definition
    response = test_client.delete(f"/api/v1/mcp-definitions/{mcp_id}")
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify delete log entry
    delete_log = db_session.query(ActionLog).filter_by(
        action_type=ActionType.DELETE,
        entity_type=EntityType.MCP_DEFINITION,
        entity_id=mcp_id
    ).first()
    assert delete_log is not None

def test_workflow_run_logging(test_client: TestClient, db_session: Session):
    """Test action logging for workflow run operations."""
    # Create a workflow run
    response = test_client.post(
        "/api/v1/workflow-runs/",
        json={"workflow_definition_id": 1, "parameters": {}}
    )
    assert response.status_code == status.HTTP_201_CREATED
    run_id = response.json()["id"]
    
    # Verify workflow start log entry
    start_log = db_session.query(ActionLog).filter_by(
        action_type=ActionType.CREATE,
        entity_type=EntityType.WORKFLOW_RUN,
        entity_id=run_id
    ).first()
    assert start_log is not None
    assert start_log.details["status"] == WorkflowRunStatus.PENDING.value
    
    # Update workflow status
    response = test_client.patch(
        f"/api/v1/workflow-runs/{run_id}/status",
        json={"status": WorkflowRunStatus.RUNNING.value}
    )
    assert response.status_code == status.HTTP_200_OK
    
    # Verify status update log entry
    status_log = db_session.query(ActionLog).filter_by(
        action_type=ActionType.UPDATE,
        entity_type=EntityType.WORKFLOW_RUN,
        entity_id=run_id
    ).first()
    assert status_log is not None
    assert status_log.details["status"] == WorkflowRunStatus.RUNNING.value

def test_actor_id_capture(test_client: TestClient, db_session: Session):
    """Test that actor_id is captured from the request context."""
    # Create MCP definition with a specific actor
    response = test_client.post(
        "/api/v1/mcp-definitions/",
        json={"name": "Test MCP", "description": "Test description"},
        headers={"X-User-ID": "test_user_123"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    mcp_id = response.json()["id"]
    
    # Verify actor_id in log entry
    log_entry = db_session.query(ActionLog).filter_by(
        entity_type=EntityType.MCP_DEFINITION,
        entity_id=mcp_id
    ).first()
    assert log_entry is not None
    assert log_entry.actor_id == "test_user_123"

def test_log_entry_ordering(test_client: TestClient, db_session: Session):
    """Test that log entries are properly ordered by timestamp."""
    # Create multiple MCP definitions
    for i in range(3):
        response = test_client.post(
            "/api/v1/mcp-definitions/",
            json={"name": f"Test MCP {i}", "description": f"Description {i}"}
        )
        assert response.status_code == status.HTTP_201_CREATED
    
    # Get all log entries
    log_entries = db_session.query(ActionLog).order_by(ActionLog.timestamp.desc()).all()
    
    # Verify ordering (newest first)
    assert len(log_entries) >= 3
    for i in range(len(log_entries) - 1):
        assert log_entries[i].timestamp >= log_entries[i + 1].timestamp 