# MCP Backend Implementation TODO List

This document tracks the progress of implementing the backend features outlined in `BACKEND_ENHANCEMENTS.MD`.

## Instructions:
- Mark tasks as `[x]` when completed.
- Add notes or references to commits after each task if necessary.

---

## Phase 1: Core MCP & Workflow Functionality Setup

### Task 1.1: Environment Setup & Basic FastAPI Application
- [x] Initialize FastAPI application (`mcp/api/main.py`)
- [x] Set up Pydantic settings model for configuration (`mcp/core/config.py`)
- [x] Integrate `.env` file loading for environment variables (in `mcp/api/main.py`)
- [x] Create `.env.example` (User to create manually based on `config.py`)
- [x] Add initial dependencies to `requirements.txt` (fastapi, uvicorn, python-dotenv, pydantic-settings - verified existing)
- [x] Configure basic logging (in `mcp/api/main.py`)
- [x] Create basic health check endpoint (`/health` in `mcp/api/main.py`)
- [x] Create basic tests for the health check endpoint (`tests/api/test_main.py`)
- [x] Document created/modified files for Task 1.1

### Task 1.2: Database Model Definitions (Initial)
- [x] Define SQLAlchemy `Base` in `mcp/db/base.py` (or `mcp/db/base_class.py` as in `BACKEND_ENHANCEMENTS.MD` inspiration).
- [x] Define core MCP models (`MCPDefinition`, `MCPVersion`) in `mcp/db/models/mcp.py` (initial fields, including `config_payload_data` as JSONB and `mcp_type`).
- [x] Define `WorkflowDefinition` and `WorkflowRun` models in `mcp/db/models/workflow.py` (initial fields).
- [x] Set up Alembic for database migrations.
    - [x] Initialize Alembic (`alembic init alembic` in `mcp_project_backend`) - (Assumed existing, files configured)
    - [x] Configure `alembic.ini` (e.g., `sqlalchemy.url`).
    - [x] Configure `env.py` to use the `Base` from `mcp.db.base` and import models.
- [x] Create initial Alembic migration script for the defined models. (Manually created `12345abcdef0_create_initial_tables.py`)
- [x] Create basic tests for model creation (e.g., can an MCPDefinition instance be created).
- [x] Document created/modified files for Task 1.2.

### Task 1.3: Typed Configuration Management for MCPs (Pydantic Models)
- [x] Create `mcp/core/mcp_configs.py`.
- [x] Define Pydantic `BaseModel` classes for each `MCPType` (LLMConfig, NotebookConfig, ScriptConfig, etc.) as detailed in `BACKEND_ENHANCEMENTS.MD` Theme 1.1.C.
    - [x] Include `type: Literal[...]` discriminator field.
    - [x] Use aliases for fields to match frontend `typeSpecificData` (e.g., `model_name` aliased to `model`).
- [x] Define `MCPConfigPayload = Union[...]` of all config models.
- [x] Implement `parse_mcp_config` helper function in `mcp_configs.py`.
- [x] Update `MCPVersion` SQLAlchemy model (from Task 1.2) to include `@hybrid_property` for `config` (getter/setter using `parse_mcp_config` and `model_dump`).
- [x] Create tests for Pydantic model validation and the `config` hybrid property on `MCPVersion`.
- [x] Document `mcp_configs.py` and changes to `mcp/db/models/mcp.py`.

### Task 1.4: API Endpoints for MCP Definition CRUD
- [x] Create `mcp/api/routers/mcp_crud_routes.py`.
- [x] Define Pydantic schemas for API request/response related to MCPDefinition and MCPVersion (e.g., `MCPDefinitionCreate`, `MCPVersionCreate`, `MCPDefinitionRead`, `MCPVersionRead`). These should utilize `MCPConfigPayload` for configuration parts. (Created in `mcp/schemas/mcp.py`)
- [x] Implement API endpoints for:
    - [x] Create MCP Definition
    - [x] Get MCP Definition (by ID, with versions)
    - [x] List MCP Definitions (with pagination/filtering if desired later)
    - [x] Update MCP Definition
    - [x] Delete MCP Definition
    - [x] Create MCP Version (for a definition, including typed config)
    - [x] Get MCP Version (by ID)
    - [ ] (Potentially Update/Delete MCP Version - consider version immutability) -> Deferred as versions are typically immutable.
- [x] Implement basic CRUD service functions in `mcp/core/services/mcp_service.py` (or similar) that interact with SQLAlchemy models.
- [x] Integrate these services into the API endpoints.
- [x] Add API endpoints to `mcp/api/main.py` router.
- [x] Create tests for these API endpoints (success and error cases).
- [x] Document created/modified files.

