# Makes 'models' a package
# This file will also be used by Alembic to import models.
# Import all your models here to make them accessible via mcp.db.models.*
# For example:
# from .mcp import MCPDefinition, MCPVersion
# from .workflow import WorkflowDefinition, WorkflowRun

"""
This package contains all SQLAlchemy ORM models.

Models are imported here to be discoverable by Alembic and for easy access throughout the application.
"""
from .mcp import MCPDefinition, MCPVersion
from .workflow import WorkflowDefinition, WorkflowRun, WorkflowRunStatus
from .external_db_config import ExternalDatabaseConfig
from .user import User
from .api_key import APIKey
from .action_log import ActionLog
from .workflow_template import WorkflowTemplate, WorkflowTemplateVersion, TemplateShare

__all__ = [
    "MCPDefinition",
    "MCPVersion",
    "WorkflowDefinition",
    "WorkflowRun",
    "WorkflowRunStatus",
    "ExternalDatabaseConfig",
    "User",
    "APIKey",
    "ActionLog",
    "WorkflowTemplate",
    "WorkflowTemplateVersion",
    "TemplateShare"
]
