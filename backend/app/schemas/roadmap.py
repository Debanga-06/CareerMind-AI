"""
Schemas for POST /api/roadmap/generate.

Takes the skill_gap already computed by /api/careers/analyze (or
/api/analysis/skill-gap) and produces a learning roadmap, project
recommendations, and resources — deliberately kept as a separate,
heavier endpoint so the core /api/careers/analyze call stays fast.
"""
from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.career import SkillGap


class RoadmapGenerateRequest(BaseModel):
    target_career: str = Field(..., min_length=2, max_length=200)
    experience_level: str = Field(..., examples=["Beginner", "Intermediate", "Advanced"])
    skill_gap: SkillGap
    include_resources: bool = True
    max_resources_per_skill: int = Field(default=2, ge=1, le=5)


class RoadmapPhase(BaseModel):
    phase_number: int
    title: str
    duration_weeks: int
    focus_skills: List[str] = Field(default_factory=list)
    description: str


class RoadmapPlan(BaseModel):
    summary: str
    phases: List[RoadmapPhase] = Field(default_factory=list)
    # "rule_based" (always available) or "ai:<provider_name>" when an AI
    # provider successfully enriched the summary.
    generated_by: str = "rule_based"


class ProjectRecommendation(BaseModel):
    title: str
    description: str
    skills_used: List[str] = Field(default_factory=list)
    difficulty: str


class ResourceItem(BaseModel):
    skill: str
    title: str
    link: str
    source: Optional[str] = None


class RoadmapGenerateResponse(BaseModel):
    roadmap: RoadmapPlan
    projects: List[ProjectRecommendation] = Field(default_factory=list)
    resources: List[ResourceItem] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    # Set when the request was authenticated: the roadmap was persisted
    # and can be retrieved later via GET /api/roadmap.
    saved: bool = False
    roadmap_id: Optional[int] = None


class SavedRoadmapResponse(BaseModel):
    id: int
    target_career: str
    experience_level: str
    skill_gap: SkillGap
    roadmap: RoadmapPlan
    projects: List[ProjectRecommendation] = Field(default_factory=list)
    resources: List[ResourceItem] = Field(default_factory=list)
    created_at: datetime
