"""
Security monitoring utilities for the MCP Backend.
"""
import logging
from typing import Dict, Any
import prometheus_client
from prometheus_client import Counter, Gauge
from mcp.core.config import settings

logger = logging.getLogger(__name__)

class SecurityMonitor:
    """
    Security monitoring class that tracks security-related metrics and events.
    """
    def __init__(self):
        self._initialized = False
        self._metrics = {}
        
    def start(self):
        """Initialize security monitoring."""
        if self._initialized:
            return
            
        # Create metrics
        self._metrics["login_attempts"] = Counter(
            "mcp_security_login_attempts_total",
            "Total number of login attempts",
            ["status", "source"]
        )
        
        self._metrics["failed_auth"] = Counter(
            "mcp_security_failed_auth_total",
            "Total number of failed authentication attempts",
            ["type", "source"]
        )
        
        self._metrics["rate_limit_hits"] = Counter(
            "mcp_security_rate_limit_hits_total",
            "Total number of rate limit hits",
            ["endpoint", "type"]
        )
        
        self._metrics["active_sessions"] = Gauge(
            "mcp_security_active_sessions",
            "Number of active sessions",
            ["user_type"]
        )
        
        self._initialized = True
        logger.info("Security monitoring initialized")
        
    def stop(self):
        """Stop security monitoring."""
        self._initialized = False
        logger.info("Security monitoring stopped")
        
    def increment_login_attempt(self, success: bool, source: str):
        """
        Track a login attempt.
        
        Args:
            success: Whether the login was successful
            source: Source of the login attempt (e.g., "api", "web")
        """
        if not self._initialized:
            return
            
        status = "success" if success else "failure"
        self._metrics["login_attempts"].labels(
            status=status,
            source=source
        ).inc()
        
    def increment_failed_auth(self, auth_type: str, source: str):
        """
        Track a failed authentication attempt.
        
        Args:
            auth_type: Type of authentication (e.g., "token", "session")
            source: Source of the authentication attempt
        """
        if not self._initialized:
            return
            
        self._metrics["failed_auth"].labels(
            type=auth_type,
            source=source
        ).inc()
        
    def increment_rate_limit(self, endpoint: str, limit_type: str):
        """
        Track a rate limit hit.
        
        Args:
            endpoint: The endpoint that was rate limited
            limit_type: Type of rate limit (e.g., "ip", "user")
        """
        if not self._initialized:
            return
            
        self._metrics["rate_limit_hits"].labels(
            endpoint=endpoint,
            type=limit_type
        ).inc()
        
    def update_active_sessions(self, count: int, user_type: str):
        """
        Update the number of active sessions.
        
        Args:
            count: Number of active sessions
            user_type: Type of user (e.g., "admin", "user")
        """
        if not self._initialized:
            return
            
        self._metrics["active_sessions"].labels(
            user_type=user_type
        ).set(count)

# Global instance
security_monitor = SecurityMonitor()
