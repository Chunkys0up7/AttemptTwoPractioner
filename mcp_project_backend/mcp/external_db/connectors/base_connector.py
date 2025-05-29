"""
Defines the abstract base class for database connectors and supporting models.
"""
import abc
from typing import Any, List, Dict, Optional
from pydantic import BaseModel, Field

# --- Supporting Pydantic Models for Connection and Schema ---


class ConnectionParams(BaseModel):
    """
    Generic model for database connection parameters.
    Specific connectors will extend or use this with db_type specific fields
    often stored in the 'additional_configs' of ExternalDatabaseConfig model.
    """
    db_type: str = Field(
        description="Type of the database (e.g., 'postgresql', 'bigquery')")
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    # Actual password, handle with care
    password: Optional[str] = Field(
        default=None, description="Actual password, to be handled securely.")
    database_name: Optional[str] = None
    additional_configs: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Additional connector-specific parameters.")


class ColumnInfo(BaseModel):
    """Represents information about a database column."""
    name: str
    type: str  # Data type as string
    nullable: Optional[bool] = None
    default: Optional[str] = None  # Default value as string
    comment: Optional[str] = None
    # Add more fields as needed: precision, scale, constraints, etc.


class TableInfo(BaseModel):
    """Represents information about a database table."""
    name: str
    columns: List[ColumnInfo]
    comment: Optional[str] = None
    # Add more fields: primary_key_columns, foreign_keys, indexes, etc.


class DBSchemaInfo(BaseModel):
    """Represents information about a database schema (or a dataset in BigQuery terms)."""
    name: str
    tables: List[TableInfo]
    comment: Optional[str] = None


class DatabaseInfo(BaseModel):
    """Represents overall information about a database (collection of schemas)."""
    name: Optional[str] = None  # e.g., actual database name or project ID for BigQuery
    schemas: List[DBSchemaInfo]

# --- Abstract Base Connector ---


class BaseDBConnector(abc.ABC):
    """
    Abstract Base Class for database connectors.

    Each concrete connector for a specific database type (PostgreSQL, BigQuery, etc.)
    should inherit from this class and implement its abstract methods.
    """

    def __init__(self, connection_params: ConnectionParams):
        """
        Initializes the connector with connection parameters.

        Args:
            connection_params: A ConnectionParams object containing all necessary
                               details to establish a connection.
        """
        self.connection_params = connection_params
        # Holds the active connection object
        self._connection: Optional[Any] = None

    @abc.abstractmethod
    async def connect(self) -> None:
        """
        Establishes a connection to the database.
        Sets self._connection if successful.
        Should raise ConnectionError or specific DB exceptions on failure.
        """
        pass

    @abc.abstractmethod
    async def disconnect(self) -> None:
        """
        Closes the database connection and cleans up resources.
        Sets self._connection to None.
        """
        pass

    @abc.abstractmethod
    async def execute_sql_statement(
        self,
        sql: str,
        params: Optional[List[Any]] = None,
        max_rows: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes an arbitrary SQL statement.

        Args:
            sql: The SQL query or statement to execute.
            params: Optional list of parameters for placeholder substitution in the SQL query.
            max_rows: Optional maximum number of rows to return for SELECT queries.

        Returns:
            A list of dictionaries, where each dictionary represents a row, 
            with column names as keys. For non-SELECT statements, might return an empty list
            or a list with a summary (e.g., row count affected).

        Raises:
            ConnectionError: If not connected.
            # Or other specific database execution errors.
        """
        pass

    @abc.abstractmethod
    async def scan_db_schema(self) -> DatabaseInfo:
        """
        Scans the database to retrieve its schema information (schemas, tables, columns).

        Returns:
            A DatabaseInfo object populated with the schema details.

        Raises:
            ConnectionError: If not connected.
            # Or other specific database errors during schema introspection.
        """
        pass

    @property
    def is_connected(self) -> bool:
        """Returns True if the connector believes it has an active connection."""
        return self._connection is not None

    async def __aenter__(self):
        """Async context manager entry: connects to the database."""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit: disconnects from the database."""
        await self.disconnect()
