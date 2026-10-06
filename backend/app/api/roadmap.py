"""
/api/roadmap routes.

POST /api/roadmap/generate is deliberately separate from
POST /api/careers/analyze (which stays fast/SerpApi-jobs-only): this
endpoint does the heavier work of building a learning roadmap, project
recommendations, and (optionally) real resource links.

Auth is OPTIONAL on /generate: anonymous callers still get a full roadmap
back (nothing is gated behind login), but if the caller is authenticated
the result is also persisted so GET /api/roadmap can return it later.
"""
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.rate_limiter import rate_limit_dependency
from app.core.security import get_current_user, get_current_user_optional
from app.database.session import get_db
from app.models.saved_roadmap import SavedRoadmap
from app.models.user import User
from app.schemas.roadmap import (
    RoadmapGenerateRequest,
    RoadmapGenerateResponse,
    SavedRoadmapResponse,
)
from app.services.ai_service import get_ai_provider
from app.services.project_service import recommend_projects
from app.services.resource_service import find_resources
from app.services.roadmap_service import generate_roadmap

router = APIRouter(prefix="/roadmap", tags=["roadmap"], dependencies=[Depends(rate_limit_dependency)])


@router.post("/generate", response_model=RoadmapGenerateResponse)
async def roadmap_generate(
    payload: RoadmapGenerateRequest,
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> RoadmapGenerateResponse:
    warnings: List[str] = []

    ai_provider = get_ai_provider()
    roadmap, roadmap_warnings = await generate_roadmap(
        target_career=payload.target_career,
        experience_level=payload.experience_level,
        skill_gap=payload.skill_gap,
        ai_provider=ai_provider,
    )
    warnings.extend(roadmap_warnings)

    projects = recommend_projects(payload.skill_gap, payload.experience_level)

    resources = []
    if payload.include_resources:
        target_skills = payload.skill_gap.priority_skills or payload.skill_gap.develop_skills
        resources, resource_warnings = await find_resources(
            target_skills, max_per_skill=payload.max_resources_per_skill
        )
        warnings.extend(resource_warnings)

    saved = False
    roadmap_id = None
    if current_user is not None:
        record = SavedRoadmap(
            user_id=current_user.id,
            target_career=payload.target_career,
            experience_level=payload.experience_level,
            skill_gap=payload.skill_gap.model_dump(),
            roadmap=roadmap.model_dump(),
            projects=[p.model_dump() for p in projects],
            resources=[r.model_dump() for r in resources],
        )
        db.add(record)
        db.commit()
        db.refresh(record)
        saved = True
        roadmap_id = record.id

    return RoadmapGenerateResponse(
        roadmap=roadmap,
        projects=projects,
        resources=resources,
        warnings=warnings,
        saved=saved,
        roadmap_id=roadmap_id,
    )


@router.get("", response_model=SavedRoadmapResponse)
async def get_saved_roadmap(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> SavedRoadmapResponse:
    """Returns the current user's most recently generated (and saved) roadmap."""
    record = (
        db.query(SavedRoadmap)
        .filter(SavedRoadmap.user_id == current_user.id)
        .order_by(SavedRoadmap.created_at.desc())
        .first()
    )
    if record is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(
                "No saved roadmap found for this account yet. "
                "Call POST /api/roadmap/generate while authenticated to create one."
            ),
        )

    return SavedRoadmapResponse(
        id=record.id,
        target_career=record.target_career,
        experience_level=record.experience_level,
        skill_gap=record.skill_gap,
        roadmap=record.roadmap,
        projects=record.projects,
        resources=record.resources,
        created_at=record.created_at,
    )
