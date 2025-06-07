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

#### Response

```json
{
  "data": [
    {
      "id": "uuid-string",
      "metricName": "string",
      "severity": "high" | "medium" | "low",
      "message": "string",
      "timestamp": "2024-03-21T10:00:00Z",
      "acknowledged": boolean,
      "value": number,
      "threshold": number
    }
  ],
  "error": "string"
}
```

### Acknowledge Notification

Marks a notification as acknowledged.

```http
POST /api/notifications/{id}/acknowledge
```

#### Response

```json
{
  "data": {
    "id": "uuid-string",
    "acknowledged": true
  },
  "error": "string"
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

#### Response

```json
{
  "data": {
    "totalAlerts": number,
    "acknowledgedAlerts": number,
    "alertsBySeverity": {
      "high": number,
      "medium": number,
      "low": number
    },
    "averageResponseTime": number,
    "alertsByMetric": {
      "string": number
    }
  },
  "error": "string"
}
```

### Error Responses

The notification system uses the same error response format as other endpoints:

```json
{
  "error": "string",
  "message": "string"
}
```

### Data Types

```typescript
interface Alert {
  id: string;
  metricName: string;
  severity: 'high' | 'medium' | 'low';
  message: string;
  timestamp: Date;
  acknowledged: boolean;
  value?: number;
  threshold?: number;
}

interface NotificationAnalytics {
  totalAlerts: number;
  acknowledgedAlerts: number;
  alertsBySeverity: {
    high: number;
    medium: number;
    low: number;
  };
  averageResponseTime: number;
  alertsByMetric: Record<string, number>;
}
```
