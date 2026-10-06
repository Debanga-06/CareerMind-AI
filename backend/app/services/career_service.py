"""
Career analysis orchestration.

Stage 1 scope (done): Google Jobs search -> normalize -> return jobs.
Stage 2 scope (this file, updated): extract skills from each job's
description, compute market skill demand across the sample, and compute
a transparent skill-gap comparison against the user's stated skills.

Nothing here fabricates job data or skill data: if SerpApi returns zero
results, or a job has no description text to extract skills from, that is
reflected honestly (empty lists / warnings) rather than invented.
"""
from __future__ import annotations

from typing import List

from app.core.logging_config import get_logger
from app.schemas.career import (
    CareerAnalyzeRequest,
    CareerAnalyzeResponse,
    JobMatch,
    NormalizedJob,
)
from app.services.job_matching_service import calculate_job_match
from app.services.job_normalization_service import normalize_google_jobs_results
from app.services.market_analysis_service import compute_market_analysis
from app.services.serpapi_service import SerpApiError, serpapi_service
from app.services.skill_extraction_service import extract_skills
from app.services.skill_gap_service import compute_skill_gap

logger = get_logger(__name__)


def _build_jobs_query(request: CareerAnalyzeRequest) -> str:
    level = request.experience_level.strip().lower()
    prefix = "entry level " if level == "beginner" else ""
    return f"{prefix}{request.target_career}".strip()


def _attach_extracted_skills(jobs: List[NormalizedJob]) -> List[NormalizedJob]:
    """
    Mutates-and-returns: fills each NormalizedJob.extracted_skills from its
    description text using the rule-based skill extraction service
    (see skill_extraction_service.py -- no LLM call involved).
    """
    for job in jobs:
        job.extracted_skills = extract_skills(job.description)
    return jobs


async def analyze_career(request: CareerAnalyzeRequest) -> CareerAnalyzeResponse:
    warnings: List[str] = []
    query = _build_jobs_query(request)

    logger.info(
        "Analyzing career=%s experience=%s location=%s",
        request.target_career,
        request.experience_level,
        request.location,
    )

    try:
        raw_jobs = await serpapi_service.google_jobs_search(
            query=query,
            location=request.location,
            num_results=request.num_jobs,
        )
    except SerpApiError as exc:
        logger.error("SerpApi google_jobs_search failed: %s", exc.message)
        # Degrade gracefully: return an empty-but-valid response with a
        # clear warning instead of raising a raw 500, and WITHOUT
        # fabricating any job data.
        warnings.append(f"Could not retrieve live job data from SerpApi: {exc.message}")
        raw_jobs = []

    normalized_jobs = normalize_google_jobs_results(raw_jobs)

    if not normalized_jobs and not warnings:
        warnings.append(
            "No live job listings were found for this search. "
            "Try a broader target career or a different/omitted location."
        )

    normalized_jobs = _attach_extracted_skills(normalized_jobs)

    jobs_without_description = sum(1 for job in normalized_jobs if not job.description)
    if normalized_jobs and jobs_without_description:
        warnings.append(
            f"{jobs_without_description} of {len(normalized_jobs)} job listings had no "
            "description text available, so no skills could be extracted from them."
        )

    market = compute_market_analysis(normalized_jobs)
    skill_gap = compute_skill_gap(request.skills, market.skills)

    jobs: List[JobMatch] = []
    for job in normalized_jobs:
        match_result = calculate_job_match(job.extracted_skills, request.skills)
        jobs.append(
            JobMatch(
                job_id=job.job_id,
                title=job.title,
                company_name=job.company_name,
                location=job.location,
                via=job.via,
                posted_at=job.posted_at,
                apply_link=job.apply_link,
                detected_skills=job.extracted_skills,
                match_percentage=match_result.match_percentage,
                matched_skills=match_result.matched_skills,
                missing_skills=match_result.missing_skills,
                match_note=match_result.match_note,
            )
        )

    # Highest match first; jobs with no computable score (None) sort last.
    jobs.sort(key=lambda j: (j.match_percentage is None, -(j.match_percentage or 0)))

    return CareerAnalyzeResponse(
        career=request.target_career,
        market=market,
        skill_gap=skill_gap,
        jobs=jobs,
        roadmap=None,
        projects=[],
        resources=[],
        warnings=warnings,
    )
