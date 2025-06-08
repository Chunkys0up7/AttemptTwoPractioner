# API Documentation

> **Note:** All user IDs are now UUIDs (universally unique identifiers, e.g., "id": "b3b7c2e2-8c2a-4e2a-9c2a-8c2a4e2a9c2a").

## 1. Authentication API

### 1.1 Login

```http
POST /api/auth/login
```

#### Request Body
```json
{
  "username": "string",
  "password": "string"
}
```

#### Response
```json
{
  "access_token": "string",
  "refresh_token": "string",
  "token_type": "bearer",
  "expires_in": 3600,
  "user": {
    "id": "uuid-string",
    "username": "string",
    "roles": ["string"]
  }
}
```

### 1.2 Refresh Token

```http
POST /api/auth/refresh
```

#### Request Body
```json
{
  "refresh_token": "string"
}
```

#### Response
```json
{
  "access_token": "string",
  "token_type": "bearer",
  "expires_in": 3600
}
```

### 1.3 Change Password

```http
POST /api/v1/auth/change-password
```

#### Request Body
```json
{
  "current_password": "string",
  "new_password": "string"
}
```

#### Response (Success)
```json
{
  "message": "Password changed successfully"
}
```

#### Response (Failure)
```json
{
  "detail": "Current password is incorrect"
}
```

## 2. Components API

### 2.1 List Components

```http
GET /api/components
```

#### Query Parameters
- `type`: Filter by component type (Python Script, TypeScript Script, etc.)
- `tag`: Filter by tag
- `search`: Search term
- `page`: Page number
- `limit`: Items per page

#### Response
```json
{
  "items": [
    {
      "id": "uuid-string",
      "name": "string",
      "type": "string",
      "description": "string",
      "version": "string",
      "tags": ["string"],
      "input_schema": "json",
      "output_schema": "json",
      "compliance": ["string"],
      "cost_tier": "string",
      "visibility": "string",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "total": number,
  "page": number,
  "limit": number
}
```

### 2.2 Create Component

```http
POST /api/components
```

#### Request Body
```json
{
  "name": "string",
  "type": "string",
  "description": "string",
  "version": "string",
  "tags": ["string"],
  "input_schema": "json",
  "output_schema": "json",
  "compliance": ["string"],
  "cost_tier": "string",
  "visibility": "string",
  "type_specific_data": {
    // Type-specific data based on component type
  }
}
```

## 3. Workflows API

### 3.1 List Workflows

```http
GET /api/workflows
```

#### Response
```json
{
  "items": [
    {
      "id": "uuid-string",
      "name": "string",
      "description": "string",
      "version": "string",
      "components": ["uuid-string"],
      "connections": ["uuid-string"],
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "total": number,
  "page": number,
  "limit": number
}
```

### 3.2 Create Workflow

```http
POST /api/workflows
```

#### Request Body
```json
{
  "name": "string",
  "description": "string",
  "components": ["uuid-string"],
  "connections": ["uuid-string"],
  "version": "string"
}
```

## 4. Execution API

### 4.1 Start Execution

```http
POST /api/executions
```

#### Request Body
```json
{
  "workflow_id": "uuid-string",
  "inputs": {
    "component_id": {
      "input_name": "value"
    }
  }
}
```

#### Response
```json
{
  "execution_id": "uuid-string",
  "status": "string",
  "started_at": "timestamp"
}
```

### 4.2 Get Execution Status

```http
GET /api/executions/{execution_id}
```

#### Response
```json
{
  "execution_id": "uuid-string",
  "status": "string",
  "started_at": "timestamp",
  "completed_at": "timestamp",
  "results": {
    "component_id": {
      "output_name": "value"
    }
  }
}
```

## 5. Error Responses

All endpoints may return the following error responses:

```json
{
  "error": {
    "code": "string",
    "message": "string",
    "details": {
      "field": "error description"
    }
  }
}
```

### Common Error Codes
- `AUTH_001`: Invalid credentials
- `AUTH_002`: Token expired
- `COMP_001`: Component not found
- `COMP_002`: Invalid component type
- `WF_001`: Workflow not found
- `WF_002`: Invalid workflow configuration
- `EXEC_001`: Execution failed
- `EXEC_002`: Execution timeout

## 6. Rate Limiting

- Maximum 100 requests per minute
- Maximum 10 concurrent executions
- Maximum 1000 components per user
- Maximum 100 workflows per user

## 7. Security

- All endpoints require authentication
- Role-based access control
- Rate limiting
- Input validation
- API key management
- Audit logging

## 8. Versioning

- API version: v1
- Version format: /api/v1/
- Breaking changes will increment major version
- Non-breaking changes will increment minor version

## 9. Authentication

- Bearer token authentication
- Refresh token support
- Token expiration: 1 hour
- Refresh token expiration: 7 days

