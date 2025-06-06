from fastapi import APIRouter
from mcp.api.services.code_validation_service import router as code_validation_router

router = APIRouter(prefix="/validation", tags=["Validation"])

# Include all code validation endpoints
router.include_router(code_validation_router) 