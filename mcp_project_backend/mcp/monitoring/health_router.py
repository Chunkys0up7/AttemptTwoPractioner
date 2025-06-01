from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
# from mcp.api.deps import get_db_session  # Uncomment and implement this import in your project
# import redis  # Uncomment if using Redis
# from mcp.core.config import settings  # Uncomment if using settings for Redis URL

router = APIRouter()

@router.get("/health", tags=["health"])
async def health_check(db: Session = Depends(lambda: None)):
    """
    Performs health checks on the application and its dependencies (e.g., database, cache).
    Returns HTTP 200 if healthy, HTTP 503 if unhealthy.
    """
    db_status = "OK"
    redis_status = "OK"  # Placeholder

    # Check Database Connection
    try:
        # Perform a simple query to check DB health
        if db is not None:
            db.execute("SELECT 1")
        else:
            db_status = "Skipped (no DB session dependency)"
    except Exception as e:
        db_status = f"Error: {e}"
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "database": db_status})

    # Check Redis Connection (Example)
    # try:
    #     r = redis.Redis.from_url(settings.REDIS_URL, socket_connect_timeout=1)
    #     r.ping()
    # except Exception as e:
    #     redis_status = f"Error: {e}"
    #     # Decide if Redis being down makes the whole app unhealthy
    #     # raise HTTPException(status_code=503, detail={"status": "unhealthy", "redis": redis_status})

    if db_status == "OK":  # and redis_status == "OK":
        return {"status": "healthy", "database": db_status, "redis": redis_status}
    else:
        # This path might not be reached if DB check already raised 503
        raise HTTPException(status_code=503, detail={"status": "unhealthy", "database": db_status, "redis": redis_status})