## 10. Best Practices

1. Always validate input data
2. Handle errors gracefully
3. Use proper error codes
4. Implement proper logging
5. Follow rate limits
6. Use proper authentication
7. Validate API keys
8. Follow security guidelines

## 11. API Keys

### Create API Key

```http
POST /api/api-keys
```

### Revoke API Key

```http
DELETE /api/api-keys/{key_id}
```

### List API Keys

```http
GET /api/api-keys
```

## 12. Monitoring

### Get API Metrics

```http
GET /api/monitoring/metrics
```

### Get API Logs

```http
GET /api/monitoring/logs
```

## 13. Documentation Guidelines

1. All endpoints must be documented
2. Request/response formats must be specified
3. Error codes must be documented
4. Security considerations must be included
5. Rate limits must be documented
6. Versioning must be documented
7. Authentication must be documented
8. Best practices must be included
9. Monitoring endpoints must be documented
10. API keys must be documented

## User Preferences API

### Get User Preferences

Retrieves the current user's preferences.

```http
GET /api/preferences/me
```

#### Response

```json
{
  "theme": "dark",
  "language": "en",
  "notifications": {
    "email": true,
    "push": true,
    "in_app": true
  },
  "privacy": {
    "data_collection": true,
    "analytics": true,
    "personalization": true
  },
  "display": {
    "font_size": "medium",
    "density": "comfortable",
    "animations": true
  }
}
```

### Update User Preferences

Updates the current user's preferences.

```http
PUT /api/preferences/me
```

#### Request Body

```json
{
  "theme": "light",
  "language": "fr",
  "notifications": {
    "email": false,
    "push": true,
    "in_app": true
  },
  "privacy": {
    "data_collection": false,
    "analytics": true,
    "personalization": false
  },
  "display": {
    "font_size": "large",
    "density": "compact",
    "animations": false
  }
}
```

#### Response

Returns the updated preferences object.

### Reset User Preferences

Resets the current user's preferences to default values.

```http
DELETE /api/preferences/me
```

#### Response

Returns the default preferences object.

## Error Responses

### 400 Bad Request

```json
{
  "error": "Invalid request",
  "message": "Invalid preference value for theme"
}
```

### 401 Unauthorized

```json
{
  "error": "Unauthorized",
  "message": "Authentication required"
}
```

### 403 Forbidden

```json
{
  "error": "Forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
  "error": "Not found",
  "message": "User preferences not found"
}
```

### 500 Server Error

```json
{
  "error": "Server error",
  "message": "Internal server error"
}
```

## Data Types

### UserPreferences

```typescript
interface UserPreferences {
  theme: 'light' | 'dark' | 'system';
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    in_app: boolean;
  };
  privacy: {
    data_collection: boolean;
    analytics: boolean;
    personalization: boolean;
  };
  display: {
    font_size: 'small' | 'medium' | 'large';
    density: 'compact' | 'comfortable' | 'spacious';
    animations: boolean;
  };
}
```

## Version History

### v1.0.0 (2024-03-20)

- Initial release
- Basic CRUD operations for user preferences
- Support for theme, language, notifications, privacy, and display settings

### v1.1.0 (2024-03-21)

- Added offline support
- Added sync functionality
- Added conflict resolution
- Added migration support

## Integration Guide

### Authentication

All API endpoints require authentication. Include the authentication token in the request header:

```http
Authorization: Bearer <token>
```

### Rate Limiting

The API is rate limited to 100 requests per minute per user. Rate limit headers are included in the response:

```http
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: 1616284800
```

### Error Handling

Handle errors by checking the response status code and error message. Implement retry logic with exponential backoff for 5xx errors.

### Offline Support

The API supports offline operations through the sync system. Changes made while offline are queued and synchronized when the connection is restored.

### Webhooks

You can subscribe to preference change events by registering a webhook URL. The webhook will be called with the following payload:

```json
{
  "event": "preferences.updated",
  "data": {
    "user_id": "uuid-string",
    "preferences": {
      // Updated preferences object
    },
    "timestamp": "2024-03-21T12:00:00Z"
  }
}
```

## Examples

### JavaScript/TypeScript

```typescript
import { api } from './api';

// Get preferences
const getPreferences = async () => {
  try {
    const response = await api.get('/preferences/me');
    return response.data;
  } catch (error) {
    console.error('Failed to get preferences:', error);
    throw error;
  }
};

// Update preferences
const updatePreferences = async preferences => {
  try {
    const response = await api.put('/preferences/me', preferences);
    return response.data;
  } catch (error) {
    console.error('Failed to update preferences:', error);
    throw error;
  }
};

// Reset preferences
const resetPreferences = async () => {
  try {
    const response = await api.delete('/preferences/me');
    return response.data;
  } catch (error) {
    console.error('Failed to reset preferences:', error);
    throw error;
  }
};
```

