from sqlalchemy.orm import Session
from .base_crud import CRUDBase
from mcp.db.models.workflow_definition import WorkflowDefinition, WorkflowStep
from mcp.api.schemas.workflow_definition_schemas import WorkflowDefinitionCreate, WorkflowDefinitionUpdate, WorkflowStepCreate
from typing import Optional

class CRUDWorkflowStep(CRUDBase[WorkflowStep, WorkflowStepCreate, WorkflowStepCreate]):
    """
    CRUD operations for WorkflowStep model.
    Inherits generic CRUD operations from CRUDBase.
    """
    pass

class CRUDWorkflowDefinition(CRUDBase[WorkflowDefinition, WorkflowDefinitionCreate, WorkflowDefinitionUpdate]):
    """
    CRUD operations for WorkflowDefinition model, including creation with steps.
    Inherits generic CRUD operations from CRUDBase.
    """
    def create_with_steps(self, db: Session, *, obj_in: WorkflowDefinitionCreate, owner_id: Optional[int] = None) -> WorkflowDefinition:
        """
        Create a WorkflowDefinition and its steps in a single transaction.
        Args:
            db (Session): SQLAlchemy session.
            obj_in (WorkflowDefinitionCreate): Data for the workflow definition and its steps.
            owner_id (Optional[int]): Owner ID if applicable.
        Returns:
            WorkflowDefinition: The created WorkflowDefinition instance with steps.
        """
        obj_in_data = obj_in.model_dump(exclude={"steps"})
        # if owner_id:
        #     obj_in_data["owner_id"] = owner_id
        db_obj = self.model(**obj_in_data)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        if obj_in.steps:
            for step_in in obj_in.steps:
                step_db_obj_data = step_in.model_dump()
                step_db_obj = WorkflowStep(**step_db_obj_data, workflow_definition_id=db_obj.id)
                db.add(step_db_obj)
            db.commit()
            db.refresh(db_obj)
        return db_obj

    def get_with_steps(self, db: Session, id: int) -> Optional[WorkflowDefinition]:
        """
        Retrieve a WorkflowDefinition with its steps.
        Args:
            db (Session): SQLAlchemy session.
            id (int): WorkflowDefinition ID.
        Returns:
            Optional[WorkflowDefinition]: The WorkflowDefinition instance with steps, or None if not found.
        """
        return db.query(self.model).filter(self.model.id == id).first()

crud_workflow_definition = CRUDWorkflowDefinition(WorkflowDefinition)
crud_workflow_step = CRUDWorkflowStep(WorkflowStep)
