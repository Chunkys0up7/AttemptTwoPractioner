"""
SQLAlchemy model for External Database Configurations.

This model stores connection details for external databases that MCP components
can interact with.
"""
import uuid
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.dialects.postgresql import UUID as PG_UUID

from mcp.db.base import Base  # Common Base for all models


class ExternalDatabaseConfig(Base):
    __tablename__ = "external_database_configs"

    id = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True, index=True,
                  comment="User-defined name for this database configuration.")
    description = Column(
        Text, nullable=True, comment="Optional description for this configuration.")
    db_type = Column(String(50), nullable=False, index=True,
                     comment="Type of the database (e.g., 'postgresql', 'mysql', 'bigquery').")

    # Connection parameters - some might be optional depending on db_type and auth mechanism
    host = Column(String(255), nullable=True, comment="Database host address.")
    port = Column(Integer, nullable=True, comment="Database port number.")
    username = Column(String(255), nullable=True,
                      comment="Username for database authentication.")
    # password_secret_ref: Store actual password or connection string in a secure vault (e.g., HashiCorp Vault, AWS Secrets Manager)
    # and store a reference/key to it here. For simplicity in this example, we might store it directly or omit.
    # Let's use a placeholder for where the secret is stored/referenced.
    password_secret_key = Column(String(
        255), nullable=True, comment="Key or reference to the password/secret in a secrets manager.")
    database_name = Column(String(
        255), nullable=True, comment="Name of the specific database/schema to connect to.")

    # For cloud-specific DBs like BigQuery, we might need additional fields or a JSONB field for extra args
    # For example, project_id for BigQuery, or path to a service account key JSON file.
    # We can store these in a JSONB field for flexibility.
    additional_configs = Column(
        Text, nullable=True, comment="JSON string for additional type-specific configurations, e.g., BigQuery project_id, GCS path for service account key.")
    # Using Text for JSON string for broader DB compatibility if JSONB is not always available/preferred for this specific simple case,
    # but JSONB would be better for querying if needed.
    # For PostgreSQL, JSONB is ideal: from sqlalchemy.dialects.postgresql import JSONB -> additional_configs = Column(JSONB, nullable=True, ...)
    # Let's stick to Text for now as per initial simpler interpretation in some docs, but note JSONB is better for PG.

    def __repr__(self):
        return f"<ExternalDatabaseConfig(id={self.id}, name='{self.name}', db_type='{self.db_type}')>"
