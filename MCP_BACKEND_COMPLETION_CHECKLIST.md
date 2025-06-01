# MCP Backend Completion Checklist & Class Map

This document provides a comprehensive, file-by-file checklist for completing the MCP backend. For each .txt scaffold, it maps the intended class/service, its purpose, key methods, and the required action. Use this as a living checklist to track backend completion and ensure every class is well-documented and purposeful.

---

## Example Entry

- **File:** `mcp/components/ai_copilot_service.py.txt`
- **Class:** `AICoPilotService`
- **Purpose:** Backend service for AI-powered suggestions (workflow optimization, component config, code snippets, etc.)
- **Key Methods:**
  - `get_workflow_optimization_suggestions(workflow_definition: dict) -> List[str]`
  - `get_component_config_advice(component_type: str, current_config: dict) -> List[str]`
- **.py Exists:** No (empty)
- **Action:** [ ] Implement

---

## Checklist

### mcp/components/

- [x] **ai_copilot_service.py.txt** → `AICoPilotService`
  - Purpose: Backend AI Co-Pilot (LLM suggestions for workflow, config, code)
  - Methods: see above
  - .py exists: implemented and documented
  - Action: Complete
- [x] **dependency_visualizer_service.py.txt** → `DependencyVisualizerService`
  - Purpose: Analyze MCP/workflow definitions, output dependency graphs (nodes/edges)
  - Methods: `get_workflow_dependency_graph`, `get_mcp_lineage_graph`
  - .py exists: implemented and documented
  - Action: Complete

### mcp/core/

- [x] **workflow_streaming_service.py.txt** → `WorkflowStreamingService`
  - Purpose: Real-time workflow event streaming
  - Methods: (from .txt)
  - .py exists: implemented and documented
  - Action: Complete
- [x] **workflow_definition_service.py.txt** → `WorkflowDefinitionService`
  - Purpose: CRUD and logic for workflow definitions
  - .py exists: implemented and documented
  - Action: Complete
- [x] **workflow_engine_service.py.txt** → `WorkflowEngineService`
  - Purpose: Core workflow execution logic (step sequencing, executor invocation, streaming updates)
  - .py exists: implemented and documented
  - Action: Complete
- [x] **mcp_registry_service.py.txt** → `MCPRegistryService`
  - Purpose: Registry for MCPs (discovery, versioning)
  - .py exists: implemented and documented
  - Action: Complete
- [x] **auditing_service.py.txt** → `AuditingService`
  - Purpose: Audit logging for actions/events
  - .py exists: implemented and documented
  - Action: Complete
- [x] **config.py.txt** → `Config`
  - Purpose: Configuration management
  - .py exists: implemented and documented
  - Action: Complete
- [x] **mcp_configs.py.txt** → `MCPConfigPayload` and related
  - Purpose: Typed config models for MCPs
  - .py exists: implemented and documented
  - Action: Complete

### mcp/core/security/

- [x] **rbac_service.py.txt** → `RBACService`
  - Purpose: Role-based access control
  - .py exists: implemented and documented
  - Action: Complete
- [x] **jwt_manager.py.txt** → `JWTManager`
  - Purpose: JWT token management
  - .py exists: implemented and documented
  - Action: Complete (.txt removed)

### mcp/core/executors/

- [ ] **base_executor.py.txt** → `BaseExecutor`
  - Purpose: Base class for all executors
  - .py exists: empty
  - Action: Implement
- [x] **script_executor.py.txt** → `ScriptExecutor`
  - Purpose: Execute script MCPs
  - .py exists: implemented and documented
  - Action: Complete
- [x] **notebook_executor.py.txt** → `NotebookExecutor`
  - Purpose: Execute notebook MCPs
  - .py exists: implemented and documented
  - Action: Complete
- [x] **llm_executor.py.txt** → `LLMExecutor`
  - Purpose: Execute LLM MCPs
  - .py exists: implemented and documented
  - Action: Complete
- [ ] **streamlit_executor.py.txt** → `StreamlitExecutor`
  - Purpose: Execute Streamlit MCPs
  - .py exists: empty
  - Action: Implement

### mcp/core/pubsub/

- [ ] **base_pubsub.py.txt** → `BasePubSub`
  - Purpose: Pub/Sub abstraction
  - .py exists: empty
  - Action: Implement
- [x] **base_pubsub.py.txt** → `BasePubSub`
  - Purpose: Pub/Sub abstraction
  - .py exists: implemented and documented
  - Action: Complete (.txt removed)
- [x] **redis_pubsub.py.txt** → `RedisPubSub`
  - Purpose: Redis-based Pub/Sub
  - .py exists: implemented and documented
  - Action: Complete (.txt removed)

### mcp/db/models/

- [ ] **workflow_run.py.txt** → `WorkflowRun`
  - Purpose: Workflow run DB model
  - .py exists: empty
  - Action: Implement
- [x] **workflow_definition.py.txt** → `WorkflowDefinition`
  - Purpose: Workflow definition DB model
  - .py exists: implemented and documented
  - Action: Complete (.txt removed)
- [ ] **mcp_definition.py.txt** → `MCPDefinition`
  - Purpose: MCP definition DB model
  - .py exists: empty
  - Action: Implement
