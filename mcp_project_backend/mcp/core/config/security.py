from typing import List, Dict, Any
from pydantic import BaseSettings
from mcp.core.config import settings
import secrets

class SecuritySettings(BaseSettings):
    # JWT Configuration
    JWT_SECRET_KEY: str = secrets.token_urlsafe(32)
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Password Security
    PASSWORD_MIN_LENGTH: int = 8
    PASSWORD_MAX_LENGTH: int = 128
    PASSWORD_REQUIRE_SPECIAL_CHAR: bool = True
    PASSWORD_REQUIRE_NUMBER: bool = True
    PASSWORD_REQUIRE_UPPERCASE: bool = True
    PASSWORD_REQUIRE_LOWERCASE: bool = True

    # Host Validation
    ALLOWED_HOSTS: List[str] = ["localhost", "127.0.0.1"]
    HOST_HEADER_VALIDATION: bool = True
    HOST_HEADER_WHITELIST: List[str] = ["localhost", "127.0.0.1"]

    # Content Security Policy
    CSP_DEFAULT_SRC: List[str] = ["'self'"]
    CSP_SCRIPT_SRC: List[str] = ["'self'", "'unsafe-inline'", "'unsafe-eval'"]
    CSP_STYLE_SRC: List[str] = ["'self'", "'unsafe-inline'"]
    CSP_IMG_SRC: List[str] = ["'self'", "data:"]
    CSP_CONNECT_SRC: List[str] = ["'self'"]
    CSP_FONT_SRC: List[str] = ["'self'"]
    CSP_OBJECT_SRC: List[str] = []
    CSP_MEDIA_SRC: List[str] = []
    CSP_FRAME_SRC: List[str] = []
    CSP_FORM_ACTION: List[str] = ["'self'"]
    CSP_SANDBOX: List[str] = []
    CSP_REPORT_URI: str = ""
    CSP_REPORT_ONLY: bool = False

    # XSS Protection
    XSS_PROTECTION: bool = True
    XSS_PROTECTION_VALUE: str = "1; mode=block"
    XSS_PROTECTION_REPORT_ONLY: bool = False

    # Rate Limiting
    RATE_LIMITING: bool = True
    RATE_LIMIT_WINDOW: int = 60  # seconds
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_BURST: int = 20
    RATE_LIMIT_EXEMPT_ROUTES: List[str] = []
    RATE_LIMIT_STORAGE: str = "redis"

    # Input Sanitization
    INPUT_SANITIZATION: bool = True
    SANITIZE_XSS: bool = True
    SANITIZE_SQL_INJECTION: bool = True
    SANITIZE_CONTENT_TYPES: List[str] = ["text/html", "application/json"]
    SANITIZE_MAX_LENGTH: int = 10000
    SANITIZE_ALLOWED_TAGS: List[str] = []
    SANITIZE_ALLOWED_ATTRIBUTES: List[str] = []
    SANITIZE_ALLOWED_STYLES: List[str] = []

    # CORS
    CORS_ENABLED: bool = True
    CORS_ALLOW_ORIGINS: List[str] = ["http://localhost:3000"]
    CORS_ALLOW_METHODS: List[str] = ["GET", "POST", "PUT", "DELETE", "OPTIONS"]
    CORS_ALLOW_HEADERS: List[str] = ["Authorization", "Content-Type", "X-Requested-With"]
    CORS_ALLOW_CREDENTIALS: bool = True
    CORS_EXPOSE_HEADERS: List[str] = []
    CORS_MAX_AGE: int = 600

    # Security Headers
    SECURITY_HEADERS: Dict[str, str] = {
        "X-Content-Type-Options": "nosniff",
        "X-Frame-Options": "DENY",
        "X-XSS-Protection": "1; mode=block",
        "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
        "Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;",
        "Referrer-Policy": "strict-origin-when-cross-origin",
        "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
        "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
        "Pragma": "no-cache",
        "Expires": "0",
        "X-Permitted-Cross-Domain-Policies": "none",
        "X-Download-Options": "noopen",
        "X-Content-Security-Policy": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;",
        "X-WebKit-CSP": "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:;"
    }

    # Rate Limiter configuration
    RATE_LIMITER_CONFIG: Dict[str, Any] = {
        "max_requests": 100,
        "window_seconds": 60,
        "max_concurrent": 10,
        "storage_uri": "redis://localhost:6379/0",
        "storage_options": {},
        "in_memory": False
    }

    # Circuit Breaker configuration
    CIRCUIT_BREAKER_CONFIG: Dict[str, Any] = {
        "failure_threshold": 5,
        "reset_timeout": 60,
        "max_concurrent": 10,
        "window_size": 60,
        "min_requests": 20,
        "error_threshold_percentage": 50
    }

    # API Key Security
    API_KEY_ENABLED: bool = True
    API_KEY_LENGTH: int = 32
    API_KEY_EXPIRATION_DAYS: int = 30
    API_KEY_MAX_PER_USER: int = 5
    API_KEY_RATE_LIMIT: int = 1000
    API_KEY_RATE_LIMIT_WINDOW: int = 3600

    # Database Security
    DB_ENCRYPTION_ENABLED: bool = True
    DB_ENCRYPTION_KEY: str = secrets.token_urlsafe(32)
    DB_AUDIT_LOGGING_ENABLED: bool = True
    DB_QUERY_LOGGING_ENABLED: bool = True

    # File Upload Security
    MAX_FILE_SIZE: int = 10485760  # 10MB
    ALLOWED_FILE_TYPES: List[str] = [".txt", ".pdf", ".doc", ".docx", ".jpg", ".jpeg", ".png", ".gif"]
    MAX_UPLOADS_PER_USER: int = 10
    UPLOAD_RATE_LIMIT: int = 10
    UPLOAD_RATE_LIMIT_WINDOW: int = 3600

    class Config:
        env_prefix = "SECURITY_"
        case_sensitive = True

# Create security settings instance
security_settings = SecuritySettings()
