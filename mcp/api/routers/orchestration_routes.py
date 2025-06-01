from fastapi import APIRouter, Depends, HTTPException
from mcp.core.orchestration.prefect_service import prefect_service
from mcp.api.routers.auth_routes import require_role, get_current_user
from mcp.db.models.user import User
from typing import Dict, Any

router = APIRouter()

@router.post("/orchestration/register")
def register_workflow(name: str, db: Any = None, current_user: User = Depends(require_role("Admin"))):
    # Placeholder: In real use, would accept/upload a flow definition
    # For now, just log registration
    prefect_service.register_workflow(name, flow_func=None)
    return {"detail": f"Workflow '{name}' registered"}

@router.post("/orchestration/trigger")
def trigger_workflow(name: str, params: Dict[str, Any]):
    run_id = prefect_service.trigger_workflow(name, params)
    return {"run_id": run_id}

@router.get("/orchestration/status/{run_id}")
def get_workflow_status(run_id: str):
    status = prefect_service.get_workflow_status(run_id)
    return status

@router.post("/orchestration/log-event")
def log_workflow_event(run_id: str, event: str, details: str = ""):
    prefect_service.log_workflow_event(run_id, event, details)
    return {"detail": "Event logged"}

@router.post("/orchestration/trace")
def trace_workflow(run_id: str, trace_data: Dict[str, Any]):
    prefect_service.trace_workflow(run_id, trace_data)
    return {"detail": "Trace logged"}

@router.post("/orchestration/elk-log")
def elk_log(run_id: str, log_data: Dict[str, Any]):
    prefect_service.elk_log(run_id, log_data)
    return {"detail": "ELK log entry created"} 