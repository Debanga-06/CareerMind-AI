"""
Stage 1 tests: FastAPI app health + POST /api/careers/analyze pipeline.

SerpApi calls are mocked with `respx` so tests are fast, free and
deterministic — they never hit the real network or require a real
SERPAPI_API_KEY. This does NOT mean the app uses fake data in production;
it means our automated tests don't spend real API quota.
"""
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


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"


def test_list_supported_careers(client):
    response = client.get("/api/careers")
    assert response.status_code == 200
    assert "careers" in response.json()
    assert len(response.json()["careers"]) > 0


def test_analyze_returns_normalized_jobs(client):
    mock_payload = {
        "jobs_results": [
            {
                "job_id": "abc123",
                "title": "AI Engineer",
                "company_name": "Acme Corp",
                "location": "Bengaluru, India",
                "via": "via LinkedIn",
                "description": "Python and PyTorch required.",
                "detected_extensions": {"posted_at": "2 days ago", "schedule_type": "Full-time"},
                "apply_options": [{"title": "Apply", "link": "https://example.com/apply"}],
            }
        ]
    }

    with respx.mock(assert_all_called=True) as mock:
        mock.get(SERPAPI_URL).mock(return_value=httpx.Response(200, json=mock_payload))

        response = client.post(
            "/api/careers/analyze",
            json={
                "target_career": "AI Engineer",
                "skills": ["Python", "React", "JavaScript", "Git"],
                "experience_level": "Beginner",
                "location": "India",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["career"] == "AI Engineer"
    assert body["market"]["sample_size"] == 1
    assert len(body["jobs"]) == 1
    assert body["jobs"][0]["job_id"] == "abc123"
    assert body["jobs"][0]["title"] == "AI Engineer"
    assert body["jobs"][0]["apply_link"] == "https://example.com/apply"
    assert body["warnings"] == []

    # Stage 2: skills extracted from the job description, market analysis
    # computed, and skill gap scored against the user's stated skills.
    assert "Python" in body["jobs"][0]["detected_skills"]
    assert "PyTorch" in body["jobs"][0]["detected_skills"]

    market_skill_names = {s["skill"] for s in body["market"]["skills"]}
    assert "Python" in market_skill_names
    assert "PyTorch" in market_skill_names

    # User listed Python -> it appears in market data -> "strong".
    assert "Python" in body["skill_gap"]["strong_skills"]
    assert "Git" not in market_skill_names  # sanity: Git wasn't in this job's text
    # PyTorch is market-demanded but the user didn't list it -> a gap.
    assert "PyTorch" in (body["skill_gap"]["missing_skills"] + body["skill_gap"]["develop_skills"])
    assert body["skill_gap"]["scoring_note"] is not None

    # Stage 3: this job's own match score. Description yields Python and
    # PyTorch as detected skills; the user has Python but not PyTorch.
    job = body["jobs"][0]
    assert job["match_percentage"] == 50.0
    assert "Python" in job["matched_skills"]
    assert "PyTorch" in job["missing_skills"]
    assert job["match_note"] is None


def test_analyze_handles_empty_results_without_fabricating_data(client):
    with respx.mock(assert_all_called=True) as mock:
        mock.get(SERPAPI_URL).mock(return_value=httpx.Response(200, json={"jobs_results": []}))

        response = client.post(
            "/api/careers/analyze",
            json={
                "target_career": "Extremely Rare Job Title",
                "skills": ["Python"],
                "experience_level": "Beginner",
            },
        )

    assert response.status_code == 200
    body = response.json()
    assert body["jobs"] == []
    assert body["market"]["sample_size"] == 0
    assert len(body["warnings"]) == 1


def test_analyze_handles_serpapi_error_gracefully(client):
    with respx.mock(assert_all_called=True) as mock:
        mock.get(SERPAPI_URL).mock(
            return_value=httpx.Response(200, json={"error": "Invalid API key."})
        )

        response = client.post(
            "/api/careers/analyze",
            json={
                "target_career": "AI Engineer",
                "skills": [],
                "experience_level": "Beginner",
            },
        )

    # Graceful degradation: still 200, with an explicit warning, no fake jobs.
    assert response.status_code == 200
    body = response.json()
    assert body["jobs"] == []
    assert "SerpApi" in body["warnings"][0]


def test_analyze_rejects_blank_target_career(client):
    response = client.post(
        "/api/careers/analyze",
        json={"target_career": "", "experience_level": "Beginner"},
    )
    assert response.status_code == 422


def test_analyze_rejects_invalid_experience_level(client):
    response = client.post(
        "/api/careers/analyze",
        json={"target_career": "AI Engineer", "experience_level": "Wizard"},
    )
    assert response.status_code == 422


def test_analysis_skills_endpoint(client):
    response = client.post(
        "/api/analysis/skills",
        json={"text": "Looking for Python, Docker, and Machine Learning (ML) experience."},
    )
    assert response.status_code == 200
    skills = response.json()["skills"]
    assert "Python" in skills
    assert "Docker" in skills
    assert "Machine Learning" in skills


def test_analysis_market_endpoint(client):
    response = client.post(
        "/api/analysis/market",
        json={
            "job_descriptions": [
                "Python and Docker required.",
                "Python only.",
            ]
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["sample_size"] == 2
    python_entry = next(s for s in body["skills"] if s["skill"] == "Python")
    assert python_entry["percentage"] == 100.0


def test_analysis_skill_gap_endpoint(client):
    response = client.post(
        "/api/analysis/skill-gap",
        json={
            "user_skills": ["Python"],
            "market_skills": [
                {"skill": "Python", "frequency": 10, "percentage": 100.0},
                {"skill": "Docker", "frequency": 8, "percentage": 80.0},
            ],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["strong_skills"] == ["Python"]
    assert body["missing_skills"] == ["Docker"]


def test_analysis_job_match_endpoint(client):
    response = client.post(
        "/api/analysis/job-match",
        json={
            "job_detected_skills": ["Python", "Git", "PyTorch", "Docker"],
            "user_skills": ["Python", "Git"],
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["match_percentage"] == 50.0
    assert body["matched_skills"] == ["Python", "Git"]
    assert body["missing_skills"] == ["PyTorch", "Docker"]
    assert body["match_note"] is None


def test_analysis_job_match_endpoint_no_detected_skills(client):
    response = client.post(
        "/api/analysis/job-match",
        json={"job_detected_skills": [], "user_skills": ["Python"]},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["match_percentage"] is None
    assert body["match_note"] is not None
