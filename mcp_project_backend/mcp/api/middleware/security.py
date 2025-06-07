from fastapi import Request, Response, HTTPException, status
from typing import Callable, Optional
from mcp.core.config import settings
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SecurityMiddleware:
    def __init__(self, app: Callable):
        self.app = app
        self.allowed_hosts = settings.ALLOWED_HOSTS
        self.csp = settings.CONTENT_SECURITY_POLICY
        self.xss_protection = settings.XSS_PROTECTION
        
    async def __call__(self, request: Request, call_next: Callable) -> Response:
        # Host header validation
        if settings.HOST_HEADER_VALIDATION:
            host = request.headers.get("host")
            if host and host not in self.allowed_hosts:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid host header"
                )

        # XSS protection
        if self.xss_protection:
            xss_header = request.headers.get("X-XSS-Protection")
            if xss_header and xss_header != "1; mode=block":
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid XSS protection header"
                )

        # Content Security Policy
        if self.csp:
            csp_header = request.headers.get("Content-Security-Policy")
            if csp_header and not re.match(self.csp, csp_header):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid Content Security Policy"
                )

        # Rate limiting
        if settings.RATE_LIMITING:
            # Get client IP
            client_ip = request.client.host
            # Check rate limits
            if not await self.check_rate_limit(client_ip):
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="Rate limit exceeded"
                )

        # Input sanitization
        if settings.INPUT_SANITIZATION:
            await self.sanitize_input(request)

        # Call next middleware
        response = await call_next(request)

        # Add security headers
        self.add_security_headers(response)

        return response

    async def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client IP is within rate limits."""
        try:
            # Get rate limiter instance
            rate_limiter = settings.RATE_LIMITER
            
            # Check rate limit
            await rate_limiter(client_ip)
            return True
        except Exception as e:
            logger.warning(f"Rate limit check failed: {str(e)}")
            return False

    async def sanitize_input(self, request: Request) -> None:
        """Sanitize request input."""
        if request.method in ["POST", "PUT", "PATCH"]:
            try:
                # Get request body
                body = await request.body()
                
                # Sanitize body
                sanitized_body = self.sanitize_body(body)
                
                # Replace request body
                request._body = sanitized_body
            except Exception as e:
                logger.warning(f"Input sanitization failed: {str(e)}")

    def sanitize_body(self, body: bytes) -> bytes:
        """Sanitize request body."""
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
        """Sanitize string content."""
        # Remove dangerous characters
        content = content.replace("<script>", "&lt;script&gt;")
        content = content.replace("</script>", "&lt;/script&gt;")
        content = content.replace("javascript:", "javascript:")
        
        return content

    def add_security_headers(self, response: Response) -> None:
        """Add security headers to response."""
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["Content-Security-Policy"] = settings.CONTENT_SECURITY_POLICY
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        response.headers["Permissions-Policy"] = "geolocation=(), microphone=(), camera=()"
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        response.headers["X-Request-ID"] = request.state.request_id
