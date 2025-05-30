from mcp.core.security.api_security import setup_cors, setup_rate_limiting

app = FastAPI()

# Setup CORS
setup_cors(app)

# Setup rate limiting (scaffold)
setup_rate_limiting(app)

# Optionally enforce HTTPS on all requests (middleware or dependency)
# from fastapi import Request, Depends
# from mcp.core.security.api_security import enforce_https
# @app.middleware("http")
# async def https_middleware(request: Request, call_next):
#     enforce_https(request)
#     return await call_next(request) 