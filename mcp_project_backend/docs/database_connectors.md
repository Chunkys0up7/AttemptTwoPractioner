# Database Connector Pattern

This document describes the standardized database connector pattern used in the MCP backend for integrating with external databases.

## Overview

The connector pattern provides a unified interface for interacting with various database systems (PostgreSQL, BigQuery, etc.) via a base class and concrete implementations. This enables MCP components to access external data sources in a consistent and secure manner.

## BaseDBConnector

All connectors inherit from `BaseDBConnector`, which defines the standard interface:

```python
import abc
from typing import Any, List, Dict, Optional

class BaseDBConnector(abc.ABC):
    def __init__(self, connection_params: Dict[str, Any]):
        self.connection_params = connection_params
        self._connection = None

    @abc.abstractmethod
    async def connect(self): pass

    @abc.abstractmethod
    async def disconnect(self): pass

    @abc.abstractmethod
    async def execute_sql_statement(self, sql: str, params: Optional[List[Any]] = None, max_rows: Optional[int] = None) -> List[Dict[str, Any]]: pass

    @abc.abstractmethod
    async def scan_db_schema(self) -> Any: pass
```

## Concrete Connectors

### PostgreSQLConnector

Implements the interface for PostgreSQL using asyncpg or SQLAlchemy.

### BigQueryConnector

Implements the interface for Google BigQuery using `google-cloud-bigquery`:

```python
from google.cloud import bigquery
from .base_connector import BaseDBConnector

class BigQueryConnector(BaseDBConnector):
    async def connect(self):
        # ... see codebase for details ...
        pass
    # ... other methods ...
```

## Configuration

Connection parameters are stored in the `ExternalDatabaseConfig` model and provided to connectors at runtime. Sensitive data (passwords, keys) should be managed securely.

## Usage Example

```python
# Get config from DB
config = db.query(ExternalDatabaseConfig).get(id)
# Instantiate connector
connector = PostgreSQLConnector(config.as_dict())
await connector.connect()
results = await connector.execute_sql_statement("SELECT * FROM my_table LIMIT 10")
await connector.disconnect()
```

## Extension

To add a new database type:

1. Subclass `BaseDBConnector`.
2. Implement all abstract methods.
3. Register the connector in the connector manager/factory.

## Integration Points

- Used by workflow engine and MCP executors to provide database access to scripts, notebooks, and LLMs.
- Managed via API endpoints for external DB configs.

## Security

- Never store plaintext passwords in code or logs.
- Use environment variables or secret managers for sensitive credentials.

## See Also

- `external_db_config_routes.md` for API endpoints
- `mcp/external_db/connectors/` for code
