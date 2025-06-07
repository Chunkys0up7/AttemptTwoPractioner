"""
MCP (Microservice Control Platform) package initialization.

This module initializes the core components of the MCP system.
"""
__version__ = "0.1.0"

from .core.config import settings
from .core.monitoring import monitor
from .api.middleware.security import SecurityMiddleware

__all__ = [
    "settings",
    "monitor",
    "SecurityMiddleware"
]