"""
Pydantic schemas for managing external database connection configurations.

These models are used for API requests and responses related to external DB configs in the MCP backend.
Each class is documented with field-level and class-level docstrings for clarity and maintainability.
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any

class ExternalDbConfigBase(BaseModel):
    """
    Base schema for an external database connection configuration.

    Attributes:
        name (str): Name of the external DB config (e.g., "My Production Postgres").
        db_type (str): Type of the database (e.g., "postgresql", "mysql", "bigquery").
        host (Optional[str]): Hostname or IP address of the database server.
        port (Optional[int]): Port number for the database connection.
        database_name (Optional[str]): Name of the database (or dataset_id for BigQuery).
        username (Optional[str]): Username for authentication.
        additional_params (Optional[Dict[str, Any]]): Type-specific parameters (e.g., BigQuery project_id, service_account_key_path).
    """
    name: str = Field(..., example="My Production Postgres", description="Name of the external DB config.")
    db_type: str = Field(..., example="postgresql", description="Type of the database (e.g., 'postgresql', 'mysql', 'bigquery').")
    host: Optional[str] = Field(None, description="Hostname or IP address of the database server.")
    port: Optional[int] = Field(None, description="Port number for the database connection.")
    database_name: Optional[str] = Field(None, description="Name of the database (or dataset_id for BigQuery).")
    username: Optional[str] = Field(None, description="Username for authentication.")
    additional_params: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Type-specific parameters (e.g., BigQuery project_id, service_account_key_path).")

class ExternalDbConfigCreate(ExternalDbConfigBase):
    """
    Schema for creating an external DB config.
    Includes a password or secret reference (write-only).
    """
    password_or_secret_ref: Optional[str] = Field(None, description="Password or reference to a secret (write-only).")

class ExternalDbConfigUpdate(ExternalDbConfigBase):
    """
    Schema for updating an external DB config. All fields are optional for partial updates.
    Includes a password or secret reference for updates.
    """
    name: Optional[str] = Field(None, description="Updated name of the external DB config.")
    db_type: Optional[str] = Field(None, description="Updated type of the database.")
    password_or_secret_ref: Optional[str] = Field(None, description="To update password/secret reference.")

class ExternalDbConfigRead(ExternalDbConfigBase):
    """
    Schema for reading an external DB config from the database/API.
    Includes the config's ID and a flag indicating if it is configured.
    Never returns passwords or sensitive connection details directly.
    """
    id: int = Field(..., description="Unique identifier for the external DB config.")
    is_configured: bool = Field(True, description="Indicates if the config is set up and ready to use.")

    class Config:
        orm_mode = True
