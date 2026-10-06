"""
Pydantic schemas for the /api/careers/analyze workflow (Stage 1).

Stage 1 focuses on proving the real SerpApi -> normalized jobs pipeline
works end-to-end. Market analysis, skill-gap, roadmap, projects and
resources are represented here but filled in during later stages.
"""
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


class CareerAnalyzeRequest(BaseModel):
    target_career: str = Field(..., min_length=2, max_length=200, examples=["AI Engineer"])
    skills: List[str] = Field(default_factory=list, max_length=100)
    experience_level: str = Field(..., examples=["Beginner", "Intermediate", "Advanced"])
    location: Optional[str] = Field(default=None, max_length=200, examples=["India"])
    num_jobs: int = Field(default=25, ge=1, le=100)

    @field_validator("target_career")
    @classmethod
    def target_career_not_blank(cls, v: str) -> str:
        v = v.strip()
        if not v:
            raise ValueError("target_career must not be blank")
        return v

    @field_validator("skills")
    @classmethod
    def clean_skills(cls, v: List[str]) -> List[str]:
        return [s.strip() for s in v if s and s.strip()]

    @field_validator("experience_level")
    @classmethod
    def normalize_experience_level(cls, v: str) -> str:
        allowed = {"beginner", "intermediate", "advanced", "expert"}
        cleaned = v.strip()
        if cleaned.lower() not in allowed:
            raise ValueError(f"experience_level must be one of {sorted(allowed)}")
        return cleaned


class NormalizedJob(BaseModel):
    job_id: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    description: Optional[str] = None
    via: Optional[str] = None
    posted_at: Optional[str] = None
    schedule_type: Optional[str] = None
    apply_link: Optional[str] = None
    extracted_skills: List[str] = Field(default_factory=list)


class SkillDemand(BaseModel):
    skill: str
    frequency: int
    percentage: float


class MarketAnalysis(BaseModel):
    sample_size: int = 0
    skills: List[SkillDemand] = Field(default_factory=list)


class SkillGap(BaseModel):
    strong_skills: List[str] = Field(default_factory=list)
    develop_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    priority_skills: List[str] = Field(default_factory=list)
    scoring_note: Optional[str] = None


class JobMatch(BaseModel):
    job_id: Optional[str] = None
    title: Optional[str] = None
    company_name: Optional[str] = None
    location: Optional[str] = None
    via: Optional[str] = None
    posted_at: Optional[str] = None
    apply_link: Optional[str] = None
    # Skills detected in THIS job's description/highlights (Stage 2).
    detected_skills: List[str] = Field(default_factory=list)
    # Job matching (Stage 3). match_percentage is None (with match_note
    # explaining why) when the job had no detected skills to score against,
    # rather than fabricating a percentage.
    match_percentage: Optional[float] = None
    matched_skills: List[str] = Field(default_factory=list)
    missing_skills: List[str] = Field(default_factory=list)
    match_note: Optional[str] = None


class CareerAnalyzeResponse(BaseModel):
    career: str
    market: MarketAnalysis
    skill_gap: SkillGap
    jobs: List[JobMatch] = Field(default_factory=list)
    roadmap: Optional[dict] = None
    projects: List[dict] = Field(default_factory=list)
    resources: List[dict] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
