"""
/api/resources routes.

Standalone resource lookup for a single skill, independent of the
roadmap-generation flow. Backed by real SerpApi Google Search results —
never a static/fabricated resource list.
"""
from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.core.rate_limiter import rate_limit_dependency
from app.schemas.roadmap import ResourceItem
from app.services.resource_service import find_resources

router = APIRouter(prefix="/resources", tags=["resources"], dependencies=[Depends(rate_limit_dependency)])


@router.get("", response_model=list[ResourceItem])
async def get_resources(
    skill: str = Query(..., min_length=1, description="Skill to find learning resources for, e.g. 'Docker'."),
    limit: int = Query(default=5, ge=1, le=10),
):
    """
    Real, current learning resources for a single skill (via SerpApi Google
    Search). Returns an empty list — never fabricated links — if nothing
    is found.
    """
    resources, warnings = await find_resources([skill], max_per_skill=limit)
    if not resources and warnings:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=warnings[0])
    return resources
