from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select
from typing import Optional, List
from datetime import datetime
import logging

from .base_crud import CRUDBase
from mcp.db.models.workflow_definition import WorkflowDefinition, WorkflowStep
from mcp.api.schemas.workflow_definition_schemas import WorkflowDefinitionCreate, WorkflowDefinitionUpdate, WorkflowStepCreate
from mcp.core.exceptions import WorkflowDefinitionError, WorkflowStepError
from mcp.monitoring.performance import performance_monitor

logger = logging.getLogger(__name__)

class CRUDWorkflowStep(CRUDBase[WorkflowStep, WorkflowStepCreate, WorkflowStepCreate]):
    """
    CRUD operations for WorkflowStep model with enhanced error handling and monitoring.
    """
    def create(self, db: Session, *, obj_in: WorkflowStepCreate) -> WorkflowStep:
        """
        Create a new workflow step.
        
        Args:
            db: SQLAlchemy session
            obj_in: WorkflowStepCreate schema
            
        Returns:
            Created WorkflowStep instance
            
        Raises:
            WorkflowStepError: If step creation fails
        """
        try:
            with performance_monitor.monitor_workflow_step_operation("create"):
                step_data = obj_in.model_dump()
                step = WorkflowStep(**step_data)
                db.add(step)
                db.commit()
                db.refresh(step)
                logger.info(f"Created workflow step {step.id}")
                return step
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to create workflow step: {e}")
            performance_monitor.increment_error("workflow_step_create", str(e))
            raise WorkflowStepError(f"Failed to create workflow step: {str(e)}")

    def get_by_workflow(self, db: Session, workflow_id: str) -> List[WorkflowStep]:
        """
        Get all steps for a workflow.
        
        Args:
            db: SQLAlchemy session
            workflow_id: ID of the workflow
            
        Returns:
            List of WorkflowStep instances
        """
        try:
            with performance_monitor.monitor_workflow_step_operation("get_by_workflow"):
                steps = db.execute(
                    select(WorkflowStep)
                    .filter(WorkflowStep.workflow_definition_id == workflow_id)
                    .order_by(WorkflowStep.order)
                ).scalars().all()
                logger.info(f"Retrieved {len(steps)} steps for workflow {workflow_id}")
                return steps
        except SQLAlchemyError as e:
            logger.error(f"Failed to get workflow steps: {e}")
            performance_monitor.increment_error("workflow_step_get", str(e))
            raise WorkflowStepError(f"Failed to retrieve workflow steps: {str(e)}")

class CRUDWorkflowDefinition(CRUDBase[WorkflowDefinition, WorkflowDefinitionCreate, WorkflowDefinitionUpdate]):
    """
    CRUD operations for WorkflowDefinition model with enhanced error handling and monitoring.
    """
    def create_with_steps(self, db: Session, *, obj_in: WorkflowDefinitionCreate, owner_id: Optional[int] = None) -> WorkflowDefinition:
        """
        Create a WorkflowDefinition and its steps in a single transaction.
        
        Args:
            db: SQLAlchemy session
            obj_in: WorkflowDefinitionCreate schema
            owner_id: Optional owner ID
            
        Returns:
            Created WorkflowDefinition instance
            
        Raises:
            WorkflowDefinitionError: If creation fails
        """
        try:
            with performance_monitor.monitor_workflow_definition_operation("create"):
                obj_in_data = obj_in.model_dump(exclude={"steps"})
                
                # Validate workflow graph
                self._validate_workflow_graph(obj_in.graph_representation)
                
                db_obj = self.model(**obj_in_data)
                db.add(db_obj)
                
                if obj_in.steps:
                    for step_in in obj_in.steps:
                        step_data = step_in.model_dump()
                        step = WorkflowStep(**step_data, workflow_definition_id=db_obj.id)
                        db.add(step)
                
                db.commit()
                db.refresh(db_obj)
                
                logger.info(f"Created workflow definition {db_obj.id} with {len(obj_in.steps) if obj_in.steps else 0} steps")
                return db_obj
                
        except SQLAlchemyError as e:
            db.rollback()
            logger.error(f"Failed to create workflow definition: {e}")
            performance_monitor.increment_error("workflow_definition_create", str(e))
            raise WorkflowDefinitionError(f"Failed to create workflow definition: {str(e)}")
        except Exception as e:
            db.rollback()
            logger.error(f"Unexpected error creating workflow definition: {e}")
            performance_monitor.increment_error("workflow_definition_unexpected", str(e))
            raise WorkflowDefinitionError(f"Unexpected error creating workflow definition: {str(e)}")

    def get_with_steps(self, db: Session, id: str) -> Optional[WorkflowDefinition]:
        """
        Retrieve a WorkflowDefinition with its steps.
        
        Args:
            db: SQLAlchemy session
            id: WorkflowDefinition ID
            
        Returns:
            WorkflowDefinition instance with steps or None
            
        Raises:
            WorkflowDefinitionError: If retrieval fails
        """
        try:
            with performance_monitor.monitor_workflow_definition_operation("get"):
                workflow = db.execute(
                    select(WorkflowDefinition)
                    .options(joinedload(WorkflowDefinition.steps))
                    .filter(WorkflowDefinition.id == id)
                ).scalar()
                
                if workflow:
                    logger.info(f"Retrieved workflow definition {id} with {len(workflow.steps)} steps")
                else:
                    logger.info(f"Workflow definition {id} not found")
                
                return workflow
                
        except SQLAlchemyError as e:
            logger.error(f"Failed to get workflow definition {id}: {e}")
            performance_monitor.increment_error("workflow_definition_get", str(e))
            raise WorkflowDefinitionError(f"Failed to retrieve workflow definition: {str(e)}")

    def _validate_workflow_graph(self, graph: dict) -> None:
        """
        Validate workflow graph structure.
        
        Args:
            graph: Workflow graph representation
            
        Raises:
            WorkflowDefinitionError: If graph is invalid
        """
        try:
            if not isinstance(graph, dict):
                raise WorkflowDefinitionError("Workflow graph must be a dictionary")
                
            required_fields = {"nodes", "edges", "start_node", "end_node"}
            if not required_fields.issubset(graph.keys()):
                missing = required_fields - set(graph.keys())
                raise WorkflowDefinitionError(f"Missing required fields: {missing}")
                
            # Validate nodes
            if not isinstance(graph["nodes"], list):
                raise WorkflowDefinitionError("Nodes must be a list")
                
            # Validate edges
            if not isinstance(graph["edges"], list):
                raise WorkflowDefinitionError("Edges must be a list")
                
            logger.info("Workflow graph validation successful")
            
        except Exception as e:
            logger.error(f"Workflow graph validation failed: {e}")
            performance_monitor.increment_error("workflow_graph_validation", str(e))
            raise WorkflowDefinitionError(f"Invalid workflow graph: {str(e)}")

    def get(self, db: Session, id: str) -> Optional[WorkflowDefinition]:
        """
        Retrieve a WorkflowDefinition by ID.
        
        Args:
            db: SQLAlchemy session
            id: WorkflowDefinition ID
            
        Returns:
            WorkflowDefinition instance or None
        """
        return db.query(self.model).filter(self.model.id == id).first()

crud_workflow_definition = CRUDWorkflowDefinition(WorkflowDefinition)
crud_workflow_step = CRUDWorkflowStep(WorkflowStep)
