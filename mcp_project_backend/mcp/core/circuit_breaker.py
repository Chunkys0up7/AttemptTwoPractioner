from typing import Callable, Any, TypeVar, Generic, Type, Optional
from datetime import datetime, timedelta
import asyncio
from mcp.core.config import settings
import logging
from prometheus_client import Counter, Gauge, Histogram

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics
CIRCUIT_BREAKER_FAILURES = Counter(
    'circuit_breaker_failures_total',
    'Total number of circuit breaker failures'
)

CIRCUIT_BREAKER_OPEN = Gauge(
    'circuit_breaker_open',
    'Circuit breaker open state (1=open, 0=closed)'
)

CIRCUIT_BREAKER_LATENCY = Histogram(
    'circuit_breaker_latency_seconds',
    'Circuit breaker operation latency'
)

T = TypeVar('T')

class CircuitBreaker(Generic[T]):
    """
    Circuit breaker implementation to protect against service failures.
    
    Args:
        failure_threshold: Number of failures before opening
        reset_timeout: Time to wait before reset
        max_concurrent: Maximum concurrent operations
        name: Name for metrics and logging
    """
    def __init__(
        self,
        failure_threshold: int = 5,
        reset_timeout: int = 60,  # seconds
        max_concurrent: int = 10,
        name: str = "default"
    ):
        self.failure_threshold = failure_threshold
        self.reset_timeout = reset_timeout
        self.max_concurrent = max_concurrent
        self.failures = 0
        self.last_failure: Optional[datetime] = None
        self.is_open = False
        self._semaphore = asyncio.Semaphore(max_concurrent)
        self.name = name
        
        # Initialize metrics
        self._latency = CIRCUIT_BREAKER_LATENCY.labels(name=self.name)
        self._open_gauge = CIRCUIT_BREAKER_OPEN.labels(name=self.name)

    async def __call__(self, func: Callable[..., T], *args: Any, **kwargs: Any) -> T:
        start_time = datetime.now()
        
        if self.is_open:
            CIRCUIT_BREAKER_OPEN.labels(name=self.name).set(1)
            raise CircuitBreakerOpenError(
                f"Circuit breaker {self.name} is open - too many failures"
            )

        async with self._semaphore:
            try:
                result = await func(*args, **kwargs)
                self._reset_state()
                self._record_latency(start_time)
                return result
            except Exception as e:
                self._record_failure()
                self._record_latency(start_time)
                raise

    def _reset_state(self) -> None:
        """Reset circuit breaker state."""
        self.failures = 0
        self.last_failure = None
        self.is_open = False
        CIRCUIT_BREAKER_OPEN.labels(name=self.name).set(0)
        logger.info(f"Circuit breaker {self.name} reset to closed state")

    def _record_failure(self) -> None:
        """Record a failure and update state."""
        self.failures += 1
        self.last_failure = datetime.now()
        CIRCUIT_BREAKER_FAILURES.labels(name=self.name).inc()
        logger.warning(f"Circuit breaker {self.name} failure recorded (total: {self.failures})")
        
        if self.failures >= self.failure_threshold:
            self.is_open = True
            self._schedule_reset()
            logger.error(f"Circuit breaker {self.name} opened due to {self.failure_threshold} failures")

    async def _schedule_reset(self) -> None:
        """Schedule circuit breaker reset after timeout."""
        await asyncio.sleep(self.reset_timeout)
        self._reset_state()
        logger.info(f"Circuit breaker {self.name} reset after timeout")

    def _record_latency(self, start_time: datetime) -> None:
        """Record operation latency."""
        duration = (datetime.now() - start_time).total_seconds()
        self._latency.observe(duration)

    def is_circuit_open(self) -> bool:
        """Check if circuit is currently open."""
        return self.is_open

    def get_failure_count(self) -> int:
        """Get current failure count."""
        return self.failures

class CircuitBreakerOpenError(Exception):
    """Raised when the circuit breaker is open."""
    pass

# Create a circuit breaker instance for workflow operations
workflow_circuit_breaker = CircuitBreaker(
    failure_threshold=settings.WORKFLOW_FAILURE_THRESHOLD,
    reset_timeout=settings.WORKFLOW_RESET_TIMEOUT,
    max_concurrent=settings.WORKFLOW_MAX_CONCURRENT,
    name="workflow"
)
