"""
Tests for Workflow Execution API endpoints.
"""
import pytest
import uuid
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session # For type hinting if needed

from mcp.db.models import WorkflowDefinition, WorkflowRun # Import WorkflowDefinition
from mcp.db.models.workflow import WorkflowRunStatus

# Helper to create a dummy WorkflowDefinition for tests, as we don't have CRUD for it yet.
def create_dummy_workflow_definition(db: Session, name: str = "Test Workflow Def") -> WorkflowDefinition:
    # This is a placeholder. In a real scenario, WorkflowDefinition would have its own CRUD.
    # For now, we'll create it directly in the DB for the test to work.
    wf_def = WorkflowDefinition(name=name, description="A test workflow definition")
    # The initial Alembic migration (12345abcdef0) defines `definition_dsl` as nullable JSONB.
    # So, no need to explicitly set it to {} if the model default works or it can be null.
    # If it were non-nullable and had no server_default, we would need: wf_def.definition_dsl = {}
    db.add(wf_def)
    db.commit()
    db.refresh(wf_def)
    return wf_def

def test_trigger_workflow_run_ok(test_client: TestClient, db_session: Session):
    # Create a dummy WorkflowDefinition because we don't have API for it yet
    # This is a temporary measure for this test.
    workflow_def = create_dummy_workflow_definition(db_session, name="My Test Workflow")
    workflow_def_id = workflow_def.id

    run_params = {"param1": "value1", "param2": 123}
    
    response = test_client.post(f"/api/v1/workflows/{workflow_def_id}/run", json=run_params)
    
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    
    assert data["workflow_definition_id"] == str(workflow_def_id)
    assert data["status"] == WorkflowRunStatus.PENDING.value # Ensure enum value is checked
    assert data["run_parameters"] == run_params
    assert "id" in data
    assert "created_at" in data
    assert "updated_at" in data

    # Verify in DB (optional, but good for confirming service logic)
    run_in_db = db_session.query(WorkflowRun).filter(WorkflowRun.id == data["id"]).first()
    assert run_in_db is not None
    assert run_in_db.status == WorkflowRunStatus.PENDING

def test_trigger_workflow_run_no_params(test_client: TestClient, db_session: Session):
    workflow_def = create_dummy_workflow_definition(db_session, name="Workflow No Params")
    workflow_def_id = workflow_def.id

    response = test_client.post(f"/api/v1/workflows/{workflow_def_id}/run", json=None) # Or simply don't pass json
    assert response.status_code == status.HTTP_202_ACCEPTED
    data = response.json()
    assert data["workflow_definition_id"] == str(workflow_def_id)
    assert data["status"] == WorkflowRunStatus.PENDING.value
    assert data["run_parameters"] == {} # Should default to empty dict

# Placeholder for a test where workflow_definition_id does not exist.
# This requires the WorkflowEngineService to actually check for existence.
# For now, the service and route don't implement this check, so a 404 won't be raised based on non-existence.
# It will proceed and the DB foreign key constraint would fail if workflow_definition_id is totally random and not in DB.
# If service.start_workflow_run is changed to fetch WorkflowDefinition first, this test becomes relevant.

# @pytest.mark.skip(reason="WorkflowDefinition existence check not yet in service")
# def test_trigger_workflow_run_workflow_def_not_found(test_client: TestClient):
#     random_uuid = uuid.uuid4()
#     response = test_client.post(f"/api/v1/workflows/{random_uuid}/run", json={})
#     assert response.status_code == status.HTTP_404_NOT_FOUND
#     assert "WorkflowDefinition with ID" in response.json()["detail"] 