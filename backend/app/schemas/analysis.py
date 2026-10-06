"""
Schemas for the standalone /api/analysis/* endpoints (Stage 2).

These let a frontend call skill extraction, market analysis, or skill-gap
scoring independently of the full /api/careers/analyze workflow — e.g. to
extract skills from a single pasted job description, or to re-score a
skill gap after the user edits their skill list without re-hitting SerpApi.
"""
from typing import List, Optional

from pydantic import BaseModel, Field

from app.schemas.career import MarketAnalysis, SkillDemand, SkillGap


class SkillExtractionRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Free text to extract skills from, e.g. a job description.")


class SkillExtractionResponse(BaseModel):
    skills: List[str] = Field(default_factory=list)


class MarketAnalysisRequest(BaseModel):
    """Analyze skill demand across a caller-supplied set of job description texts."""
    job_descriptions: List[str] = Field(..., min_length=1, max_length=200)


class SkillGapRequest(BaseModel):
    user_skills: List[str] = Field(default_factory=list)
    market_skills: List[SkillDemand] = Field(
        ..., description="Market skill-demand data, typically from a prior /api/analysis/market call."
    )


class SkillGapResponse(SkillGap):
    pass


class JobMatchRequest(BaseModel):
    job_detected_skills: List[str] = Field(
        default_factory=list, description="Skills detected in a single job's description (e.g. from /api/analysis/skills)."
    )
    user_skills: List[str] = Field(default_factory=list)


class JobMatchResponse(BaseModel):
    match_percentage: Optional[float] = None
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    match_note: Optional[str] = None
