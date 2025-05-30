"""
Application Configuration Management.

This module defines the Pydantic-based settings management for the MCP backend.
It loads configuration from environment variables and/or a .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional, List


class Settings(BaseSettings):
    """
    Application settings.

    Attributes:
        APP_NAME: The name of the application.
        DEBUG: Boolean flag for enabling debug mode.
        DATABASE_URL: The connection URL for the primary database.
        REDIS_URL: The connection URL for Redis.
        # Add other environment variables as needed
        # Security settings
        SECRET_KEY: str = "your-secret-key-here"  # Change in production
        ALGORITHM: str = "HS256"
        ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
        REFRESH_TOKEN_EXPIRE_DAYS: int = 7
        SESSION_SECRET_KEY: Optional[str] = None
        SESSION_MAX_AGE: int = 3600  # 1 hour
        RATE_LIMIT_PER_MINUTE: int = 100
        ALLOWED_HOSTS: List[str] = ["*"]  # Restrict in production
        BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Restrict in production
        API_KEY_PREFIX: str = "mcp_"
        API_KEY_LENGTH: int = 32
    """
    APP_NAME: str = "MCP Backend"
    DEBUG: bool = False
    DATABASE_URL: Optional[str] = "postgresql://user:password@localhost/mcpdb"
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    # Add other environment variables as needed
    # Security settings
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    SESSION_SECRET_KEY: Optional[str] = None
    SESSION_MAX_AGE: int = 3600  # 1 hour
    RATE_LIMIT_PER_MINUTE: int = 100
    ALLOWED_HOSTS: List[str] = ["*"]  # Restrict in production
    BACKEND_CORS_ORIGINS: List[str] = ["*"]  # Restrict in production
    API_KEY_PREFIX: str = "mcp_"
    API_KEY_LENGTH: int = 32

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
"""Global instance of application settings."""
