# Security Enhancements

This document describes the security enhancements implemented in the MCP Backend.

## Overview

The security enhancements provide:

1. Security headers for HTTP responses
2. Rate limiting for API requests
3. CORS configuration
4. Trusted host validation
5. Session management
6. API key authentication
7. JWT token management (placeholder)

## Components

### 1. Security Headers

The `SecurityHeadersMiddleware` adds the following security headers to all responses:

- `X-Content-Type-Options`: Prevents MIME type sniffing
- `X-Frame-Options`: Prevents clickjacking
- `X-XSS-Protection`: Enables XSS filtering
- `Strict-Transport-Security`: Enforces HTTPS
- `Content-Security-Policy`: Controls resource loading
- `Referrer-Policy`: Controls referrer information
- `Permissions-Policy`: Controls browser features

### 2. Rate Limiting

The `RateLimitMiddleware` implements rate limiting:

- Configurable requests per minute
- IP-based rate limiting
- Sliding window implementation
- Automatic cleanup of old requests

### 3. CORS Configuration

CORS is configured through FastAPI's `CORSMiddleware`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 4. Trusted Host Validation

The `TrustedHostMiddleware` validates the `Host` header:

```python
app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)
```

### 5. Session Management

Session management is implemented using `SessionMiddleware`:

```python
app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SESSION_SECRET_KEY,
    session_cookie="mcp_session",
    max_age=settings.SESSION_MAX_AGE,
    same_site="lax",
    https_only=not settings.DEBUG
)
```

### 6. API Key Authentication

API key authentication is implemented through:

1. `APIKey` model for storing keys
2. `APIKeyService` for key management
3. FastAPI dependency for key validation

Example usage:

```python
from fastapi import Depends
from mcp.api.deps import get_api_key_user

@app.get("/protected-endpoint")
async def protected_endpoint(user_id: str = Depends(get_api_key_user)):
    return {"message": f"Hello, {user_id}!"}
```

### 7. JWT Token Management (Placeholder)

JWT token management is prepared for future implementation:

1. `JWTManager` class for token operations
2. Token refresh mechanism
3. Token validation middleware

## Configuration

Security settings are configured in `mcp/core/config.py`:

```python
class Settings(BaseSettings):
    # Security settings
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_SECRET_KEY: Optional[str]
    SESSION_MAX_AGE: int = 3600
    RATE_LIMIT_PER_MINUTE: int = 100
    ALLOWED_HOSTS: List[str]
    BACKEND_CORS_ORIGINS: List[str]
    API_KEY_PREFIX: str = "mcp_"
    API_KEY_LENGTH: int = 32
```

## Testing

Security features are tested in:

1. `tests/core/test_security_middleware.py`:
   - Security headers
   - Rate limiting
   - Middleware setup

2. `tests/api/test_api_key_routes.py`:
   - API key creation
   - API key validation
   - API key authentication

## Best Practices

1. **Configuration**
   - Use environment variables for sensitive settings
   - Restrict CORS origins in production
   - Set appropriate rate limits
   - Use strong secret keys

2. **API Keys**
   - Rotate keys regularly
   - Use key scopes for fine-grained access
   - Monitor key usage
   - Implement key revocation

3. **Headers**
   - Keep security headers up to date
   - Customize CSP for your needs
   - Use appropriate HSTS settings
   - Configure referrer policy

4. **Rate Limiting**
   - Set appropriate limits per endpoint
   - Monitor rate limit hits
   - Implement IP allowlisting
   - Consider user-based limits

## Future Enhancements

1. **Authentication**
   - Implement OAuth2
   - Add social login
   - Support MFA
   - Add password policies

2. **Authorization**
   - Implement RBAC
   - Add resource-level permissions
   - Support user groups
   - Add audit logging

3. **Monitoring**
   - Add security event logging
   - Implement intrusion detection
   - Add anomaly detection
   - Create security dashboards 