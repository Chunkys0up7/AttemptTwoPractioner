# Heterogeneous Entity Details Endpoint

This document describes the implementation of the heterogeneous entity details endpoint in the MCP Backend.

## Overview

The heterogeneous entity details endpoint provides a unified way to fetch details for different types of entities in the system. It supports various entity types such as MCP versions and workflow runs, with the ability to easily extend to support additional entity types in the future.

## API Endpoint

### GET `/api/v1/entities/{entity_type}/{entity_id}`

Returns detailed information about a specific entity based on its type and ID.

#### Path Parameters
- `entity_type`: The type of entity to fetch (e.g., "mcp_version", "workflow_run")
- `entity_id`: The unique identifier of the entity

#### Supported Entity Types
1. `mcp_version`: MCP Version details
2. `workflow_run`: Workflow Run details

#### Response Format
The response format varies based on the entity type:

##### MCP Version Response
```json
{
    "id": 1,
    "version": "1.0.0",
    "mcp_definition_id": 1,
    "description": "Test version",
    "created_at": "2024-03-14T12:00:00Z",
    "updated_at": "2024-03-14T12:00:00Z"
}
```

##### Workflow Run Response
```json
{
    "id": 1,
    "workflow_definition_id": 1,
    "status": "RUNNING",
    "created_at": "2024-03-14T12:00:00Z",
    "ended_at": null,
    "parameters": {}
}
```

## Error Handling

The endpoint handles various error cases:

1. **Invalid Entity Type** (400 Bad Request)
   ```json
   {
       "detail": "Invalid entity type: invalid_type"
   }
   ```

2. **Entity Not Found** (404 Not Found)
   ```json
   {
       "detail": "Entity not found"
   }
   ```

3. **Invalid Entity ID** (422 Unprocessable Entity)
   ```json
   {
       "detail": [
           {
               "loc": ["path", "entity_id"],
               "msg": "value is not a valid integer",
               "type": "type_error.integer"
           }
       ]
   }
   ```

## Implementation Details

### Entity Routes

The entity routes are defined in `mcp/api/routers/entity_routes.py`. The router is registered in `main.py` under the `/api/v1/entities` prefix.

### Entity Service

The entity service (`mcp/core/services/entity_service.py`) is responsible for:
1. Validating entity types
2. Fetching entity details from the database
3. Converting database models to response schemas

### Testing

The entity endpoint is tested in `tests/api/test_entity_routes.py`. The test suite includes:

1. `test_get_mcp_version_details`: Tests fetching MCP version details
2. `test_get_workflow_run_details`: Tests fetching workflow run details
3. `test_get_nonexistent_entity`: Tests handling of nonexistent entities
4. `test_get_invalid_entity_type`: Tests handling of invalid entity types
5. `test_get_entity_with_invalid_id`: Tests handling of invalid entity IDs

## Future Enhancements

Potential improvements to the entity endpoint:
1. Add support for more entity types
2. Implement caching for frequently accessed entities
3. Add filtering and pagination for related entities
4. Include more detailed information in responses
5. Add support for bulk entity fetching 