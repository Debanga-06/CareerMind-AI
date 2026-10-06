"""
Skill-gap calculation: compares a user's stated skills against the market
skill-demand data produced by market_analysis_service.

Scoring formula (transparent, deterministic, documented)
---------------------------------------------------------
Inputs:
  * user_skills   -> normalized to canonical skill names
  * market_skills -> List[SkillDemand] (skill, frequency, percentage),
                      already sorted by demand percentage descending

For every market skill, it is bucketed as follows:

  1. STRONG      -> the user already has this skill (it appears, in
                     canonical form, in their stated skills). This is
                     independent of demand percentage: any market-relevant
                     skill the user already has counts as a strength.

  2. MISSING     -> the user does NOT have the skill, AND it appears in
                     >= HIGH_DEMAND_THRESHOLD% of analyzed jobs (default 30%).
                     These are high-priority gaps.

  3. DEVELOP     -> the user does NOT have the skill, AND it appears in
                     between LOW_DEMAND_THRESHOLD% and HIGH_DEMAND_THRESHOLD%
                     of analyzed jobs (default 10%–30%). Worth developing,
                     but lower urgency than MISSING.

  4. (ignored)   -> demand below LOW_DEMAND_THRESHOLD% is treated as noise
                     for gap purposes (too rare in this sample to act on).

PRIORITY_SKILLS = the top `PRIORITY_LIMIT` (default 5) entries of MISSING,
i.e. the highest-demand skills the user is missing — these are surfaced as
"learn these first".

IMPORTANT: This score reflects overlap with skills mentioned in a sample of
current job postings. It is a directional signal for what to learn next,
NOT a prediction of interview success or hiring likelihood, and it does not
account for skill depth/proficiency — only presence/absence of a skill
name in the user's stated skill list.
"""
from typing import List

from app.schemas.career import SkillDemand, SkillGap
from app.services.skill_extraction_service import normalize_skill_list

HIGH_DEMAND_THRESHOLD = 30.0
LOW_DEMAND_THRESHOLD = 10.0
PRIORITY_LIMIT = 5

SCORING_NOTE = (
    "Skills are compared by name only (not proficiency depth). A market "
    "skill is 'strong' if you already listed it. Unlisted market skills "
    f"are 'missing' if they appear in >= {HIGH_DEMAND_THRESHOLD:.0f}% of "
    f"analyzed jobs, or 'develop' if they appear in "
    f"{LOW_DEMAND_THRESHOLD:.0f}-{HIGH_DEMAND_THRESHOLD:.0f}% of jobs. "
    "'priority_skills' are the highest-demand missing skills. This does "
    "NOT predict whether you will get hired."
)


def compute_skill_gap(user_skills: List[str], market_skills: List[SkillDemand]) -> SkillGap:
    normalized_user = {s.lower() for s in normalize_skill_list(user_skills)}

    strong: List[str] = []
    missing: List[str] = []
    develop: List[str] = []

    for entry in market_skills:  # already sorted by demand descending
        if entry.skill.lower() in normalized_user:
            strong.append(entry.skill)
        elif entry.percentage >= HIGH_DEMAND_THRESHOLD:
            missing.append(entry.skill)
        elif entry.percentage >= LOW_DEMAND_THRESHOLD:
            develop.append(entry.skill)
        # else: below LOW_DEMAND_THRESHOLD -> ignored as noise

    priority = missing[:PRIORITY_LIMIT]

    return SkillGap(
        strong_skills=strong,
        develop_skills=develop,
        missing_skills=missing,
        priority_skills=priority,
        scoring_note=SCORING_NOTE,
    )
