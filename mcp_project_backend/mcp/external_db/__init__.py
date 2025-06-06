# Makes 'external_db' a Python package
from .connector_manager import ConnectorManager, connector_manager
from .connectors import (
    BaseDBConnector,
    ConnectionParams,
    ColumnInfo,
    TableInfo,
    DBSchemaInfo,
    DatabaseInfo
)

__all__ = [
    "ConnectorManager",
    "connector_manager",
    "BaseDBConnector",
    "ConnectionParams",
    "ColumnInfo",
    "TableInfo",
    "DBSchemaInfo",
    "DatabaseInfo"
]
