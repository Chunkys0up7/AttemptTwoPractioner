import pytest
from mcp.core.recommendation_service import RecommendationService

def test_get_recommendations_top_n(monkeypatch):
    service = RecommendationService()
    recs = service.get_recommendations(user_id="test", top_n=2)
    assert len(recs) == 2
    assert recs[0]["score"] >= recs[1]["score"]

def test_get_recommendations_filter_category():
    service = RecommendationService()
    recs = service.get_recommendations(user_id="test", context={"category": "A"}, top_n=5)
    assert all(r["category"] == "A" for r in recs)
    assert len(recs) > 0

def test_analytics_logging(capsys):
    service = RecommendationService()
    service.get_recommendations(user_id="test", context={"category": "B"})
    captured = capsys.readouterr()
    assert "[Analytics] get_recommendations called for user_id=test" in captured.out 