- [x] **user.py.txt** → `User`
  - Purpose: User DB model
  - .py exists: implemented and documented
  - Action: Complete (.txt removed)
- [x] **external_db_config.py.txt** → `ExternalDatabaseConfig`
  - Purpose: External DB config DB model
  - .py exists: implemented and documented
  - Action: Complete (.txt removed)
- [ ] **action_log.py.txt** → `ActionLog`
  - Purpose: Action log DB model
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete

### mcp/db/crud/

- [ ] **crud_workflow_run.py.txt** → CRUD for WorkflowRun
  - Purpose: CRUD logic for workflow runs
  - .py exists: empty
  - Action: Implement
- [ ] **crud_workflow_definition.py.txt** → CRUD for WorkflowDefinition
  - Purpose: CRUD logic for workflow definitions
  - .py exists: empty
  - Action: Implement
- [ ] **crud_mcp_definition.py.txt** → CRUD for MCPDefinition
  - Purpose: CRUD logic for MCP definitions
  - .py exists: empty
  - Action: Implement
- [ ] **crud_user.py.txt** → CRUD for User
  - Purpose: CRUD logic for users
  - .py exists: empty
  - Action: Implement
- [ ] **crud_action_log.py.txt** → CRUD for ActionLog
  - Purpose: CRUD logic for action logs
  - .py exists: empty
  - Action: Implement
- [ ] **crud_external_db_config.py.txt** → CRUD for ExternalDatabaseConfig
  - Purpose: CRUD logic for external DB configs
  - .py exists: empty
  - Action: Implement
- [ ] **base_crud.py.txt** → Base CRUD class
  - Purpose: Base class for CRUD logic
  - .py exists: empty
  - Action: Implement

### mcp/external_db/connectors/

- [ ] **base_connector.py.txt** → `BaseDBConnector`
  - Purpose: Abstract base for DB connectors
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete
- [ ] **postgresql_connector.py.txt** → `PostgreSQLConnector`
  - Purpose: PostgreSQL DB connector
  - .py exists: empty
  - Action: Implement
- [ ] **bigquery_connector.py.txt** → `BigQueryConnector`
  - Purpose: BigQuery DB connector
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete

### mcp/monitoring/

- [ ] **metrics_router.py.txt** → Metrics API router
  - Purpose: API endpoints for metrics
  - .py exists: empty
  - Action: Implement
- [ ] **health_router.py.txt** → Health check API router
  - Purpose: API endpoints for health checks
  - .py exists: empty
  - Action: Implement

### mcp/api/routers/

- [ ] **workflow_execution_routes.py.txt** → Workflow execution API
  - Purpose: API endpoints for workflow execution
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete
- [ ] **workflow_definition_routes.py.txt** → Workflow definition API
  - Purpose: API endpoints for workflow definitions
  - .py exists: empty
  - Action: Implement
- [ ] **mcp_definition_routes.py.txt** → MCP definition API
  - Purpose: API endpoints for MCP definitions
  - .py exists: empty
  - Action: Implement
- [ ] **streaming_routes.py.txt** → Streaming API
  - Purpose: API endpoints for streaming events
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete
- [ ] **external_db_config_routes.py.txt** → External DB config API
  - Purpose: API endpoints for external DB configs
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete
- [ ] **entity_routes.py.txt** → Entity API
  - Purpose: API endpoints for entities
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete
- [ ] **dashboard_routes.py.txt** → Dashboard API
  - Purpose: API endpoints for dashboard
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete
- [ ] **auth_routes.py.txt** → Auth API
  - Purpose: API endpoints for authentication
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete

### mcp/api/schemas/

- [ ] **workflow_definition_schemas.py.txt** → Workflow definition schemas
  - Purpose: Pydantic schemas for workflow definitions
  - .py exists: empty
  - Action: Implement
- [ ] **workflow_run_schemas.py.txt** → Workflow run schemas
  - Purpose: Pydantic schemas for workflow runs
  - .py exists: empty
  - Action: Implement
- [ ] **mcp_definition_schemas.py.txt** → MCP definition schemas
  - Purpose: Pydantic schemas for MCP definitions
  - .py exists: empty
  - Action: Implement
- [ ] **mcp_version_schemas.py.txt** → MCP version schemas
  - Purpose: Pydantic schemas for MCP versions
  - .py exists: empty
  - Action: Implement
- [ ] **external_db_config_schemas.py.txt** → External DB config schemas
  - Purpose: Pydantic schemas for external DB configs
  - .py exists: empty
  - Action: Implement
- [ ] **dashboard_schemas.py.txt** → Dashboard schemas
  - Purpose: Pydantic schemas for dashboard
  - .py exists: empty
  - Action: Implement
- [ ] **entity_schemas.py.txt** → Entity schemas
  - Purpose: Pydantic schemas for entities
  - .py exists: empty
  - Action: Implement
- [ ] **auth_schemas.py.txt** → Auth schemas
  - Purpose: Pydantic schemas for auth
  - .py exists: implemented (review if complete)
  - Action: Review/delete .txt if .py is complete

---

**Instructions:**

- For each [ ] item, implement the class/service/schema as described.
- For items marked "review/delete .txt if .py is complete," check if the .py is fully implemented and remove the .txt if so.
- Document every class/service with a clear docstring and method descriptions.
