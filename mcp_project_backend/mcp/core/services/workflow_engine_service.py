"""
Workflow Engine Service for orchestrating workflow executions.

Handles workflow run lifecycle management, execution, and monitoring.
"""
import uuid
from typing import Dict, Any, Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime
import logging

from mcp.db.models import WorkflowRun
from mcp.db.models.workflow import WorkflowRunStatus
from mcp.monitoring.performance import performance_monitor

logger = logging.getLogger(__name__)

class WorkflowEngineService:
    def __init__(self, db: Session):
        self.db = db
        self._validate_db_connection()

    def _validate_db_connection(self) -> None:
        """Validate database connection and raise error if not healthy."""
        try:
            self.db.execute("SELECT 1")
        except SQLAlchemyError as e:
            logger.error(f"Database connection validation failed: {e}")
            performance_monitor.increment_error("db_connection", str(e))
            raise ValueError("Database connection is not healthy")

    async def start_workflow_run(
        self,
        workflow_definition_id: uuid.UUID,
        run_params: Optional[Dict[str, Any]] = None,
        actor_id: str = "system"
    ) -> WorkflowRun:
        """
        Starts a new workflow run for the given definition ID.

        Args:
            workflow_definition_id: The ID of the workflow definition to run.
            run_params: Optional dictionary of parameters for this specific run.
            actor_id: ID of the actor initiating the run (for auditing)

        Returns:
            The created WorkflowRun database object.

        Raises:
            ValueError: If workflow definition is invalid or required params are missing.
            SQLAlchemyError: If database operation fails.
        """
        try:
            # Validate input parameters
            if not workflow_definition_id:
                raise ValueError("Workflow definition ID is required")

            # Create new workflow run
            new_run = WorkflowRun(
                workflow_definition_id=workflow_definition_id,
                status=WorkflowRunStatus.PENDING,
                parameters=run_params,
                started_at=datetime.utcnow(),
                actor_id=actor_id
            )

            # Add to database
            self.db.add(new_run)
            self.db.commit()
            self.db.refresh(new_run)
        self.db.commit()
        self.db.refresh(new_run)

        # TODO: In a real engine, this would trigger asynchronous execution
        # For example, by publishing an event or adding a task to a queue.
        # print(f"Workflow run {new_run.id} created for definition {workflow_definition_id}. Status: PENDING")

        return new_run
