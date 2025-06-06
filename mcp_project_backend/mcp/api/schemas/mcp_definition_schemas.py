"""
Pydantic schemas for MCPDefinition entities.

These models are used for API requests and responses related to MCP definitions in the MCP backend.
Each class is documented with field-level and class-level docstrings for clarity and maintainability.
"""

from pydantic import BaseModel, Field
from typing import Optional, List

# Note: SpecificComponentType is not defined in the codebase. For now, use str and document expected values.
# In the future, this could be an Enum matching frontend types (e.g., "LLM Prompt Agent", "Jupyter Notebook", etc.)

class MCPDefinitionBase(BaseModel):
    """
    Base schema for an MCP definition.

    Attributes:
        name (str): Name of the MCP definition.
        description (Optional[str]): Optional description of the MCP.
        mcp_type (str): General category/type of the MCP (should match frontend types).
        tags (Optional[List[str]]): List of tags for categorization.
    """
    name: str = Field(..., description="Name of the MCP definition.")
    description: Optional[str] = Field(None, description="Optional description of the MCP.")
    mcp_type: str = Field(..., description="General category/type of the MCP (e.g., 'LLM Prompt Agent', 'Jupyter Notebook', etc.).")
    tags: Optional[List[str]] = Field(default_factory=list, description="Tags for the MCP definition.")

class MCPDefinitionCreate(MCPDefinitionBase):
    """
    Schema for creating an MCP definition.
    Inherits all fields from MCPDefinitionBase.
    """
    pass

class MCPDefinitionUpdate(MCPDefinitionBase):
    """
    Schema for updating an MCP definition.
    All fields are optional for partial updates.
    """
    name: Optional[str] = Field(None, description="Updated name of the MCP definition.")
    mcp_type: Optional[str] = Field(None, description="Updated type of the MCP definition.")

class MCPDefinitionRead(MCPDefinitionBase):
    """
    Schema for reading an MCP definition from the database/API.
    Includes the MCP's ID and optional owner ID.
    """
    id: int = Field(..., description="Unique identifier for the MCP definition.")
    owner_id: Optional[int] = Field(None, description="ID of the MCP owner, if applicable.")

    class Config:
        orm_mode = True
