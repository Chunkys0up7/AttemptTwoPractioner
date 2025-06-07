from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse, Response
from prometheus_client import Counter, Histogram, generate_latest
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.sessions import SessionMiddleware
from .api.routers import auth, data, monitoring, template
from .core.config import settings
from .monitoring.performance import performance_monitor
import time

# Request metrics
request_counter = Counter('http_requests_total', 'Total HTTP requests', ['method', 'path', 'status_code'])
request_latency = Histogram('http_request_duration_seconds', 'HTTP request duration', ['method', 'path'])

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    GZipMiddleware,
    minimum_size=1000
)

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=settings.ALLOWED_HOSTS
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY
)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        
        request_counter.labels(
            method=request.method,
            path=request.url.path,
            status_code=response.status_code
        ).inc()
        
        request_latency.labels(
            method=request.method,
            path=request.url.path
        ).observe(duration)
        
        return response

app.add_middleware(RequestLoggingMiddleware)

# Include routers
app.include_router(auth.router, prefix=settings.API_V1_STR)
app.include_router(data.router, prefix=settings.API_V1_STR)
app.include_router(monitoring.router, prefix=settings.API_V1_STR)
app.include_router(template.router, prefix=settings.API_V1_STR)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    performance_monitor.increment_error("unhandled_exception", "main")
    return JSONResponse(
        status_code=500,
        content={"message": "Internal server error"}
    )

@app.get("/")
def root():
    return {
        "message": "Welcome to the MCP API",
        "version": settings.VERSION,
        "docs_url": "/docs",
        "redoc_url": "/redoc",
        "health_url": "/health"
    }

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "uptime": performance_monitor.get_system_metrics()["uptime"]
    }

@app.get("/metrics")
def metrics():
    return Response(
        generate_latest(),
        media_type="text/plain"
    )