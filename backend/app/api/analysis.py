"""
/api/analysis routes.

These expose the Stage 2 building blocks (skill extraction, market
analysis, skill-gap scoring) standalone, so a frontend can use them
independently of the full /api/careers/analyze pipeline — e.g. extracting
skills from a single job description the user pastes in, or re-scoring a
skill gap after they edit their skill list client-side.
"""
from fastapi import APIRouter, Depends

from app.core.rate_limiter import rate_limit_dependency
from app.schemas.analysis import (
    JobMatchRequest,
    JobMatchResponse,
    MarketAnalysisRequest,
    SkillExtractionRequest,
    SkillExtractionResponse,
    SkillGapRequest,
    SkillGapResponse,
)
from app.schemas.career import MarketAnalysis, NormalizedJob
from app.services.job_matching_service import calculate_job_match
from app.services.market_analysis_service import compute_market_analysis
from app.services.skill_extraction_service import extract_skills
from app.services.skill_gap_service import compute_skill_gap

router = APIRouter(prefix="/analysis", tags=["analysis"], dependencies=[Depends(rate_limit_dependency)])


@router.post("/skills", response_model=SkillExtractionResponse)
async def analysis_skills(payload: SkillExtractionRequest) -> SkillExtractionResponse:
    """Rule-based skill extraction from a single blob of free text (no LLM call)."""
    return SkillExtractionResponse(skills=extract_skills(payload.text))


@router.post("/market", response_model=MarketAnalysis)
async def analysis_market(payload: MarketAnalysisRequest) -> MarketAnalysis:
    """
    Compute skill demand (frequency + percentage) across a caller-supplied
    set of job description texts. Useful for analyzing job text obtained
    outside of the /api/careers/analyze SerpApi flow (e.g. pasted listings).
    """
    jobs = [
        NormalizedJob(description=text, extracted_skills=extract_skills(text))
        for text in payload.job_descriptions
    ]
    return compute_market_analysis(jobs)


@router.post("/skill-gap", response_model=SkillGapResponse)
async def analysis_skill_gap(payload: SkillGapRequest) -> SkillGapResponse:
    """Transparent skill-gap comparison; see skill_gap_service.py for the documented formula."""
    gap = compute_skill_gap(payload.user_skills, payload.market_skills)
    return SkillGapResponse(**gap.model_dump())


@router.post("/job-match", response_model=JobMatchResponse)
async def analysis_job_match(payload: JobMatchRequest) -> JobMatchResponse:
    """
    Transparent per-job match score; see job_matching_service.py for the
    documented formula. Returns match_percentage=None (with a match_note)
    rather than fabricating a score when the job has no detected skills.
    """
    result = calculate_job_match(payload.job_detected_skills, payload.user_skills)
    return JobMatchResponse(
        match_percentage=result.match_percentage,
        matched_skills=result.matched_skills,
        missing_skills=result.missing_skills,
        match_note=result.match_note,
    )
