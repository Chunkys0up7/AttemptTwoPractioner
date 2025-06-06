# API Key Management

This document describes the API key management system implemented in the MCP Backend.

## Overview

The API key management system provides a secure way to authenticate API requests. It includes:

1. API key generation and storage
2. Key validation and authentication
3. Key lifecycle management (creation, deactivation)
4. Integration with FastAPI's dependency injection system

## Components

### 1. API Key Model (`APIKey`)

The `APIKey` model stores API key information in the database:

```python
class APIKey(Base):
    __tablename__ = "api_keys"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    key_hash = Column(String, nullable=False, unique=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    is_active = Column(Boolean, default=True)
    created_by = Column(String, nullable=False)
    owner_id = Column(String, nullable=True)
    owner_type = Column(String, nullable=True)
```

### 2. API Key Service (`APIKeyService`)

The service layer provides methods for managing API keys:

```python
class APIKeyService:
    def create_api_key(self, name: str, created_by: str, ...) -> APIKey
    def get_api_key(self, key_id: int) -> Optional[APIKey]
    def list_api_keys(self, owner_id: str = None, ...) -> List[APIKey]
    def deactivate_api_key(self, key_id: int) -> APIKey
    def validate_api_key(self, key: str) -> Optional[APIKey]
```

### 3. API Routes

The API provides endpoints for managing API keys:

- `POST /api/v1/api-keys/`: Create a new API key
- `GET /api/v1/api-keys/`: List API keys (with filtering)
- `GET /api/v1/api-keys/{key_id}`: Get a specific API key
- `DELETE /api/v1/api-keys/{key_id}`: Deactivate an API key

### 4. Authentication

API key authentication is implemented using FastAPI's dependency injection:

```python
async def get_api_key_user(
    api_key: Optional[str] = Depends(api_key_header),
    db: Session = Depends(get_db)
) -> str:
    # Validate API key and return associated user
```

## Security Features

1. **Secure Key Generation**
   - Keys are generated using `secrets.token_bytes()`
   - Keys are prefixed for easy identification
   - Keys are hashed before storage

2. **Key Validation**
   - Keys are validated on each request
   - Expired keys are rejected
   - Inactive keys are rejected
   - Last used timestamp is updated

3. **Key Lifecycle**
   - Keys can be deactivated
   - Keys can have expiration dates
   - Keys are associated with owners

## Usage

### Creating an API Key

```python
# Using the API
response = requests.post(
    "http://api.example.com/api/v1/api-keys/",
    json={
        "name": "My API Key",
        "owner_id": "user123",
        "owner_type": "user",
        "expires_in_days": 30
    },
    headers={"X-User-ID": "user123"}
)

# The response includes the raw API key
api_key = response.json()["key"]
```

### Using an API Key

```python
# Include the API key in the X-API-Key header
response = requests.get(
    "http://api.example.com/api/v1/mcp-definitions/",
    headers={"X-API-Key": api_key}
)
```

## Testing

The API key management system is tested in `tests/api/test_api_key_routes.py`. The test suite includes:

1. `test_create_api_key`: Tests API key creation
2. `test_list_api_keys`: Tests listing and filtering API keys
3. `test_get_api_key`: Tests retrieving a specific API key
4. `test_deactivate_api_key`: Tests deactivating an API key
5. `test_api_key_authentication`: Tests API key authentication

## Future Enhancements

1. **Key Rotation**
   - Implement automatic key rotation
   - Add key versioning
   - Support key migration

2. **Enhanced Security**
   - Add rate limiting per key
   - Implement key scopes/permissions
   - Add IP restrictions

3. **Monitoring**
   - Add usage tracking
   - Implement alerts for suspicious activity
   - Add key usage analytics

4. **Integration**
   - Add OAuth2 support
   - Implement key delegation
   - Add key sharing capabilities 