from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import asyncio
from mcp.core.config import settings

class RateLimiter:
    def __init__(
        self,
        max_requests: int = 100,
        window_seconds: int = 60,
        max_concurrent: int = 10
    ):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.max_concurrent = max_concurrent
        self.requests: Dict[str, list] = {}
        self._semaphore = asyncio.Semaphore(max_concurrent)

    def _get_window_start(self) -> datetime:
        return datetime.now() - timedelta(seconds=self.window_seconds)

    def _cleanup_old_requests(self, client_id: str) -> None:
        if client_id in self.requests:
            self.requests[client_id] = [
                ts for ts in self.requests[client_id]
                if ts > self._get_window_start()
            ]

    def _add_request(self, client_id: str) -> None:
        if client_id not in self.requests:
            self.requests[client_id] = []
        self.requests[client_id].append(datetime.now())

    def _is_rate_limited(self, client_id: str) -> bool:
        self._cleanup_old_requests(client_id)
        if client_id in self.requests:
            return len(self.requests[client_id]) >= self.max_requests
        return False

    async def __call__(self, client_id: str) -> None:
        async with self._semaphore:
            if self._is_rate_limited(client_id):
                raise RateLimitExceededError(
                    f"Rate limit exceeded for client {client_id}."
                )
            self._add_request(client_id)

class RateLimitExceededError(Exception):
    """Raised when the rate limit is exceeded."""
    pass

# Create rate limiter instances
workflow_rate_limiter = RateLimiter(
    max_requests=settings.WORKFLOW_MAX_REQUESTS,
    window_seconds=settings.WORKFLOW_RATE_WINDOW,
    max_concurrent=settings.WORKFLOW_MAX_CONCURRENT
)

# Create separate rate limiter for workflow steps
workflow_steps_rate_limiter = RateLimiter(
    max_requests=settings.WORKFLOW_STEPS_MAX_REQUESTS,
    window_seconds=settings.WORKFLOW_STEPS_RATE_WINDOW,
    max_concurrent=settings.WORKFLOW_STEPS_MAX_CONCURRENT
)
