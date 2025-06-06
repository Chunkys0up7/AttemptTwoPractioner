"""
Pydantic schemas for MCPDefinition and MCPVersion API operations.

These schemas are used by FastAPI for request validation, response serialization,
and generating OpenAPI documentation.
"""
import uuid
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from pydantic import ConfigDict
from pydantic import validator

# Ensure all are imported
from mcp.core.mcp_configs import MCPConfigPayload
# LLMConfig, NotebookConfig, ScriptConfig, StreamlitAppConfig, MCPPackageConfig

# --- MCPVersion Schemas ---


class MCPVersionBase(BaseModel):
    """Base schema for MCPVersion, common fields for creation and reading."""
    version_string: str = Field(..., min_length=1, max_length=50,
                                description="Version identifier (e.g., '1.0.0', 'latest').")
    description: Optional[str] = Field(
        default=None, description="Description of this MCP version.")
    mcp_type: str = Field(..., min_length=1, max_length=100,
                          description="Type of the MCP component (e.g., 'Python Script', 'LLM Prompt Agent').")
    # The config field will use the MCPConfigPayload Union type for validation and serialization.
    # FastAPI will handle the discriminated union based on the 'type' field within the config payload.
    config: Optional[MCPConfigPayload] = Field(
        default=None, description="Type-specific configuration payload for the MCP version.")
    external_db_config_ids: Optional[List[uuid.UUID]] = Field(
        default_factory=list)

    model_config = ConfigDict(from_attributes=True)


class MCPVersionCreate(MCPVersionBase):
    """Schema for creating a new MCPVersion. No mcp_definition_id here as it's a path param."""
    mcp_type: str  # Make mcp_type explicit here for creation if not always derived from config
    config: MCPConfigPayload  # Config is required on creation
    # external_db_config_ids is optional, defaults to empty list

    @validator('config', pre=True, always=True)
    def validate_config_type_match(cls, v, values):
        mcp_type = values.get('mcp_type')
        if not mcp_type:
            # This case should ideally be caught by mcp_type being non-optional in MCPVersionCreate
            # or handled if mcp_type is to be derived from config.type
            raise ValueError("mcp_type must be provided")

        if v is None:  # Config can be None if mcp_type doesn't require specific config
            # We might need to refine this if certain MCP types MUST have a config.
            # For now, assume some types (like a basic 'Data' component) might not have one.
            # However, the current Union MCPConfigPayload doesn't have a NoneType member.
            # This implies config IS generally expected. The example NotebookConfig has optional fields.
            # Let's reconsider if MCPConfigPayload should be Optional[Union[...]] or if all members must have config.
            # For now, sticking to MCPConfigPayload being required on create.
            raise ValueError("config must be provided for the given mcp_type")

        # If config is provided as a dictionary, Pydantic will attempt to validate it against MCPConfigPayload.
        # The MCPConfigPayload union uses a 'type' field as a discriminator.
        # We need to ensure that the provided mcp_type matches the 'type' field within the config payload.

        # If v is already a Pydantic model (part of MCPConfigPayload union)
        if hasattr(v, 'type'):
            if v.type != mcp_type:
                raise ValueError(
                    f"Type in config ('{v.type}') does not match mcp_type ('{mcp_type}')")
        # If v is a dict, it will be validated by Pydantic against MCPConfigPayload.
        # The parse_mcp_config logic or Pydantic's discriminated union handling
        # should manage this. The key is that `config` field is `MCPConfigPayload`.
        # We could add `type: mcp_type` to `v` if it's a dict and doesn't have it,
        # to aid Pydantic's discriminated union resolution.
        elif isinstance(v, dict) and 'type' not in v:
            v['type'] = mcp_type  # Inject type for Pydantic validation
        elif isinstance(v, dict) and 'type' in v and v['type'] != mcp_type:
            raise ValueError(
                f"Type in config dictionary ('{v['type']}') does not match mcp_type ('{mcp_type}')")

        return v


class MCPVersionUpdate(MCPVersionBase):
    # All fields are optional for an update
    name: Optional[str] = None
    description: Optional[str] = None
    mcp_type: Optional[str] = None
    config: Optional[MCPConfigPayload] = None
    # Allow full replacement or no change
    external_db_config_ids: Optional[List[uuid.UUID]] = None

    @validator('config', pre=True, always=True)
    def validate_update_config_type_match(cls, v, values):
        # When updating, if config is provided, mcp_type must also be present or already set
        # and they must match.
        # This is the new mcp_type being set in this update payload
        mcp_type = values.get('mcp_type')
        # We would need access to the existing mcp_type of the object being updated if mcp_type is not in payload.
        # This validator is tricky for updates without knowing the existing state or if mcp_type itself is being changed.

        # Config can be explicitly set to None or not provided (None)
        if v is None:
            return None

        # If mcp_type is also being updated in the same payload, use that for validation.
        # If mcp_type is NOT in the update payload, this validation assumes config.type must match OLD mcp_type.
        # This kind of cross-field validation is complex in Pydantic for partial updates.
        # A service layer validation might be more appropriate here after fetching the existing object.

        # Simplified: if config is given, its internal type must be consistent.
        # The linkage to the parent MCPVersion.mcp_type is enforced at the DB model or service level.
        if hasattr(v, 'type') and mcp_type and v.type != mcp_type:
            raise ValueError(
                f"Type in config ('{v.type}') does not match mcp_type ('{mcp_type}') for update.")
        elif isinstance(v, dict) and 'type' in v and mcp_type and v['type'] != mcp_type:
            raise ValueError(
                f"Type in config dictionary ('{v['type']}') does not match mcp_type ('{mcp_type}') for update.")
        # If mcp_type is not provided in the update payload, we cannot reliably validate v.type against it here.
        # This validation should primarily ensure that `v` itself is a valid MCPConfigPayload member if provided.
        return v


class MCPVersionRead(MCPVersionBase):
    """Schema for reading/returning an MCPVersion."""
    id: uuid.UUID
    mcp_definition_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # external_db_config_ids will be included from MCPVersionBase

    class Config:
        from_attributes = True  # Pydantic v2 alias for orm_mode = True

# --- MCPDefinition Schemas ---


class MCPDefinitionBase(BaseModel):
    """Base schema for MCPDefinition."""
    name: str = Field(..., min_length=1, max_length=255,
                      description="Unique name for the MCP definition.")
    description: Optional[str] = Field(
        default=None, description="Description of the MCP definition.")


class MCPDefinitionCreate(MCPDefinitionBase):
    """Schema for creating a new MCPDefinition."""
    # Optionally, allow creating the first version along with the definition
    initial_version: Optional[MCPVersionCreate] = Field(
        default=None, description="Optional initial version to create along with the definition.")


class MCPDefinitionUpdate(MCPDefinitionBase):
    """Schema for updating an MCPDefinition. All fields are optional for partial updates."""
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None


class MCPDefinitionRead(MCPDefinitionBase):
    """Schema for reading/returning an MCPDefinition, including its versions."""
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    # Include versions when reading a definition
    versions: List[MCPVersionRead] = []

    class Config:
        from_attributes = True

# --- List Schemas for pagination (example) ---


class MCPDefinitionList(BaseModel):
    items: List[MCPDefinitionRead]
    total: int


class MCPVersionList(BaseModel):
    items: List[MCPVersionRead]
    total: int
