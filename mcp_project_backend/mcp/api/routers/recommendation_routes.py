from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from mcp.core.recommendation_service import RecommendationService

router = APIRouter()

@router.get('/recommendations', tags=["Recommendations"])
def get_recommendations(
    user_id: str = "demo",
    category: Optional[str] = Query(None, description="Filter by category"),
    top_n: int = Query(3, description="Number of recommendations to return")
):
    """
    Get recommendations for the current user (dummy data for now).
    """
    service = RecommendationService()
    context: Dict[str, Any] = {}
    if category:
        context["category"] = category
    return service.get_recommendations(user_id, context, top_n) 