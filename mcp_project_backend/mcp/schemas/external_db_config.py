"""
Pydantic schemas for ExternalDatabaseConfig API operations.
"""
import uuid
import json  # For validating additional_configs as JSON string
from pydantic import BaseModel, Field, field_validator
from typing import Optional


class ExternalDbConfigBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255,
                      description="Unique name for the database configuration.")
    description: Optional[str] = Field(
        default=None, description="Optional description.")
    db_type: str = Field(..., min_length=1, max_length=50,
                         description="Type of the database (e.g., 'postgresql', 'mysql', 'bigquery').")
    host: Optional[str] = Field(
        default=None, max_length=255, description="Database host address.")
    port: Optional[int] = Field(
        default=None, ge=1, le=65535, description="Database port number.")
    username: Optional[str] = Field(
        default=None, max_length=255, description="Username for database authentication.")
    password_secret_key: Optional[str] = Field(
        default=None, max_length=255, description="Key or reference to the password/secret in a secrets manager.")
    database_name: Optional[str] = Field(
        default=None, max_length=255, description="Name of the specific database/schema.")
    additional_configs: Optional[str] = Field(
        default=None, description="JSON string for additional type-specific configurations.")

    @field_validator('additional_configs')
    @classmethod
    def validate_additional_configs_json(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        try:
            json.loads(v)
        except json.JSONDecodeError as e:
            raise ValueError(
                "additional_configs must be a valid JSON string.") from e
        return v


class ExternalDbConfigCreate(ExternalDbConfigBase):
    pass


class ExternalDbConfigUpdate(ExternalDbConfigBase):
    # All fields are optional for update
    name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    db_type: Optional[str] = Field(default=None, min_length=1, max_length=50)
    # For other fields, default=None from base is fine, meaning they won't be updated if not provided.


class ExternalDbConfigRead(ExternalDbConfigBase):
    id: uuid.UUID
    # We might not want to expose password_secret_key directly in read operations for security.
    # Consider if it should be omitted or handled differently.
    # For now, including it as per model, but in a real app, this needs careful consideration.

    class Config:
        from_attributes = True


class ExternalDbConfigList(BaseModel):
    items: list[ExternalDbConfigRead]
    total: int
