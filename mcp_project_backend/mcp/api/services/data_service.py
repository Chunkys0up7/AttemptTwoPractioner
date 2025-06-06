from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from mcp.db.session import get_db
from mcp.db.models.mcp import MCPDefinition, MCPVersion
from mcp.schemas.mcp import MCPDefinitionRead, MCPVersionRead
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