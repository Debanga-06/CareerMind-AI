"""
Per-job match scoring.

Scoring formula (transparent, deterministic, documented)
---------------------------------------------------------
For a given job:

    required_skills = job.detected_skills   (from skill_extraction_service,
                                              i.e. skills found in THIS
                                              job's own description/highlights)
    matched_skills  = required_skills ∩ user_skills   (name match, case-insensitive,
                                                        after normalization)
    missing_skills  = required_skills - matched_skills

    match_percentage = round(len(matched_skills) / len(required_skills) * 100, 1)

Example: a job's description yields 8 detected skills, the user has 6 of
them -> match_percentage = 75.0, matched_skills = those 6, missing_skills
= the other 2.

Honesty guarantees
-------------------
* If a job has ZERO detected skills (e.g. the listing had no usable
  description text), `match_percentage` is left as `None` rather than
  fabricated as 0% or 100% — an explanatory `match_note` is set instead.
  A 0% score would wrongly imply the job requires skills the user lacks;
  a 100% score would wrongly imply a perfect match. Neither is true when
  we simply don't have enough text to know what the job requires.
* This score reflects *keyword/skill-name overlap* with what SerpApi
  returned for that single listing. It is not a prediction of interview
  or hiring success, and it does not account for skill proficiency depth,
  years of experience, or requirements not captured in the extraction
  taxonomy.
"""
from dataclasses import dataclass
from typing import List, Optional

from app.services.skill_extraction_service import normalize_skill_list

NO_SKILLS_DETECTED_NOTE = (
    "No skills could be reliably detected in this job's listing text, so a "
    "match score was not calculated (to avoid fabricating a percentage)."
)


@dataclass
class JobMatchResult:
    match_percentage: Optional[float]
    matched_skills: List[str]
    missing_skills: List[str]
    match_note: Optional[str] = None


def calculate_job_match(job_detected_skills: List[str], user_skills: List[str]) -> JobMatchResult:
    if not job_detected_skills:
        return JobMatchResult(
            match_percentage=None,
            matched_skills=[],
            missing_skills=[],
            match_note=NO_SKILLS_DETECTED_NOTE,
        )

    normalized_user_lower = {s.lower() for s in normalize_skill_list(user_skills)}

    matched = [s for s in job_detected_skills if s.lower() in normalized_user_lower]
    missing = [s for s in job_detected_skills if s.lower() not in normalized_user_lower]

    match_percentage = round(len(matched) / len(job_detected_skills) * 100, 1)

    return JobMatchResult(
        match_percentage=match_percentage,
        matched_skills=matched,
        missing_skills=missing,
        match_note=None,
    )
