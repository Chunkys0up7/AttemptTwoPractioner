from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from mcp.db.session import get_db
from mcp.db.models.mcp import MCPDefinition, MCPVersion
from mcp.db.models.workflow import WorkflowDefinition, WorkflowRun
from mcp.db.models.user import User
from mcp.schemas.mcp import MCPDefinitionRead, MCPVersionRead
from mcp.schemas.workflow import WorkflowDefinitionRead, WorkflowRunRead
from mcp.schemas.user import UserResponse
import uuid

router = APIRouter()

@router.get("/definitions/{definition_id}", response_model=MCPDefinitionRead)
def get_mcp_definition(definition_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve an MCPDefinition by its ID, including its versions.
    """
    definition = db.query(MCPDefinition).filter(MCPDefinition.id == definition_id).first()
    if not definition:
        raise HTTPException(status_code=404, detail="MCPDefinition not found")
    return MCPDefinitionRead.model_validate(definition)

@router.get("/versions/{version_id}", response_model=MCPVersionRead)
def get_mcp_version(version_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve an MCPVersion by its ID.
    """
    version = db.query(MCPVersion).filter(MCPVersion.id == version_id).first()
    if not version:
        raise HTTPException(status_code=404, detail="MCPVersion not found")
    return MCPVersionRead.model_validate(version)

@router.get("/workflows/{workflow_id}", response_model=WorkflowDefinitionRead)
def get_workflow_definition(workflow_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a WorkflowDefinition by its ID.
    """
    workflow = db.query(WorkflowDefinition).filter(WorkflowDefinition.id == workflow_id).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="WorkflowDefinition not found")
    return WorkflowDefinitionRead.model_validate(workflow)

@router.get("/workflow-runs/{run_id}", response_model=WorkflowRunRead)
def get_workflow_run(run_id: uuid.UUID, db: Session = Depends(get_db)):
    """
    Retrieve a WorkflowRun by its ID.
    """
    run = db.query(WorkflowRun).filter(WorkflowRun.id == run_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="WorkflowRun not found")
    return WorkflowRunRead.model_validate(run)

@router.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve a User by their ID.
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse.model_validate(user) 