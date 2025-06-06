from fastapi import APIRouter
from mcp.api.services.code_formatting_service import router as code_formatting_router

router = APIRouter(prefix="/formatting", tags=["Formatting"])

# Include all code formatting endpoints
router.include_router(code_formatting_router) 