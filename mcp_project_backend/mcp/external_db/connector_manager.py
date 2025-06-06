"""
Manages and provides instances of database connectors.

This manager will act as a factory or registry for different BaseDBConnector implementations.
"""
from typing import Dict, Type
import json

from mcp.db.models import ExternalDatabaseConfig
from mcp.external_db.connectors.base_connector import BaseDBConnector, ConnectionParams
# Specific connector implementations will be imported here later, e.g.:
# from .connectors.postgresql_connector import PostgreSQLConnector
from .connectors.bigquery_connector import BigQueryConnector


class ConnectorManager:
    def __init__(self):
        # Registry for connector types
        self._connector_registry: Dict[str, Type[BaseDBConnector]] = {
            # "postgresql": PostgreSQLConnector, # Example
            "bigquery": BigQueryConnector,   # Register BigQueryConnector
        }

    def register_connector(self, db_type: str, connector_class: Type[BaseDBConnector]):
        """Registers a new connector class for a given database type."""
        if db_type in self._connector_registry:
            print(
                f"Warning: Overwriting existing connector for db_type '{db_type}'.")
        self._connector_registry[db_type] = connector_class

    async def get_connector(self, db_config: ExternalDatabaseConfig) -> BaseDBConnector:
        """
        Retrieves and initializes a database connector based on the ExternalDatabaseConfig.

        Args:
            db_config: The ExternalDatabaseConfig model instance from the database.

        Returns:
            An initialized instance of a BaseDBConnector subclass.

        Raises:
            ValueError: If the db_type is unsupported or if essential config is missing.
            ConnectionError: If the connector fails to establish an initial connection (if auto-connect is implemented).
        """
        connector_class = self._connector_registry.get(
            db_config.db_type.lower())
        if not connector_class:
            raise ValueError(
                f"Unsupported database type: '{db_config.db_type}'")

        additional_params = {}
        if db_config.additional_configs:
            try:
                additional_params = json.loads(db_config.additional_configs)
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Invalid JSON in additional_configs for '{db_config.name}': {e}")

        # TODO: Securely retrieve password if password_secret_key is used.
        # This is a placeholder. In a real system, this would involve fetching the actual password
        # from a secrets manager using db_config.password_secret_key.
        # For now, we'll assume password might be directly in additional_params or handled by connector.
        # Example if passed via additional_configs
        retrieved_password = additional_params.pop('password', None)
        if not retrieved_password and db_config.password_secret_key:
            # print(f"Warning: password_secret_key '{db_config.password_secret_key}' is set but no secret retrieval logic is implemented.")
            # In a real implementation: password = fetch_secret(db_config.password_secret_key)
            pass

        conn_params = ConnectionParams(
            db_type=db_config.db_type,
            host=db_config.host,
            port=db_config.port,
            username=db_config.username,
            # This needs to be the actual password if required by the connector
            password=retrieved_password,
            database_name=db_config.database_name,
            additional_configs=additional_params
        )

        connector_instance = connector_class(connection_params=conn_params)
        # Optionally, could implement an auto-connect here and handle initial connection errors.
        # await connector_instance.connect() # Or leave connection to be explicitly managed by the caller.
        return connector_instance


# Global instance of the manager (Singleton-like access)
connector_manager = ConnectorManager()
