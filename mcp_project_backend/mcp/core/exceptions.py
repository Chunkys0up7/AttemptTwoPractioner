"""
Custom exceptions for MCP application
"""

class MCPException(Exception):
    """Base exception class for MCP application"""
    def __init__(self, message: str, status_code: int = 500):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

    def to_dict(self):
        return {
            "error": self.message,
            "status_code": self.status_code
        }

class WorkflowDefinitionError(MCPException):
    """Raised when there's an error with workflow definitions"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class WorkflowStepError(MCPException):
    """Raised when there's an error with workflow steps"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class ComponentError(MCPException):
    """Raised when there's an error with components"""
    def __init__(self, message: str):
        super().__init__(message, status_code=400)

class ValidationError(MCPException):
    """Raised when there's a validation error"""
    def __init__(self, message: str):
        super().__init__(message, status_code=422)

class AuthenticationError(MCPException):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message, status_code=401)

class AuthorizationError(MCPException):
    """Raised when authorization fails"""
    def __init__(self, message: str = "Not authorized"):
        super().__init__(message, status_code=403)

class NotFoundError(MCPException):
    """Raised when a resource is not found"""
    def __init__(self, message: str):
        super().__init__(message, status_code=404)

class ConflictError(MCPException):
    """Raised when there's a conflict"""
    def __init__(self, message: str):
        super().__init__(message, status_code=409)

class RateLimitError(MCPException):
    """Raised when rate limit is exceeded"""
    def __init__(self, message: str):
        super().__init__(message, status_code=429)

class InternalServerError(MCPException):
    """Raised when there's an internal server error"""
    def __init__(self, message: str):
        super().__init__(message, status_code=500)

class ServiceUnavailableError(MCPException):
    """Raised when service is unavailable"""
    def __init__(self, message: str):
        super().__init__(message, status_code=503)
