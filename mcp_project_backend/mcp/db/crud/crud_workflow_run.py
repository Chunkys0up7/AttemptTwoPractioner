from sqlalchemy.orm import Session
from .base_crud import CRUDBase
from mcp.db.models.workflow_run import WorkflowRun
from mcp.api.schemas.workflow_run_schemas import WorkflowRunStatusEnum
from typing import Optional, Dict, Any
from datetime import datetime, timezone

class CRUDWorkflowRun(CRUDBase[WorkflowRun, dict, dict]):
    """
    CRUD operations for the WorkflowRun model, including creation and status updates.
    Inherits generic CRUD operations from CRUDBase.
    """
    def create_for_definition(
        self,
        db: Session,
        *,
        workflow_definition_id: int,
        status: WorkflowRunStatusEnum = WorkflowRunStatusEnum.PENDING,
        initial_inputs: Optional[Dict[str, Any]] = None,
        triggered_by: Optional[str] = None
    ) -> WorkflowRun:
        """
        Create a WorkflowRun for a given workflow definition.
        Args:
            db (Session): SQLAlchemy session.
            workflow_definition_id (int): ID of the workflow definition.
            status (WorkflowRunStatusEnum): Initial status.
            initial_inputs (Optional[Dict[str, Any]]): Initial input values.
            triggered_by (Optional[str]): Actor ID who triggered the run.
        Returns:
            WorkflowRun: The created WorkflowRun instance.
        """
        db_obj = self.model(
            workflow_definition_id=workflow_definition_id,
            status=status,
            initial_inputs=initial_inputs,
            triggered_by_actor_id=triggered_by,
            created_at=datetime.now(timezone.utc)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_status(
        self, db: Session, *, run_id: int, status: WorkflowRunStatusEnum, error_message: Optional[str] = None
    ) -> Optional[WorkflowRun]:
        """
        Update the status (and optionally error message) of a WorkflowRun.
        Args:
            db (Session): SQLAlchemy session.
            run_id (int): WorkflowRun ID.
            status (WorkflowRunStatusEnum): New status.
            error_message (Optional[str]): Error message if failed.
        Returns:
            Optional[WorkflowRun]: The updated WorkflowRun instance, or None if not found.
        """
        db_obj = self.get(db, id=run_id)
        if db_obj:
            db_obj.status = status
            if status == WorkflowRunStatusEnum.RUNNING and not db_obj.started_at:
                db_obj.started_at = datetime.now(timezone.utc)
            if status in [WorkflowRunStatusEnum.SUCCESS, WorkflowRunStatusEnum.FAILED, WorkflowRunStatusEnum.ABORTED] and not db_obj.ended_at:
                db_obj.ended_at = datetime.now(timezone.utc)
            if error_message:
                db_obj.error_message = error_message
            db.add(db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

crud_workflow_run = CRUDWorkflowRun(WorkflowRun)
