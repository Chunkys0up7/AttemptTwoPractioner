"""
SQLAlchemy Base Configuration.

This module provides the declarative base for all SQLAlchemy models in the application.
It also includes a helper for common table arguments like table name generation.
"""
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import MetaData, Column, Integer, DateTime
from sqlalchemy.sql import func
from datetime import datetime, timezone

# Recommended naming convention for constraints
# See: https://alembic.sqlalchemy.org/en/latest/naming.html
NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=NAMING_CONVENTION)

Base = declarative_base(metadata=metadata)

# You could also add a Base class with common columns like id, created_at, updated_at here
# For example:
class BaseTimestampedModel(Base):
    __abstract__ = True # Important: tells SQLAlchemy not to create a table for this model
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
# Then other models can inherit from BaseTimestampedModel

# Import all the models, so that Base has them before being
# imported by Alembic
from mcp.db.models.mcp import MCPDefinition, MCPVersion  # noqa
from mcp.db.models.workflow import WorkflowDefinition, WorkflowRun  # noqa
from mcp.db.models.external_db_config import ExternalDatabaseConfig  # noqa
from mcp.db.models.action_log import ActionLog  # noqa - Add ActionLog model