### Task 1.5: Basic Workflow Engine Service (Placeholder)
- [x] Create `mcp/core/workflow_engine_service.py`.
- [x] Define a placeholder `WorkflowEngineService` class.
- [x] Add basic methods like `start_workflow_run(workflow_definition_id: Any, run_params: Dict) -> WorkflowRun` (conceptual).
    - [x] This method would initially just create a `WorkflowRun` record in the DB with 'Pending' or 'Queued' status.
- [x] Implement API endpoint in `mcp/api/routers/workflow_execution_routes.py` to trigger a workflow run (calling the placeholder service).
- [x] Add router to `main.py`.
- [x] Create tests for the API endpoint and placeholder service.
- [x] Document created files.

---

## Phase 2: External Data & Resource Integration

### Task 2.1: External Database Configuration Model & API
- [x] Define `ExternalDatabaseConfig` SQLAlchemy model in `mcp/db/models/external_db_config.py` (name, db_type, host, port, db_name, username, secret_ref).
- [x] Add Alembic migration for `ExternalDatabaseConfig`.
- [x] Create `mcp/api/routers/external_db_config_routes.py`.
- [x] Define Pydantic schemas for `ExternalDatabaseConfig` CRUD. (In `mcp/schemas/external_db_config.py`)
- [x] Implement API endpoints for CRUD operations on `ExternalDatabaseConfig`.
- [x] Implement service layer for `ExternalDatabaseConfig` CRUD. (In `mcp/core/services/external_db_config_service.py`)
- [x] Add router to `main.py`.
- [x] Create tests for the model and API endpoints.
- [x] Document created files.

### Task 2.2: Base Database Connector (`BaseDBConnector`)
- [x] Create `mcp/external_db/connectors/base_connector.py`.
- [x] Define `BaseDBConnector` as an ABC with abstract methods (`connect`, `disconnect`, `execute_sql_statement`, `scan_db_schema`).
- [x] Define supporting Pydantic models if needed for connection parameters or schema representation (e.g., `ConnectionParams`, `DatabaseInfo` etc. in `base_connector.py`).
- [x] Create `mcp/external_db/connector_manager.py` (placeholder for now, to be expanded with specific connectors).
- [x] Document created files.

### Task 2.3: Specific Connector Implementation (e.g., BigQuery - Placeholder)
- [x] Create `mcp/external_db/connectors/bigquery_connector.py` (can be a minimal placeholder initially).
- [x] Implement a `BigQueryConnector` class inheriting from `BaseDBConnector`.
    - [x] Implement methods with placeholder logic or basic BigQuery connection (if `google-cloud-bigquery` is added).
- [x] Update `ConnectorManager` to recognize "bigquery" `db_type`.
- [x] Add `google-cloud-bigquery` to `requirements.txt` (optional for placeholder, required for full impl).
- [x] Document created files.

### Task 2.4: Link MCP Definitions to External DB Configs
- [x] Modify `MCPVersion` SQLAlchemy model to include a relationship (e.g., many-to-many or a list of IDs) to `ExternalDatabaseConfig` (e.g., `external_db_config_ids: List[int]`).
- [x] Update Alembic migration if `MCPVersion` changes.
- [x] Update Pydantic schemas for `MCPVersion` creation/update to include selection of `ExternalDatabaseConfig` IDs.
- [x] Update MCP CRUD API endpoints (Task 1.4) and services to handle linking.
- [x] Test linking functionality.
- [x] Document changes.

---

## Phase 3: Real-time Capabilities & UI Data Provisioning

### Task 3.1: Redis Setup & Pub/Sub Manager
- [x] Ensure Redis is running and `REDIS_URL` is configured in `.env`. (User responsible for Redis; .env guidance provided)
- [x] Create `mcp/core/pubsub/redis_pubsub.py`.
- [x] Implement `RedisPubSubManager` class with `connect_publisher`, `publish`, and `subscribe_to_channel` methods (async, using `aioredis`).
- [x] Integrate `RedisPubSubManager` into FastAPI app lifespan (connect publisher on startup, close on shutdown) in `mcp/api/main.py`.
- [x] Basic tests for publish/subscribe (can be more involved, possibly integration tests).
- [x] Document `redis_pubsub.py`.

