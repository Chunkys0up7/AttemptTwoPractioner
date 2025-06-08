import pytest
from fastapi.testclient import TestClient
from mcp.api.main import app

client = TestClient(app)

def test_get_recommendations_default():
    resp = client.get("/api/recommendations")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) or "recommendations" in data
    recs = data if isinstance(data, list) else data["recommendations"]
    assert len(recs) > 0

def test_get_recommendations_category():
    resp = client.get("/api/recommendations?category=A")
    assert resp.status_code == 200
    recs = resp.json()
    if isinstance(recs, dict):
        recs = recs["recommendations"]
    assert all(r["category"] == "A" for r in recs)

def test_get_recommendations_top_n():
    resp = client.get("/api/recommendations?top_n=1")
    assert resp.status_code == 200
    recs = resp.json()
    if isinstance(recs, dict):
        recs = recs["recommendations"]
    assert len(recs) == 1 