from fastapi import APIRouter, Depends
from mcp.core.recommendation_service import RecommendationService

router = APIRouter()

@router.get('/recommendations', tags=["Recommendations"])
def get_recommendations(user_id: str = "demo"):
    """
    Get recommendations for the current user (dummy data for now).
    """
    service = RecommendationService()
    # TODO: Use real user_id from auth context
    return {"recommendations": service.get_recommendations(user_id)} 