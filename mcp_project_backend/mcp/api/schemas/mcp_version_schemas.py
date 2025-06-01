"""
Pydantic schemas for MCPVersion entities.

These models are used for API requests and responses related to MCP versions in the MCP backend.
Each class is documented with field-level and class-level docstrings for clarity and maintainability.
"""

from pydantic import BaseModel, Field
from typing import Optional
from mcp.core.mcp_configs import MCPConfigPayload

# Note: SpecificComponentType is not defined in the codebase. For now, use str and document expected values.
# In the future, this could be an Enum matching frontend types (e.g., "LLM Prompt Agent", "Jupyter Notebook", etc.)

class MCPVersionBase(BaseModel):
    """
    Base schema for an MCP version.

    Attributes:
        version_string (str): Version string (e.g., "1.0.0", "1.0.1-alpha").
        description (Optional[str]): Optional description of the version.
        mcp_type (str): Type of the MCP (should match the 'type' discriminator in MCPConfigPayload).
        config (MCPConfigPayload): Typed configuration payload for this version.
    """
    version_string: str = Field(..., example="1.0.0", description="Version string (e.g., '1.0.0', '1.0.1-alpha').")
    description: Optional[str] = Field(None, description="Optional description of the MCP version.")
    mcp_type: str = Field(..., description="Type of the MCP (should match the 'type' discriminator in MCPConfigPayload).")
    config: MCPConfigPayload = Field(..., description="Typed configuration payload for this MCP version.")

class MCPVersionCreate(MCPVersionBase):
    """
    Schema for creating an MCP version.
    Includes the parent MCPDefinition ID.
    """
    mcp_definition_id: int = Field(..., description="ID of the parent MCPDefinition.")

class MCPVersionUpdate(BaseModel):
    """
    Schema for updating an MCP version. All fields are optional for partial updates.
    Updating mcp_type or config structure is typically handled by creating a new version.
    """
    version_string: Optional[str] = Field(None, description="Updated version string.")
    description: Optional[str] = Field(None, description="Updated description.")
    # config: Optional[MCPConfigPayload] = Field(None, description="Updated configuration payload (if allowed).")

class MCPVersionRead(MCPVersionBase):
    """
    Schema for reading an MCP version from the database/API.
    Includes the version's ID and parent MCPDefinition ID.
    """
    id: int = Field(..., description="Unique identifier for the MCP version.")
    mcp_definition_id: int = Field(..., description="ID of the parent MCPDefinition.")
    # Optionally, add creation/update timestamps here.

    class Config:
        orm_mode = True
