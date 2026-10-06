import httpx
import pytest
import respx

from app.services.cache_service import cache_clear
from app.services.resource_service import find_resources

SERPAPI_URL = "https://serpapi.com/search"


@pytest.fixture(autouse=True)
def _clear_cache():
    cache_clear()
    yield
    cache_clear()


@pytest.mark.asyncio
async def test_find_resources_returns_real_links():
    mock_payload = {
        "organic_results": [
            {"title": "Docker Official Docs", "link": "https://docs.docker.com/get-started/"},
            {"title": "Docker Crash Course", "link": "https://www.youtube.com/watch?v=xyz"},
        ]
    }
    with respx.mock(assert_all_called=True) as mock:
        mock.get(SERPAPI_URL).mock(return_value=httpx.Response(200, json=mock_payload))
        resources, warnings = await find_resources(["Docker"], max_per_skill=2)

    assert len(resources) == 2
    assert resources[0].skill == "Docker"
    assert resources[0].source == "docs.docker.com"
    assert warnings == []


@pytest.mark.asyncio
async def test_find_resources_handles_no_results():
    with respx.mock(assert_all_called=True) as mock:
        mock.get(SERPAPI_URL).mock(return_value=httpx.Response(200, json={"organic_results": []}))
        resources, warnings = await find_resources(["ObscureSkillXYZ"], max_per_skill=2)

    assert resources == []
    assert len(warnings) == 1


@pytest.mark.asyncio
async def test_find_resources_handles_serpapi_error_gracefully():
    with respx.mock(assert_all_called=True) as mock:
        mock.get(SERPAPI_URL).mock(return_value=httpx.Response(200, json={"error": "quota exceeded"}))
        resources, warnings = await find_resources(["Docker"], max_per_skill=2)

    assert resources == []
    assert len(warnings) == 1
    assert "Docker" in warnings[0]


@pytest.mark.asyncio
async def test_find_resources_caps_number_of_skills_searched():
    mock_payload = {"organic_results": [{"title": "T", "link": "https://example.com"}]}
    skills = [f"Skill{i}" for i in range(10)]
    with respx.mock(assert_all_called=False) as mock:
        route = mock.get(SERPAPI_URL).mock(return_value=httpx.Response(200, json=mock_payload))
        await find_resources(skills, max_per_skill=1)

    # MAX_SKILLS_TO_SEARCH=5, so only 5 calls should have been made.
    assert route.call_count == 5
