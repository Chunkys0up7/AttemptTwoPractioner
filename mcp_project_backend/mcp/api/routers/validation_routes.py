from fastapi import APIRouter
from mcp.api.services.code_validation_service import router as code_validation_router

router = APIRouter(prefix="/validation", tags=["Validation"])

# Include all code validation endpoints
router.include_router(code_validation_router)

@router.post("/report-error")
def report_validation_error():
    # TODO: Implement error reporting for validation failures
    return {"message": "Validation error reporting not yet implemented"}

@router.get("/results-cache/{code_hash}")
def get_cached_validation_results(code_hash: str):
    # TODO: Implement results caching for validation results
    return {"message": f"Results cache for {code_hash} not yet implemented"} 