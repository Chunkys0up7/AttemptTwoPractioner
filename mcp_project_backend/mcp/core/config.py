"""
Application Configuration Management.

This module defines the Pydantic-based settings management for the MCP backend.
It loads configuration from environment variables and/or a .env file.
"""
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional


class Settings(BaseSettings):
    """
    Application settings.

    Attributes:
        APP_NAME: The name of the application.
        DEBUG: Boolean flag for enabling debug mode.
        DATABASE_URL: The connection URL for the primary database.
        REDIS_URL: The connection URL for Redis.
        # Add other environment variables as needed
    """
    APP_NAME: str = "MCP Backend"
    DEBUG: bool = False
    DATABASE_URL: Optional[str] = "postgresql://user:password@localhost/mcpdb"
    REDIS_URL: Optional[str] = "redis://localhost:6379/0"
    # Add other environment variables as needed

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


settings = Settings()
"""Global instance of application settings."""
