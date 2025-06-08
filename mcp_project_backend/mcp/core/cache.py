from functools import wraps
from typing import Callable, Any, Optional, TypeVar, Generic
from datetime import datetime, timedelta
from mcp.core.settings import settings
import redis
import pickle
import logging
from prometheus_client import Counter, Gauge

# Set up logging
logger = logging.getLogger(__name__)

# Prometheus metrics
CACHE_HIT = Counter(
    'cache_hits_total',
    'Total number of cache hits'
)

CACHE_MISS = Counter(
    'cache_misses_total',
    'Total number of cache misses'
)

CACHE_SIZE = Gauge(
    'cache_size_bytes',
    'Current cache size in bytes'
)

# Initialize Redis client with connection pool
redis_pool = redis.ConnectionPool(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    max_connections=settings.REDIS_MAX_CONNECTIONS,
    socket_timeout=settings.REDIS_TIMEOUT
)

redis_client = redis.Redis(connection_pool=redis_pool, decode_responses=True)

# Export cache_manager for external use
cache_manager = redis_client

T = TypeVar('T')

def cache_response(
    timeout: int,
    key_prefix: str = "workflow"
) -> Callable:
    """
    Decorator to cache API responses using Redis.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache keys
    
    Returns:
        Decorated function with caching
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> T:
            try:
                # Generate cache key based on function name and arguments
                cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
                
                # Check cache first
                cached_result = redis_client.get(cache_key)
                if cached_result:
                    CACHE_HIT.inc()
                    return pickle.loads(cached_result)  # Use pickle for security
                
                CACHE_MISS.inc()
                
                # If not cached, execute function
                result = await func(*args, **kwargs)
                
                # Cache the result using pickle for security
                redis_client.setex(
                    cache_key,
                    timeout,
                    pickle.dumps(result)
                )
                
                # Update cache size metric
                cache_size = redis_client.info('memory')['used_memory']
                CACHE_SIZE.set(cache_size)
                
                return result
                
            except redis.exceptions.RedisError as e:
                logger.error(f"Redis error in cache operation: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Cache error: {str(e)}")
                raise
        
        return wrapper
    
    return decorator

def invalidate_cache(key_prefix: str = "workflow") -> None:
    """
    Invalidate all cache entries with the given prefix.
    
    Args:
        key_prefix: Prefix of cache keys to invalidate
    """
    try:
        keys = redis_client.keys(f"{key_prefix}:*")
        if keys:
            redis_client.delete(*keys)
            logger.info(f"Invalidated {len(keys)} cache entries with prefix {key_prefix}")
    except redis.exceptions.RedisError as e:
        logger.error(f"Redis error while invalidating cache: {str(e)}")
        raise

def cache_key_exists(key: str) -> bool:
    """
    Check if a specific cache key exists.
    
    Args:
        key: Cache key to check
    
    Returns:
        bool: True if key exists, False otherwise
    """
    return redis_client.exists(key) > 0

def get_cache_ttl(key: str) -> Optional[int]:
    """
    Get the remaining time-to-live for a cache key.
    
    Args:
        key: Cache key to check
    
    Returns:
        int: Remaining TTL in seconds, or None if key doesn't exist
    """
    ttl = redis_client.ttl(key)
    return ttl if ttl >= 0 else None
