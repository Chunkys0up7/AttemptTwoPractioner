# Workflow Definitions API Documentation

## Overview

The Workflow Definitions API provides endpoints for managing and querying workflow definitions and their steps. This API is part of the MCP (Machine Configuration Platform) system and is designed to handle complex workflow configurations and executions.

## Authentication

All endpoints require authentication using JWT tokens. The token should be provided in the Authorization header:

```
Authorization: Bearer <your-token>
```

## Rate Limiting

- Maximum requests per minute: 100
- Maximum concurrent requests: 10
- Workflow steps have separate rate limits

## Error Responses

All endpoints return standardized error responses with the following structure:

```json
{
    "detail": "Error description",
    "request_id": "unique-request-id",
    "timestamp": "ISO timestamp"
}
```

## Endpoints

### List Workflow Definitions

```
GET /api/v1/workflow-definitions
```

List all workflow definitions with optional filtering.

#### Query Parameters

- `skip`: Number of items to skip (default: 0)
- `limit`: Maximum number of items to return (default: 100, max: 200)
- `search`: Search term to filter workflows by name or description
- `mcp_type`: Filter workflows containing steps of this MCP type
- `include_archived`: Include archived workflows (default: false)

#### Response

```json
{
    "total": 100,
    "items": [
        {
            "id": 1,
            "name": "string",
            "description": "string",
            "created_at": "ISO timestamp",
            "updated_at": "ISO timestamp",
            "steps": [
                {
                    "id": 1,
                    "mcp_type": "string",
                    "order": 1,
                    "config": {}
                }
            ]
        }
    ]
}
```

### Get Workflow Definition

```
GET /api/v1/workflow-definitions/{id}
```

Get a specific workflow definition by ID.

#### Path Parameters

- `id`: Workflow definition ID

#### Response

```json
{
    "id": 1,
    "name": "string",
    "description": "string",
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "steps": [
        {
            "id": 1,
            "mcp_type": "string",
            "order": 1,
            "config": {}
        }
    ]
}
```

### Create Workflow Definition

```
POST /api/v1/workflow-definitions
```

Create a new workflow definition.

#### Request Body

```json
{
    "name": "string",
    "description": "string",
    "steps": [
        {
            "mcp_type": "string",
            "order": 1,
            "config": {}
        }
    ]
}
```

#### Response

```json
{
    "id": 1,
    "name": "string",
    "description": "string",
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "steps": [
        {
            "id": 1,
            "mcp_type": "string",
            "order": 1,
            "config": {}
        }
    ]
}
```

### Update Workflow Definition

```
PUT /api/v1/workflow-definitions/{id}
```

Update an existing workflow definition.

#### Path Parameters

- `id`: Workflow definition ID

#### Request Body

```json
{
    "name": "string",
    "description": "string",
    "steps": [
        {
            "id": 1,
            "mcp_type": "string",
            "order": 1,
            "config": {}
        }
    ]
}
```

#### Response

```json
{
    "id": 1,
    "name": "string",
    "description": "string",
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "steps": [
        {
            "id": 1,
            "mcp_type": "string",
            "order": 1,
            "config": {}
        }
    ]
}
```

### Delete Workflow Definition

```
DELETE /api/v1/workflow-definitions/{id}
```

Delete a workflow definition and all its steps.

#### Path Parameters

- `id`: Workflow definition ID

#### Response

```json
{
    "id": 1,
    "name": "string",
    "description": "string",
    "created_at": "ISO timestamp",
    "updated_at": "ISO timestamp",
    "steps": [
        {
            "id": 1,
            "mcp_type": "string",
            "order": 1,
            "config": {}
        }
    ]
}
```

## Health Check

```
GET /api/v1/health
```

Get system health status.

#### Response

```json
{
    "status": "healthy",
    "components": {
        "database": {
            "status": "healthy",
            "details": {
                "last_check": "ISO timestamp",
                "error": null
            }
        },
        "redis": {
            "status": "healthy",
            "details": {
                "last_check": "ISO timestamp",
                "error": null
            }
        },
        "system": {
            "status": "healthy",
            "details": {
                "last_check": "ISO timestamp",
                "error": null
            }
        }
    },
    "timestamp": "ISO timestamp"
}
```

## Security

The API uses JWT-based authentication and implements the following security measures:

- Rate limiting
- Input validation
- Circuit breaker pattern
- Request ID tracking
- Error logging
- Security headers

## Performance

The API implements several performance optimizations:

- Redis caching for frequently accessed data
- Query optimization to prevent N+1 queries
- Connection pooling
- Response compression
- Circuit breaker to prevent cascading failures