### Python

```python
import requests

API_URL = 'https://api.example.com'
TOKEN = 'your-auth-token'

headers = {
    'Authorization': f'Bearer {TOKEN}',
    'Content-Type': 'application/json'
}

def get_preferences():
    response = requests.get(f'{API_URL}/preferences/me', headers=headers)
    response.raise_for_status()
    return response.json()

def update_preferences(preferences):
    response = requests.put(f'{API_URL}/preferences/me', json=preferences, headers=headers)
    response.raise_for_status()
    return response.json()

def reset_preferences():
    response = requests.delete(f'{API_URL}/preferences/me', headers=headers)
    response.raise_for_status()
    return response.json()
```

### cURL

```bash
# Get preferences
curl -X GET \
  'https://api.example.com/preferences/me' \
  -H 'Authorization: Bearer your-auth-token'

# Update preferences
curl -X PUT \
  'https://api.example.com/preferences/me' \
  -H 'Authorization: Bearer your-auth-token' \
  -H 'Content-Type: application/json' \
  -d '{
    "theme": "light",
    "language": "en"
  }'

# Reset preferences
curl -X DELETE \
  'https://api.example.com/preferences/me' \
  -H 'Authorization: Bearer your-auth-token'
```

## Notification System API

### Get Notifications

Retrieves the current user's notifications.

```http
GET /api/notifications
```

#### Query Parameters

- `severity` (optional): Filter by severity ('high', 'medium', 'low')
- `type` (optional): Filter by notification type
- `search` (optional): Search in notification messages
- `start` (optional): Start date for filtering
- `end` (optional): End date for filtering

#### Example Response
```json
{
  "data": [
    {
      "id": "uuid-string",
      "metricName": "string",
      "severity": "high",
      "message": "string",
      "timestamp": "2024-03-21T10:00:00Z",
      "acknowledged": false,
      "value": 42,
      "threshold": 50
    }
  ],
  "error": null
}
```

### Acknowledge Notification

Marks a notification as acknowledged.

```http
POST /api/notifications/{id}/acknowledge
```

#### Example Response
```json
{
  "data": {
    "id": "uuid-string",
    "acknowledged": true
  },
  "error": null
}
```

### Get Notification Analytics

Retrieves analytics data for notifications.

```http
GET /api/notifications/analytics
```

#### Query Parameters
- `start` (required): Start date for analytics
- `end` (required): End date for analytics

#### Example Response
```json
{
  "data": {
    "totalAlerts": 10,
    "acknowledgedAlerts": 8,
    "alertsBySeverity": {"high": 2, "medium": 5, "low": 3},
    "averageResponseTime": 120,
    "alertsByMetric": {"CPU": 4, "Memory": 6}
  },
  "error": null
}
```

#### Notes
- All endpoints require authentication.
- Standard error responses apply.

## Recommendation System API

### Get Recommendations

Retrieves personalized recommendations for the current user.

```http
GET /api/recommendations
```

#### Query Parameters
- `user_id` (optional, string): User identifier (default: demo)
- `category` (optional, string): Filter recommendations by category
- `top_n` (optional, integer): Number of recommendations to return (default: 3)

#### Example Request
```http
GET /api/recommendations?category=A&top_n=2
```

#### Example Response
```json
[
  {
    "id": 1,
    "title": "Example Recommendation",
    "score": 0.95,
    "category": "A"
  },
  {
    "id": 3,
    "title": "Third Recommendation",
    "score": 0.85,
    "category": "A"
  }
]
```

#### Notes
- Returns a list of recommended items (components, workflows, etc.) for the user.
- Results can be filtered by category and limited by top_n.
- Each item includes a relevance score (higher is more relevant).
- Requires authentication.
- Standard error responses apply.

## Workflow Templates API

### Create Workflow Template

```http
POST /api/templates
```

#### Request Body
```json
{
  "name": "string",
  "description": "string",
  "category": "string",
  "template_metadata": {"key": "value"},
  "is_public": true,
  "content": {"workflow": "definition"}
}
```

#### Response
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "category": "string",
  "template_metadata": {"key": "value"},
  "is_public": true,
  "created_by": "uuid-string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### List Workflow Templates

```http
GET /api/templates
```

#### Query Parameters
- `category`: Filter by category
- `search`: Search by name or description
- `public_only`: Boolean to list only public templates

#### Example Response
```json
{
  "items": [
    {
      "id": 1,
      "name": "string",
      "description": "string",
      "category": "string",
      "template_metadata": {"key": "value"},
      "is_public": true,
      "created_by": "uuid-string",
      "created_at": "timestamp",
      "updated_at": "timestamp"
    }
  ],
  "total": 1
}
```

