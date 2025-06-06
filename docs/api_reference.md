# MCP Backend API Reference

This document provides a comprehensive reference for the MCP Backend API endpoints, schemas, and authentication methods.

## Base URL

All API endpoints are prefixed with `/api/v1`.

## Authentication

### API Key Authentication

Most endpoints require API key authentication. Include the API key in the `X-API-Key` header:

```http
X-API-Key: mcp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Session Authentication (Future)

Session-based authentication will be implemented in the future using JWT tokens.

## Endpoints

### Health Check

```http
GET /health
```

Returns the health status of the API.

**Response:**

```json
{
  "status": "healthy",
  "version": "1.0.0"
}
```

### MCP Definitions

#### List MCP Definitions

```http
GET /mcp-definitions
```

Query Parameters:

- `skip` (int, optional): Number of records to skip
- `limit` (int, optional): Maximum number of records to return
- `mcp_type` (string, optional): Filter by MCP type

**Response:**

```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "description": "string",
      "mcp_type": "string",
      "created_at": "string",
      "updated_at": "string",
      "latest_version": {
        "id": "string",
        "version": "string",
        "config": {
          "type": "string"
          // Type-specific configuration
        }
      }
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 10
}
```

#### Create MCP Definition

```http
POST /mcp-definitions
```

**Request Body:**

```json
{
  "name": "string",
  "description": "string",
  "mcp_type": "string",
  "config": {
    "type": "string"
    // Type-specific configuration
  }
}
```

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "mcp_type": "string",
  "created_at": "string",
  "updated_at": "string",
  "latest_version": {
    "id": "string",
    "version": "string",
    "config": {
      "type": "string"
      // Type-specific configuration
    }
  }
}
```

#### Get MCP Definition

```http
GET /mcp-definitions/{definition_id}
```

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "mcp_type": "string",
  "created_at": "string",
  "updated_at": "string",
  "versions": [
    {
      "id": "string",
      "version": "string",
      "config": {
        "type": "string"
        // Type-specific configuration
      },
      "created_at": "string"
    }
  ]
}
```

#### Update MCP Definition

```http
PUT /mcp-definitions/{definition_id}
```

**Request Body:**

```json
{
  "name": "string",
  "description": "string"
}
```

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "mcp_type": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

#### Delete MCP Definition

```http
DELETE /mcp-definitions/{definition_id}
```

**Response:**

```json
{
  "message": "MCP definition deleted successfully"
}
```

### Workflow Management

#### Start Workflow Run

```http
POST /workflow-runs
```

**Request Body:**

```json
{
  "workflow_definition_id": "string",
  "parameters": {
    // Workflow-specific parameters
  }
}
```

**Response:**

```json
{
  "id": "string",
  "workflow_definition_id": "string",
  "status": "string",
  "parameters": {
    // Workflow-specific parameters
  },
  "created_at": "string",
  "updated_at": "string"
}
```

#### Get Workflow Run Status

```http
GET /workflow-runs/{run_id}
```

**Response:**

```json
{
  "id": "string",
  "workflow_definition_id": "string",
  "status": "string",
  "parameters": {
    // Workflow-specific parameters
  },
  "result": {
    // Workflow result data
  },
  "created_at": "string",
  "updated_at": "string"
}
```

#### Stream Workflow Run Events

```http
GET /workflow-runs/{run_id}/stream
```

Server-Sent Events endpoint that streams workflow run updates.

**Event Types:**

- `status_change`: Workflow status updates
- `log`: Log messages
- `result_preview`: Partial results

### External Database Configuration

#### List External Database Configurations

```http
GET /external-db-configs
```

**Response:**

```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "db_type": "string",
      "host": "string",
      "port": "integer",
      "db_name": "string",
      "username": "string",
      "created_at": "string",
      "updated_at": "string"
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 10
}
```

#### Create External Database Configuration

```http
POST /external-db-configs
```

**Request Body:**

```json
{
  "name": "string",
  "db_type": "string",
  "host": "string",
  "port": "integer",
  "db_name": "string",
  "username": "string",
  "password": "string"
}
```

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "db_type": "string",
  "host": "string",
  "port": "integer",
  "db_name": "string",
  "username": "string",
  "created_at": "string",
  "updated_at": "string"
}
```

### Dashboard

#### Get Dashboard Summary

```http
GET /dashboard/summary
```

**Response:**

```json
{
  "total_mcps": 0,
  "active_workflows": 0,
  "recent_workflow_runs": [
    {
      "id": "string",
      "workflow_definition_id": "string",
      "status": "string",
      "created_at": "string"
    }
  ],
  "system_health": {
    "status": "string",
    "metrics": {
      // System metrics
    }
  }
}
```

### Entity Details

#### Get Entity Details

```http
GET /entities/{entity_type}/{entity_id}
```

**Response:**

```json
{
  "id": "string",
  "type": "string",
  "data": {
    // Entity-specific data
  },
  "related_entities": [
    {
      "id": "string",
      "type": "string",
      "relationship": "string"
    }
  ]
}
```

### API Key Management

#### List API Keys

```http
GET /api-keys
```

**Response:**

```json
{
  "items": [
    {
      "id": "string",
      "name": "string",
      "prefix": "string",
      "created_at": "string",
      "last_used_at": "string"
    }
  ],
  "total": 0,
  "skip": 0,
  "limit": 10
}
```

#### Create API Key

```http
POST /api-keys
```

**Request Body:**

```json
{
  "name": "string"
}
```

**Response:**

```json
{
  "id": "string",
  "name": "string",
  "key": "string",
  "prefix": "string",
  "created_at": "string"
}
```

#### Delete API Key

```http
DELETE /api-keys/{key_id}
```

**Response:**

```json
{
  "message": "API key deleted successfully"
}
```

### Performance Metrics

#### Get Performance Metrics

```http
GET /metrics
```

Returns metrics in Prometheus format.

#### Get Metrics Summary

```http
GET /metrics/summary
```

**Response:**

```json
{
  "http_requests": {
    "total": 0,
    "success_rate": 0.0,
    "average_latency": 0.0
  },
  "database_operations": {
    "total": 0,
    "average_latency": 0.0
  },
  "workflow_steps": {
    "total": 0,
    "success_rate": 0.0,
    "average_duration": 0.0
  }
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "detail": "Invalid request parameters"
}
```

### 401 Unauthorized

```json
{
  "detail": "Invalid API key"
}
```

### 403 Forbidden

```json
{
  "detail": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
  "detail": "Resource not found"
}
```

### 429 Too Many Requests

```json
{
  "detail": "Rate limit exceeded"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

## Rate Limiting

The API implements rate limiting:

- 100 requests per minute per IP address
- Rate limit headers are included in responses:
  - `X-RateLimit-Limit`: Maximum requests per window
  - `X-RateLimit-Remaining`: Remaining requests in current window
  - `X-RateLimit-Reset`: Time until rate limit resets

## Security Headers

All responses include the following security headers:

- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: DENY`
- `X-XSS-Protection: 1; mode=block`
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'`
- `Referrer-Policy: strict-origin-when-cross-origin`
- `Permissions-Policy: geolocation=(), microphone=(), camera=()`

## Documentation Update Best Practices

- For every new or changed API endpoint, update this file with request/response examples, authentication, and error handling details.
- Ensure all endpoints are documented with clear descriptions and sample payloads.
- When authentication or security changes, update the relevant sections.
- Annotate major changes in the changelog below.

## Changelog

- [YYYY-MM-DD] Documentation best practices and changelog section added.
- [YYYY-MM-DD] All outstanding technical tasks completed and documented.
- [YYYY-MM-DD] Initial API reference created.
