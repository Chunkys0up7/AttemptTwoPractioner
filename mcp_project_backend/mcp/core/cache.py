from functools import wraps
from typing import Callable, Any, Optional
from datetime import datetime, timedelta
from mcp.core.config import settings
import redis

# Initialize Redis client
redis_client = redis.Redis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB,
    decode_responses=True
)

def cache_response(
    timeout: int,
    key_prefix: str = "workflow"
) -> Callable:
    """
    Decorator to cache API responses using Redis.
    
    Args:
        timeout: Cache timeout in seconds
        key_prefix: Prefix for cache keys
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Generate cache key based on function name and arguments
            cache_key = f"{key_prefix}:{func.__name__}:{str(args)}:{str(kwargs)}"
            
            # Check cache first
            cached_result = redis_client.get(cache_key)
            if cached_result:
                return eval(cached_result)  # Convert string back to object
                
            # If not cached, execute function
            result = await func(*args, **kwargs)
            
            # Cache the result
            redis_client.setex(
                cache_key,
                timeout,
                str(result)  # Convert object to string for storage
            )
            
            return result
        
        return wrapper
    
    return decorator

def invalidate_cache(key_prefix: str = "workflow") -> None:
    """
    Invalidate all cache entries with the given prefix.
    
    Args:
        key_prefix: Prefix of cache keys to invalidate
    """
    keys = redis_client.keys(f"{key_prefix}:*")
    if keys:
        redis_client.delete(*keys)

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
