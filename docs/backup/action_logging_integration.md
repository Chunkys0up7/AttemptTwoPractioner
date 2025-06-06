# Action Logging Integration

This document describes how action logging is integrated into various parts of the MCP Backend system.

## Integration Points

### 1. CRUD Operations

Action logging is integrated into all CRUD operations through the service layer. Each service method that performs a database operation creates an action log entry.

#### MCP Definition Service
```python
class MCPDefinitionService:
    def create_mcp_definition(self, data: MCPDefinitionCreate) -> MCPDefinition:
        mcp_def = MCPDefinition(**data.dict())
        self.db.add(mcp_def)
        self.db.commit()
        
        # Log the creation
        self.auditing_service.create_action_log_entry(
            actor_id=self.get_current_user(),
            action_type=ActionType.CREATE,
            entity_type=EntityType.MCP_DEFINITION,
            entity_id=mcp_def.id,
            details=data.dict()
        )
        return mcp_def
```

#### Workflow Service
```python
class WorkflowService:
    def start_workflow_run(self, workflow_id: int, parameters: Dict) -> WorkflowRun:
        run = WorkflowRun(workflow_definition_id=workflow_id, parameters=parameters)
        self.db.add(run)
        self.db.commit()
        
        # Log the workflow start
        self.auditing_service.create_action_log_entry(
            actor_id=self.get_current_user(),
            action_type=ActionType.CREATE,
            entity_type=EntityType.WORKFLOW_RUN,
            entity_id=run.id,
            details={"status": run.status.value, "parameters": parameters}
        )
        return run
```

### 2. Workflow Engine Integration

The workflow engine logs various events during workflow execution:

```python
class WorkflowEngineService:
    def update_workflow_status(self, run_id: int, status: WorkflowRunStatus):
        run = self.get_workflow_run(run_id)
        run.status = status
        self.db.commit()
        
        # Log the status change
        self.auditing_service.create_action_log_entry(
            actor_id="system",  # System-initiated action
            action_type=ActionType.UPDATE,
            entity_type=EntityType.WORKFLOW_RUN,
            entity_id=run_id,
            details={"status": status.value, "previous_status": run.status.value}
        )
```

### 3. Actor ID Capture

The actor ID is captured from the request context using a FastAPI dependency:

```python
async def get_current_user(request: Request) -> str:
    """Get the current user ID from the request context."""
    # In a real implementation, this would extract the user ID from the auth token
    return request.headers.get("X-User-ID", "system")

@app.post("/api/v1/mcp-definitions/")
async def create_mcp_definition(
    data: MCPDefinitionCreate,
    current_user: str = Depends(get_current_user)
):
    return mcp_service.create_mcp_definition(data, actor_id=current_user)
```

## Testing

The action logging integration is tested in `tests/integration/test_action_logging_integration.py`. The test suite includes:

1. `test_mcp_definition_crud_logging`: Tests logging for MCP definition CRUD operations
2. `test_workflow_run_logging`: Tests logging for workflow run operations
3. `test_actor_id_capture`: Tests that actor IDs are properly captured
4. `test_log_entry_ordering`: Tests that log entries are properly ordered

## Error Handling

The action logging integration includes error handling:

1. **Database Errors**
   - If logging fails, the original operation is still committed
   - Logging errors are caught and logged to the application log

2. **Missing Actor ID**
   - If no actor ID is provided, "system" is used as a fallback
   - This ensures all actions are logged, even system-initiated ones

## Future Enhancements

Potential improvements to the action logging integration:

1. **Authentication Integration**
   - Integrate with a proper authentication system
   - Extract user information from JWT tokens
   - Add role-based logging

2. **Performance Optimization**
   - Implement batch logging for bulk operations
   - Add caching for frequently accessed log entries
   - Optimize log entry queries

3. **Enhanced Context**
   - Add request metadata to log entries
   - Include IP addresses and user agents
   - Track related actions across services

4. **Monitoring and Alerts**
   - Add monitoring for suspicious activities
   - Implement alerting for critical operations
   - Create audit reports 