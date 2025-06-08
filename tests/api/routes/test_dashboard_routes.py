"""
Tests for Dashboard API endpoints.
"""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

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

def create_test_workflow_run(
    db: Session,
    status: WorkflowRunStatus,
    created_at: datetime = None,
    ended_at: datetime = None
) -> WorkflowRun:
    run = WorkflowRun(
        workflow_definition_id=1,  # Placeholder ID
        status=status,
        created_at=created_at or datetime.utcnow(),
        ended_at=ended_at
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

def test_get_dashboard_summary_empty_db(test_client: TestClient, db_session: Session):
    """Test dashboard summary with an empty database."""
    response = test_client.get("/api/v1/dashboard/summary")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total_mcp_definitions"] == 0
    assert data["total_mcp_versions"] == 0
    assert data["total_workflow_runs"] == 0
    assert data["active_workflow_runs"] == 0
    assert data["successful_runs_today"] == 0
    assert data["failed_runs_today"] == 0

def test_get_dashboard_summary_with_data(test_client: TestClient, db_session: Session):
    """Test dashboard summary with various data in the database."""
    # Create test data
    mcp_def1 = create_test_mcp_definition(db_session, "Test MCP 1")
    mcp_def2 = create_test_mcp_definition(db_session, "Test MCP 2")
    
    create_test_mcp_version(db_session, mcp_def1.id)
    create_test_mcp_version(db_session, mcp_def1.id)  # Second version
    create_test_mcp_version(db_session, mcp_def2.id)
    
    # Create workflow runs with different statuses
    now = datetime.utcnow()
    today = now.date()
    yesterday = today - timedelta(days=1)
    
    # Active runs
    create_test_workflow_run(db_session, WorkflowRunStatus.RUNNING)
    create_test_workflow_run(db_session, WorkflowRunStatus.PENDING)
    
    # Today's runs
    create_test_workflow_run(
        db_session,
        WorkflowRunStatus.SUCCESS,
        created_at=datetime.combine(today, datetime.min.time()),
        ended_at=datetime.combine(today, datetime.max.time())
    )
    create_test_workflow_run(
        db_session,
        WorkflowRunStatus.FAILED,
        created_at=datetime.combine(today, datetime.min.time()),
        ended_at=datetime.combine(today, datetime.max.time())
    )
    
    # Yesterday's runs (should not be counted in today's stats)
    create_test_workflow_run(
        db_session,
        WorkflowRunStatus.SUCCESS,
        created_at=datetime.combine(yesterday, datetime.min.time()),
        ended_at=datetime.combine(yesterday, datetime.max.time())
    )
    
    # Get dashboard summary
    response = test_client.get("/api/v1/dashboard/summary")
    assert response.status_code == status.HTTP_200_OK
    
    data = response.json()
    assert data["total_mcp_definitions"] == 2
    assert data["total_mcp_versions"] == 3
    assert data["total_workflow_runs"] == 5
    assert data["active_workflow_runs"] == 2  # RUNNING + PENDING
    assert data["successful_runs_today"] == 1
    assert data["failed_runs_today"] == 1

def test_get_dashboard_summary_error_handling(test_client: TestClient, db_session: Session, monkeypatch):
    """Test error handling in dashboard summary endpoint."""
    # Mock the dashboard service to raise an exception
    from mcp.core.services.dashboard_service import DashboardService
    
    def mock_get_summary(*args, **kwargs):
        raise Exception("Test error")
    
    monkeypatch.setattr(DashboardService, "get_dashboard_summary", mock_get_summary)
    
    response = test_client.get("/api/v1/dashboard/summary")
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert "error" in response.json()["detail"].lower() 