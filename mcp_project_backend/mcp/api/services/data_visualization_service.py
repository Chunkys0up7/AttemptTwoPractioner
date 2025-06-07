from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from mcp.db.session import get_db
from mcp.db.models.mcp import MCPDefinition, MCPVersion
from mcp.db.models.workflow import WorkflowRun, WorkflowRunStatus
from datetime import datetime
from sqlalchemy import func

router = APIRouter()

@router.get("/visualization/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    try:
        total_mcp_definitions = db.query(MCPDefinition).count()
        total_mcp_versions = db.query(MCPVersion).count()
        total_workflow_runs = db.query(WorkflowRun).count()
        active_workflow_runs = db.query(WorkflowRun).filter(WorkflowRun.status.in_([WorkflowRunStatus.RUNNING, WorkflowRunStatus.PENDING])).count()
        today_date = datetime.utcnow().date()
        successful_runs_today = db.query(WorkflowRun).filter(WorkflowRun.status == WorkflowRunStatus.SUCCESS).filter(WorkflowRun.ended_at != None).filter(WorkflowRun.ended_at.cast('date') == today_date).count()
        failed_runs_today = db.query(WorkflowRun).filter(WorkflowRun.status == WorkflowRunStatus.FAILED).filter(WorkflowRun.ended_at != None).filter(WorkflowRun.ended_at.cast('date') == today_date).count()
        return {
            "total_mcp_definitions": total_mcp_definitions,
            "total_mcp_versions": total_mcp_versions,
            "total_workflow_runs": total_workflow_runs,
            "active_workflow_runs": active_workflow_runs,
            "successful_runs_today": successful_runs_today,
            "failed_runs_today": failed_runs_today,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error aggregating dashboard summary: {e}")

@router.get("/visualization/chart")
def get_sample_chart(db: Session = Depends(get_db)):
    try:
        # Example: count workflow runs by status for a bar chart
        status_counts = (
            db.query(WorkflowRun.status, func.count(WorkflowRun.id))
            .group_by(WorkflowRun.status)
            .all()
        )
        labels = [status.value for status, _ in status_counts]
        values = [count for _, count in status_counts]
        return {"labels": labels, "values": values}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating chart data: {e}")

@router.get("/visualization/realtime")
def get_realtime_updates():
    # TODO: Implement real-time updates using WebSockets or server-sent events
    return {"message": "Real-time updates not yet implemented"} 