"""
Learning resource discovery.

Per project requirements, resources are NOT fabricated: every link
returned here comes from a real SerpApi Google Search result for
"learn {skill}" style queries. If SerpApi fails or returns nothing for a
skill, that skill is simply skipped (with a warning) rather than backed
by an invented link.
"""
from typing import List, Tuple
from urllib.parse import urlparse

from app.core.logging_config import get_logger
from app.schemas.roadmap import ResourceItem
from app.services.serpapi_service import SerpApiError, serpapi_service

logger = get_logger(__name__)

MAX_SKILLS_TO_SEARCH = 5  # bound SerpApi calls/cost per roadmap request


def _domain(url: str) -> str:
    try:
        netloc = urlparse(url).netloc
        return netloc.replace("www.", "") if netloc else ""
    except Exception:  # noqa: BLE001
        return ""


async def find_resources(skills: List[str], max_per_skill: int = 2) -> Tuple[List[ResourceItem], List[str]]:
    warnings: List[str] = []
    resources: List[ResourceItem] = []

    for skill in skills[:MAX_SKILLS_TO_SEARCH]:
        query = f"learn {skill} tutorial for beginners"
        try:
            results = await serpapi_service.google_search(query=query, num_results=max_per_skill)
        except SerpApiError as exc:
            logger.warning("SerpApi google_search failed for skill=%s: %s", skill, exc.message)
            warnings.append(f"Could not fetch resources for '{skill}': {exc.message}")
            continue

        if not results:
            warnings.append(f"No resources found for '{skill}'.")
            continue

        for result in results[:max_per_skill]:
            link = result.get("link")
            title = result.get("title")
            if not link or not title:
                continue
            resources.append(
                ResourceItem(skill=skill, title=title, link=link, source=_domain(link))
            )

    return resources, warnings
