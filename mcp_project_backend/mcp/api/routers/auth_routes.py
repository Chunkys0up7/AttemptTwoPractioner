from fastapi import APIRouter, Depends
from mcp.api.services.auth_service import router as auth_service_router

router = APIRouter()
router.include_router(auth_service_router, prefix="/auth", tags=["auth"])