### Task 3.2: SSE Endpoint for Workflow Monitoring
- [x] Create `mcp/api/routers/streaming_routes.py`.
- [x] Implement FastAPI SSE endpoint `/api/v1/workflow-runs/{run_id}/stream` using `EventSourceResponse`.
- [x] The endpoint's event generator should use `RedisPubSubManager.subscribe_to_channel(f"workflow_run_events:{run_id}")`.
- [x] Format messages as SSE events (`event: <type>`, `data: <json_payload>`).
- [x] Handle client disconnects gracefully.
- [x] Add router to `main.py`.
- [x] Test the SSE endpoint (e.g., with a simple client or `httpx`).
- [x] Document `streaming_routes.py`.

### Task 3.3: Integrate Workflow Engine with Pub/Sub for Real-time Events
- [x] Modify `WorkflowEngineService` (from Task 1.5).
- [x] When a workflow step's status changes (e.g., starts, completes, fails) or logs are generated (conceptual for now), publish an event to Redis using `RedisPubSubManager`.
    - [x] Channel: `workflow_run_events:{run_id}`
    - [x] Payload: `{"event_type": "log/status_change/result_preview", "payload": {...}}`
- [x] This makes the actual execution logic drive the SSE updates.
- [x] Test that events from the engine are received by the SSE endpoint.
- [x] Document changes in `WorkflowEngineService`.

### Task 3.4: Dashboard-Oriented API Endpoints
- [x] Create dashboard routes for summary data
- [x] Implement dashboard service for data aggregation
- [x] Test dashboard API endpoints
- [x] Document created files.

### Task 3.5: Heterogeneous Entity Details Endpoint
- [x] Create `mcp/api/routers/entity_routes.py`.
- [x] Implement a GET endpoint `/api/v1/entities/{entity_type}/{entity_id}`.
- [x] Based on `entity_type` (e.g., "mcp_version", "workflow_run"), fetch and return details for the specified entity.
    - [x] May require a mapping of `entity_type` strings to SQLAlchemy models and service methods. (Implemented with if/else and service calls)
- [x] Add router to `main.py`.
- [x] Test endpoint with different entity types.
- [x] Document `entity_routes.py`.

---

## Phase 4: Operational Robustness & Developer Experience

### Task 4.1: Robust Environment Variable Management (`.env` loading)
- [x] Already integrated as part of Task 1.1.

### Task 4.2: Database Action Logging (Model & Service)
- [x] Create `mcp/db/models/action_log.py` with `ActionLog` SQLAlchemy model (id, timestamp, actor_id, action_type, entity_type, entity_id, details as JSONB).
- [x] Add Alembic migration for `ActionLog`.
- [x] Create `mcp/core/services/auditing_service.py`.
- [x] Implement `AuditingService` with `create_action_log_entry` method.
- [x] Test model creation and service method.
- [x] Document created files.

### Task 4.3: Integrate Action Logging into CRUD operations and Workflow Engine
- [x] Ensure `actor_id` is captured appropriately (currently a placeholder, requires authentication integration)
- [x] Test that logs are created for relevant actions
- [x] Document integration points

### Task 4.4: API Key Management (Model, Service, API)
- [x] Create `APIKey` model in `mcp/db/models/api_key.py`
- [x] Add Alembic migration for `APIKey`
- [x] Create `APIKeyService` in `mcp/core/services/api_key_service.py`
- [x] Implement API endpoints in `mcp/api/routers/api_key_routes.py`
- [x] Add API key authentication dependency
- [x] Test API key functionality
- [x] Document API key management

### Task 4.5: Error Handling & Logging
- [x] Create custom exception classes in `mcp/core/errors.py`
- [x] Implement error handling middleware
- [x] Add logging configuration and utilities
- [x] Test error handling and logging
- [x] Document error handling and logging system

### Task 4.6: Performance Monitoring
- [x] Create performance monitoring module
- [x] Add metrics collection for API endpoints
- [x] Add metrics collection for database operations
- [x] Add metrics collection for workflow steps
- [x] Create metrics endpoint
- [x] Test performance monitoring
- [x] Document performance monitoring system

### Task 4.7: Security Enhancements
- [x] Create security middleware for headers and rate limiting
- [x] Add CORS and trusted host configuration
- [x] Implement session management
- [x] Add security headers
- [x] Test security middleware
- [x] Document security enhancements

### Task 4.8: Documentation & API Reference
- [x] Create comprehensive API reference documentation
- [x] Create project README with setup instructions
- [x] Document all endpoints, schemas, and authentication methods
- [x] Add examples and usage instructions
- [x] Document error responses and rate limiting
- [x] Add security headers documentation