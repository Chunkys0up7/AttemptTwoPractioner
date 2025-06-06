"""
Concrete implementation of BaseDBConnector for Google BigQuery.
"""
from typing import Any, List, Dict, Optional

from google.cloud import bigquery
from google.oauth2 import service_account  # For service account auth
from google.auth.exceptions import DefaultCredentialsError

from .base_connector import (
    BaseDBConnector,
    ConnectionParams,
    DatabaseInfo,
    DBSchemaInfo,
    TableInfo,
    ColumnInfo
)


class BigQueryConnector(BaseDBConnector):
    """Connector for Google BigQuery."""

    def __init__(self, connection_params: ConnectionParams):
        super().__init__(connection_params)
        # BigQuery client requires project_id. It can be in additional_configs.
        self.project_id: Optional[str] = self.connection_params.additional_configs.get(
            "project_id")
        self.dataset_id: Optional[str] = self.connection_params.additional_configs.get(
            "dataset_id")  # Optional default dataset
        self.service_account_json_path: Optional[str] = self.connection_params.additional_configs.get(
            "service_account_json_path")
        self.service_account_info: Optional[Dict[str, str]] = self.connection_params.additional_configs.get(
            "service_account_info")  # dict for SA info

        if not self.project_id:
            raise ValueError(
                "BigQueryConnector requires 'project_id' in additional_configs.")

    async def connect(self) -> None:
        """Establishes a connection to BigQuery using a BigQuery client."""
        if self.is_connected:
            return

        try:
            credentials = None
            if self.service_account_json_path:
                credentials = service_account.Credentials.from_service_account_file(
                    self.service_account_json_path,
                    scopes=["https://www.googleapis.com/auth/bigquery"],
                )
            elif self.service_account_info:  # if SA info is provided as a dict
                credentials = service_account.Credentials.from_service_account_info(
                    self.service_account_info,
                    scopes=["https://www.googleapis.com/auth/bigquery"],
                )
            # If no specific credentials, client will try to use Application Default Credentials (ADC)

            self._connection = bigquery.Client(
                project=self.project_id, credentials=credentials)

            # Test connection by listing datasets (limited to 1 for speed)
            list(self._connection.list_datasets(max_results=1))
            print(
                f"Successfully connected to BigQuery project '{self.project_id}'.")
        except DefaultCredentialsError as e:
            self._connection = None
            raise ConnectionError(
                f"Failed to connect to BigQuery: No Google Cloud credentials found. "
                f"Ensure ADC are set up or provide service account details. Original error: {e}"
            ) from e
        except Exception as e:
            self._connection = None  # Ensure connection is None on failure
            raise ConnectionError(
                f"Failed to connect to BigQuery project '{self.project_id}': {e}") from e

    async def disconnect(self) -> None:
        """Closes the BigQuery client connection (BigQuery client is often stateless regarding connections)."""
        if self._connection:
            self._connection.close()  # Closes the background resources used by the client
            self._connection = None
            print("BigQuery client resources released.")

    async def execute_sql_statement(
        self,
        sql: str,
        # BigQuery uses named params @param_name
        params: Optional[List[Any]] = None,
        max_rows: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Executes a SQL statement in BigQuery.
        Note: BigQuery Python client typically uses named parameters (@param_name) in SQL 
        and `query_parameters` in `JobConfig`, not positional `params` list directly.
        This implementation is simplified and does not map positional params.
        """
        if not self.is_connected or not isinstance(self._connection, bigquery.Client):
            raise ConnectionError(
                "Not connected to BigQuery or invalid connection object.")

        try:
            # For named parameters, one would construct bigquery.ScalarQueryParameter items
            # and pass them to bigquery.QueryJobConfig(query_parameters=...)
            # This example doesn't support query parameters for simplicity of the base interface.
            if params:
                print("Warning: BigQueryConnector currently does not support parameterized queries via the 'params' list argument. Execute raw SQL.")

            query_job = self._connection.query(sql)  # API request
            # Waits for the job to complete
            results = query_job.result(max_results=max_rows)
            return [dict(row) for row in results]
        except Exception as e:
            raise RuntimeError(f"Error executing BigQuery SQL: {e}") from e

    async def scan_db_schema(self) -> DatabaseInfo:
        """Scans and returns schema information for the configured BigQuery project and optional dataset."""
        if not self.is_connected or not isinstance(self._connection, bigquery.Client):
            raise ConnectionError(
                "Not connected to BigQuery or invalid connection object.")

        bq_schemas: List[DBSchemaInfo] = []
        datasets_to_scan = []

        if self.dataset_id:  # If a specific dataset is configured, scan only that
            datasets_to_scan.append(
                self._connection.get_dataset(self.dataset_id))
        # Otherwise, scan all datasets in the project (can be slow/expensive)
        else:
            # Consider adding a limit or allowing user to specify datasets for scanning
            print(
                f"Scanning all datasets in project '{self.project_id}'. This might take a while...")
            datasets_to_scan = list(self._connection.list_datasets())

        for dataset in datasets_to_scan:
            dataset_ref = self._connection.dataset(dataset.dataset_id)
            tables_in_dataset: List[TableInfo] = []
            bq_tables = list(self._connection.list_tables(dataset_ref))

            for bq_table_item in bq_tables:
                bq_table = self._connection.get_table(bq_table_item.reference)
                columns_in_table: List[ColumnInfo] = []
                for schema_field in bq_table.schema:
                    columns_in_table.append(ColumnInfo(
                        name=schema_field.name,
                        type=schema_field.field_type,
                        nullable=schema_field.mode == 'NULLABLE',  # REQUIRED, NULLABLE, REPEATED
                        # default: BigQuery schema doesn't directly expose default values like traditional SQL
                        comment=schema_field.description
                    ))
                tables_in_dataset.append(TableInfo(
                    name=bq_table.table_id,
                    columns=columns_in_table,
                    comment=bq_table.description
                ))
            bq_schemas.append(DBSchemaInfo(
                name=dataset.dataset_id,
                tables=tables_in_dataset,
                comment=dataset.description
            ))

        return DatabaseInfo(name=self.project_id, schemas=bq_schemas)
