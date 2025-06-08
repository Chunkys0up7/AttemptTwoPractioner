"""
Service layer for dashboard-related data aggregation.
"""
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timezone

from mcp.db.models.mcp import MCPDefinition, MCPVersion
from mcp.db.models.workflow import WorkflowRun, WorkflowRunStatus


class DashboardService:
    def __init__(self, db: Session):
        self.db = db

    async def get_dashboard_summary(self) -> dict:
        """Aggregates various statistics for the dashboard summary."""
        total_mcp_definitions = self.db.query(
            func.count(MCPDefinition.id)).scalar()
        total_mcp_versions = self.db.query(func.count(MCPVersion.id)).scalar()

        total_workflow_runs = self.db.query(
            func.count(WorkflowRun.id)).scalar()
        active_workflow_runs = self.db.query(func.count(WorkflowRun.id))\
            .filter(WorkflowRun.status.in_([WorkflowRunStatus.RUNNING, WorkflowRunStatus.PENDING]))\
            .scalar()

        today_date = datetime.now(timezone.utc).date()

        successful_runs_today = self.db.query(func.count(WorkflowRun.id))\
            .filter(WorkflowRun.status == WorkflowRunStatus.SUCCESS)\
            .filter(func.date(WorkflowRun.ended_at) == today_date)\
            .scalar()

        failed_runs_today = self.db.query(func.count(WorkflowRun.id))\
            .filter(WorkflowRun.status == WorkflowRunStatus.FAILED)\
            .filter(func.date(WorkflowRun.ended_at) == today_date)\
            .scalar()

        return {
            "total_mcp_definitions": total_mcp_definitions or 0,
            "total_mcp_versions": total_mcp_versions or 0,
            "total_workflow_runs": total_workflow_runs or 0,
            "active_workflow_runs": active_workflow_runs or 0,
            "successful_runs_today": successful_runs_today or 0,
            "failed_runs_today": failed_runs_today or 0,
        }