### Get Workflow Template by ID

```http
GET /api/templates/{id}
```

#### Example Response
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "category": "string",
  "template_metadata": {"key": "value"},
  "is_public": true,
  "created_by": "uuid-string",
  "created_at": "timestamp",
  "updated_at": "timestamp",
  "versions": [
    {"id": 1, "version": 1, "content": {"workflow": "definition"}, "created_at": "timestamp"}
  ]
}
```

### Update Workflow Template

```http
PUT /api/templates/{id}
```

#### Request Body
```json
{
  "name": "string",
  "description": "string",
  "category": "string",
  "template_metadata": {"key": "value"},
  "is_public": true,
  "content": {"workflow": "definition"},
  "changes": "string"
}
```

#### Response
```json
{
  "id": 1,
  "name": "string",
  "description": "string",
  "category": "string",
  "template_metadata": {"key": "value"},
  "is_public": true,
  "created_by": "uuid-string",
  "created_at": "timestamp",
  "updated_at": "timestamp"
}
```

### Delete Workflow Template

```http
DELETE /api/templates/{id}
```

#### Response
```json
{
  "message": "Template deleted successfully"
}
```

### List Template Versions

```http
GET /api/templates/{id}/versions
```

#### Response
```json
{
  "versions": [
    {"id": 1, "version": 1, "content": {"workflow": "definition"}, "created_at": "timestamp"}
  ]
}
```

### Get Specific Template Version

```http
GET /api/templates/{id}/versions/{version}
```

#### Response
```json
{
  "id": 1,
  "template_id": 1,
  "version": 1,
  "content": {"workflow": "definition"},
  "changes": "string",
  "created_by": "uuid-string",
  "created_at": "timestamp"
}
```

### Search Templates

```http
GET /api/templates/search?query=example
```

#### Response
```json
{
  "items": [
    {"id": 1, "name": "string", "description": "string"}
  ],
  "total": 1
}
```

### Get Template Statistics

```http
GET /api/templates/stats
```

#### Response
```json
{
  "total_templates": 10,
  "public_templates": 5,
  "categories": 3
}
```

### List Template Categories

```http
GET /api/v1/templates/categories
```

#### Response
```json
[
  "Data Processing",
  "Machine Learning",
  "ETL",
  "Visualization",
  "Reporting",
  "Automation",
  "Custom"
]
```

## Performance Monitoring Endpoints

### Get Performance Report

Returns a JSON summary of key performance metrics and any current alerts.

```http
GET /api/v1/metrics/report
```

#### Example Response
```json
{
  "metrics": {
    "requests": {"count": 123, "latency": 0.12},
    "cache": {"hits": 100, "misses": 23, "hit_ratio": 0.81},
    "errors": {"total": 2}
  },
  "alerts": [
    "High request latency: 1.23s (threshold: 1.0s)",
    "Low cache hit ratio: 75.00% (threshold: 80.00%)"
  ]
}
```

### Reset Performance Metrics

Resets all in-memory performance metrics (admin only).

```http
POST /api/v1/metrics/reset
```

#### Example Response
```json
{
  "message": "Performance metrics reset."
}
```

### Dashboard Visualization

Returns a summary of key performance metrics and alerts for dashboard visualization.

```http
GET /api/v1/metrics/dashboard
```

#### Example Response
```json
{
  "metrics": { ... },
  "alerts": [ ... ],
  "dashboard": {
    "uptime": 12345,
    "request_count": 100,
    "error_count": 2,
    "cache_hit_ratio": 0.85,
    "active_alerts": 1
  }
}
```

## Changelog

- [YYYY-MM-DD] Added/updated documentation for recommendations, notifications, workflow templates, and performance monitoring endpoints. Expanded examples and clarified authentication/error handling for new endpoints.

## Notifications API

### POST /api/notifications
Send a notification to a user.
- **Request Body:**
  - `user_id` (string, required)
  - `message` (string, required)
  - `type_` (string, optional, default: "info")
- **Response:**
  - Notification object
- **Example:**
```json
{
  "user_id": "user123",
  "message": "You have a new message!",
  "type_": "info"
}
```

### GET /api/notifications
Fetch notifications for a user.
- **Query Params:**
  - `user_id` (string, required)
  - `unread_only` (bool, optional)
- **Response:**
  - List of notification objects
- **Example:**
`/api/notifications?user_id=user123&unread_only=true`

### POST /api/notifications/read
Mark a notification as read.
- **Request Body:**
  - `user_id` (string, required)
  - `notification_id` (string, required)
- **Response:**
  - `{ "success": true }`

**Authentication:**
- Requires user authentication (to be enforced in production).

**Error Handling:**
- Returns 400 for missing/invalid parameters.
- Returns 404 if notification not found.
