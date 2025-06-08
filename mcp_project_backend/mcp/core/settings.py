"""
Application settings configuration.
"""
from pydantic_settings import BaseSettings
from pydantic import SecretStr
from typing import Optional


class Settings(BaseSettings):
    """Application settings."""
    
    # Database settings
    DATABASE_URL: str = "sqlite:///./test.db"
    
    # Redis settings
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_DB: int = 0
    REDIS_PASSWORD: Optional[str] = None
    REDIS_MAX_CONNECTIONS: int = 100
    REDIS_TIMEOUT: float = 5.0
    
    # JWT settings
    JWT_SECRET_KEY: SecretStr = SecretStr("your-secret-key-here")
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API settings
    API_V1_STR: str = "/api/v1"
    
    # CORS settings
    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000"]
    
    # Security settings
    SECURITY_PASSWORD_SALT: str = "your-salt-here"
    SECURITY_PASSWORD_HASH: str = "bcrypt"
    
    # Monitoring settings
    MONITORING_ENABLED: bool = True
    
    # Performance monitoring thresholds
    ERROR_RATE_THRESHOLD: float = 0.1  # 10% error rate threshold
    MEMORY_THRESHOLD: float = 90.0  # Memory usage threshold (percent)
    CPU_THRESHOLD: float = 90.0  # CPU usage threshold (percent)
    
    # API settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "MCP Practitioner"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "MCP Practitioner Backend API"
    
    # Security settings
    SECURITY_PASSWORD_SALT: str = "your-salt-here"
    SECURITY_PASSWORD_HASH: str = "bcrypt"
    SECRET_KEY: str = "your-secret-key-here"
    SESSION_SECRET_KEY: str = "your-session-secret-key-here"
    SESSION_MAX_AGE: int = 3600  # 1 hour
    ALLOWED_HOSTS: list[str] = ["localhost", "127.0.0.1"]
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000"]
    RATE_LIMIT_PER_MINUTE: int = 100  # requests per minute
    DEBUG: bool = False
    
    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

# Global settings instance
settings = Settings()
