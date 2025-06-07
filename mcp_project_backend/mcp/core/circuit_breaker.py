from typing import Callable, Any, TypeVar, Generic, Type
from datetime import datetime, timedelta
import asyncio
from mcp.core.config import settings

T = TypeVar('T')

class CircuitBreaker(Generic[T]):
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,  # seconds
        max_concurrent: int = 10
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.max_concurrent = max_concurrent
        self.failures = 0
        self.last_failure: Optional[datetime] = None
        self.is_open = False
        self._semaphore = asyncio.Semaphore(max_concurrent)

    async def __call__(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        if self.is_open:
            raise CircuitBreakerOpenError(
                "Circuit breaker is open - too many failures"
            )

        async with self._semaphore:
            try:
                result = await func(*args, **kwargs)
                self._reset_state()
                return result
            except Exception as e:
                self._record_failure()
                raise

    def _reset_state(self) -> None:
        self.failures = 0
        self.last_failure = None
        self.is_open = False

    def _record_failure(self) -> None:
        self.failures += 1
        self.last_failure = datetime.now()
        
        if self.failures >= self.failure_threshold:
            self.is_open = True
            self._schedule_reset()

    async def _schedule_reset(self) -> None:
        await asyncio.sleep(self.reset_timeout)
        self._reset_state()

class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open."""
    pass

# Create a circuit breaker instance for workflow operations
workflow_circuit_breaker = CircuitBreaker(
    failure_threshold=settings.WORKFLOW_FAILURE_THRESHOLD,
    reset_timeout=settings.WORKFLOW_RESET_TIMEOUT,
    max_concurrent=settings.WORKFLOW_MAX_CONCURRENT
)
