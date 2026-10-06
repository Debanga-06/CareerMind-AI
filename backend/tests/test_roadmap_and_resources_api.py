import httpx
import pytest
import respx
from fastapi.testclient import TestClient

from app.main import app
from app.services.cache_service import cache_clear

SERPAPI_URL = "https://serpapi.com/search"


@pytest.fixture(autouse=True)
def _clear_cache():
    cache_clear()
    yield
    cache_clear()


@pytest.fixture
def client():
    return TestClient(app)


def _skill_gap_payload():
    return {
        "strong_skills": ["Python"],
        "develop_skills": ["SQL"],
        "missing_skills": ["Docker", "Machine Learning"],
        "priority_skills": ["Docker", "Machine Learning"],
        "scoring_note": "note",
    }


def test_roadmap_generate_without_resources(client):
    response = client.post(
        "/api/roadmap/generate",
        json={
            "target_career": "AI Engineer",
            "experience_level": "Beginner",
            "skill_gap": _skill_gap_payload(),
            "include_resources": False,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["roadmap"]["generated_by"] == "rule_based"
    assert len(body["roadmap"]["phases"]) >= 2
    assert len(body["projects"]) > 0
    assert body["resources"] == []


def test_roadmap_generate_with_resources(client):
    mock_payload = {"organic_results": [{"title": "Docker Docs", "link": "https://docs.docker.com"}]}
    with respx.mock(assert_all_called=False) as mock:
        mock.get(SERPAPI_URL).mock(return_value=httpx.Response(200, json=mock_payload))
        response = client.post(
            "/api/roadmap/generate",
            json={
                "target_career": "AI Engineer",
                "experience_level": "Beginner",
                "skill_gap": _skill_gap_payload(),
                "include_resources": True,
                "max_resources_per_skill": 1,
            },
        )
    assert response.status_code == 200
    body = response.json()
    assert len(body["resources"]) > 0
    assert body["resources"][0]["link"] == "https://docs.docker.com"


def test_get_saved_roadmap_requires_auth(client):
    response = client.get("/api/roadmap")
    assert response.status_code == 401


def test_resources_endpoint_returns_real_links(client):
    mock_payload = {
        "organic_results": [{"title": "Learn Python", "link": "https://docs.python.org/3/tutorial/"}]
    }
    with respx.mock(assert_all_called=True) as mock:
        mock.get(SERPAPI_URL).mock(return_value=httpx.Response(200, json=mock_payload))
        response = client.get("/api/resources", params={"skill": "Python", "limit": 1})
    assert response.status_code == 200
    body = response.json()
    assert len(body) == 1
    assert body[0]["skill"] == "Python"
    assert body[0]["link"] == "https://docs.python.org/3/tutorial/"


def test_resources_endpoint_requires_skill_param(client):
    response = client.get("/api/resources")
    assert response.status_code == 422
