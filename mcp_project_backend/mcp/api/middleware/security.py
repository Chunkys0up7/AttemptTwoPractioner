from fastapi import Request, Response, HTTPException, status
from typing import Callable, Optional, Dict, Any
from mcp.core.config import settings
import re
import logging
from datetime import datetime
from urllib.parse import urlparse
from mcp.core.monitoring import monitor

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    """
    Security middleware for protecting the application.
    
    Provides:
    - Host header validation
    - XSS protection
    - Content Security Policy enforcement
    - Rate limiting
    - Input sanitization
    - Security headers
    """
    
    def __init__(self, app: Callable):
        """Initialize security middleware."""
        self.app = app
        self.allowed_hosts = settings.ALLOWED_HOSTS
        self.csp = settings.CONTENT_SECURITY_POLICY
        self.xss_protection = settings.XSS_PROTECTION
        self.rate_limit_window = settings.RATE_LIMIT_WINDOW
        self.rate_limit_count = settings.RATE_LIMIT_COUNT
        self.ip_blacklist = settings.IP_BLACKLIST or []
        self.ip_whitelist = settings.IP_WHITELIST or []
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        """
        Process incoming request and apply security measures.
        
        Args:
            request: Incoming HTTP request
            call_next: Next middleware to call
            
        Returns:
            Response with security headers
            
        Raises:
            HTTPException: If security checks fail
        """
        try:
            # IP blacklist check
            if self.ip_blacklist:
                client_ip = request.client.host
                if client_ip in self.ip_blacklist:
                    logger.warning(f"Blocked request from blacklisted IP: {client_ip}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied"
                    )
            
            # IP whitelist check
            if self.ip_whitelist:
                client_ip = request.client.host
                if client_ip not in self.ip_whitelist:
                    logger.warning(f"Blocked request from non-whitelisted IP: {client_ip}")
                    raise HTTPException(
                        status_code=status.HTTP_403_FORBIDDEN,
                        detail="Access denied"
                    )
            
            # Host header validation
            if settings.HOST_HEADER_VALIDATION:
                host = request.headers.get("host")
                if host and host not in self.allowed_hosts:
                    logger.warning(f"Invalid host header: {host}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid host header"
                    )

            # XSS protection
            if self.xss_protection:
                xss_header = request.headers.get("X-XSS-Protection")
                if xss_header and xss_header != "1; mode=block":
                    logger.warning(f"Invalid XSS protection header: {xss_header}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid XSS protection header"
                    )

            # Content Security Policy
            if self.csp:
                csp_header = request.headers.get("Content-Security-Policy")
                if csp_header and not re.match(self.csp, csp_header):
                    logger.warning(f"Invalid CSP header: {csp_header}")
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Content Security Policy"
                    )

            # Rate limiting
            if settings.RATE_LIMITING:
                client_ip = request.client.host
                if not await self.check_rate_limit(client_ip, request.url.path):
                    logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                    raise HTTPException(
                        status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                        detail="Rate limit exceeded"
                    )

            # Input sanitization
            if settings.INPUT_SANITIZATION:
                await self.sanitize_input(request)

            # Security metrics
            monitor.increment_event('security_request_processed')
            
            # Call next middleware
            response = await call_next(request)

            # Add security headers
            self.add_security_headers(response)

            return response
            
        except HTTPException as e:
            logger.error(f"Security middleware error: {str(e)}")
            monitor.increment_event('security_error', {'type': 'http'})
            raise
        except Exception as e:
            logger.error(f"Unexpected security middleware error: {str(e)}")
            monitor.increment_event('security_error', {'type': 'unexpected'})
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Internal server error"
            )

    async def check_rate_limit(self, client_ip: str, path: str) -> bool:
        """
        Check if client IP is within rate limits.
        
        Args:
            client_ip: Client IP address
            path: Request path
            
        Returns:
            bool: True if within limits, False otherwise
        """
        try:
            # Get rate limiter instance
            rate_limiter = settings.RATE_LIMITER
            
            # Check rate limit with path context
            await rate_limiter(client_ip, path)
            
            # Update metrics
            monitor.increment_event('rate_limit_check', {'result': 'success'})
            return True
            
        except Exception as e:
            logger.warning(f"Rate limit check failed: {str(e)}")
            monitor.increment_event('rate_limit_check', {'result': 'error'})
            return False

    async def sanitize_input(self, request: Request) -> None:
        """
        Sanitize request input.
        
        Args:
            request: Incoming HTTP request
        """
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                # Get request body
                body = await request.body()
                
                # Sanitize body
                sanitized_body = self.sanitize_body(body)
                
                # Replace request body
                request._body = sanitized_body
                
                # Update metrics
                monitor.increment_event('input_sanitized')
                
        except Exception as e:
            logger.warning(f"Input sanitization failed: {str(e)}")
            monitor.increment_event('input_sanitization_error')

    def sanitize_body(self, body: bytes) -> bytes:
        """
        Sanitize request body.
        
        Args:
            body: Raw request body
            
        Returns:
            bytes: Sanitized body
        """
        try:
            # Decode body
            content = body.decode()
            
            # Sanitize content
            sanitized = self.sanitize_content(content)
            
            # Encode back
            return sanitized.encode()
            
        except Exception as e:
            logger.warning(f"Body sanitization failed: {str(e)}")
            return body

    def sanitize_content(self, content: str) -> str:
        """
        Sanitize string content.
        
        Args:
            content: Input content
            
        Returns:
            str: Sanitized content
        """
        # Remove dangerous characters
        content = content.replace("<script>", "&lt;script&gt;")
        content = content.replace("</script>", "&lt;/script&gt;")
        content = content.replace("javascript:", "javascript:")
        
        # Remove SQL injection patterns
        content = re.sub(r'\b(union|select|from|where|insert|update|delete)\b', '', content, flags=re.IGNORECASE)
        
        # Remove command injection patterns
        content = re.sub(r'\b(echo|cat|rm|ls|cd)\b', '', content, flags=re.IGNORECASE)
        
        return content

    def add_security_headers(self, response: Response) -> None:
        """
        Add security headers to response.
        
        Args:
            response: HTTP response
        """
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": settings.CONTENT_SECURITY_POLICY,
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Request-ID": request.state.request_id,
            "X-Content-Security": "active",
            "X-Permitted-Cross-Domain-Policies": "none",
            "X-Download-Options": "noopen",
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains; preload",
            "Content-Security-Policy": settings.CONTENT_SECURITY_POLICY,
            "Referrer-Policy": "strict-origin-when-cross-origin",
            "Permissions-Policy": "geolocation=(), microphone=(), camera=()",
            "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
            "Pragma": "no-cache",
            "Expires": "0",
            "X-Request-ID": request.state.request_id
        }
        
        # Add headers
        for key, value in security_headers.items():
            response.headers[key] = value
            
        # Update metrics
        monitor.increment_event('security_headers_added')
