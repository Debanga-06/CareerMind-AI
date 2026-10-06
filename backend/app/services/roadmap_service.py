"""
Roadmap generation.

Always produces a deterministic, rule-based roadmap first (so the feature
works with zero AI configuration and zero cost). If an AI provider is
configured (see ai_service.py) and reachable, its output is used only to
enrich the free-text `summary` — the phase structure itself always comes
from the transparent rule-based logic below, so the roadmap never depends
on an LLM successfully returning valid structured data.

Rule-based algorithm (documented, deterministic)
--------------------------------------------------
1. Build an ordered skill queue: priority_skills first (highest market
   demand among what the user is missing), then develop_skills.
2. Split the queue into phases of up to `SKILLS_PER_PHASE` skills each,
   capped at `MAX_LEARNING_PHASES` phases (extra skills roll into the
   final learning phase's description as "and beyond").
3. Phase 1 duration is longer for Beginners (more foundational ramp-up).
4. A final "Portfolio & Job Search" phase is always appended, recommending
   the user build projects (see project_service.py) and start applying.
"""
from __future__ import annotations

from typing import List, Tuple

from app.core.logging_config import get_logger
from app.schemas.career import SkillGap
from app.schemas.roadmap import RoadmapPhase, RoadmapPlan
from app.services.ai_service import AIProvider, AIProviderUnavailable

logger = get_logger(__name__)

SKILLS_PER_PHASE = 3
MAX_LEARNING_PHASES = 3


def _build_skill_queue(skill_gap: SkillGap) -> List[str]:
    queue: List[str] = []
    seen = set()
    for skill in list(skill_gap.priority_skills) + list(skill_gap.develop_skills):
        key = skill.lower()
        if key not in seen:
            seen.add(key)
            queue.append(skill)
    return queue


def _chunk(items: List[str], size: int) -> List[List[str]]:
    return [items[i : i + size] for i in range(0, len(items), size)]


def _build_rule_based_summary(target_career: str, experience_level: str, skill_gap: SkillGap) -> str:
    gap_count = len(skill_gap.priority_skills) + len(skill_gap.develop_skills)
    strong_count = len(skill_gap.strong_skills)

    if gap_count == 0:
        return (
            f"Your current skills already cover the market-demanded skills we detected for "
            f"{target_career}. Focus on building portfolio projects and applying -- see the "
            f"projects and resources below."
        )

    return (
        f"Based on {strong_count} skill(s) you already have and {gap_count} market-demanded "
        f"skill(s) you don't yet list, here is a {experience_level.lower()}-friendly path toward "
        f"{target_career}. It prioritizes the skills that showed up most often in current job "
        f"listings first."
    )


def _build_rule_based_phases(experience_level: str, skill_gap: SkillGap) -> List[RoadmapPhase]:
    queue = _build_skill_queue(skill_gap)
    chunks = _chunk(queue, SKILLS_PER_PHASE)[:MAX_LEARNING_PHASES]
    leftover = queue[SKILLS_PER_PHASE * len(chunks):]

    is_beginner = experience_level.strip().lower() == "beginner"
    phases: List[RoadmapPhase] = []

    for i, chunk in enumerate(chunks, start=1):
        duration = 4 if (i == 1 and is_beginner) else 3
        description = f"Learn and practice: {', '.join(chunk)}."
        if i == len(chunks) and leftover:
            description += f" Once comfortable, continue with: {', '.join(leftover)}."
        phases.append(
            RoadmapPhase(
                phase_number=i,
                title=f"Phase {i}: Build {chunk[0]}" if i == 1 else f"Phase {i}: Core Skills",
                duration_weeks=duration,
                focus_skills=chunk,
                description=description,
            )
        )

    if not phases:
        # No gap skills at all -> single phase focused on application/portfolio.
        phases.append(
            RoadmapPhase(
                phase_number=1,
                title="Phase 1: Portfolio & Applications",
                duration_weeks=3,
                focus_skills=list(skill_gap.strong_skills)[:SKILLS_PER_PHASE],
                description="Build 1-2 portfolio projects showcasing your existing skills and start applying.",
            )
        )
        return phases

    phases.append(
        RoadmapPhase(
            phase_number=len(phases) + 1,
            title=f"Phase {len(phases) + 1}: Portfolio & Job Search",
            duration_weeks=3,
            focus_skills=queue[:SKILLS_PER_PHASE],
            description=(
                "Build 1-2 portfolio projects that combine your new and existing skills "
                "(see project recommendations), polish your resume/GitHub, and start applying."
            ),
        )
    )
    return phases


async def generate_roadmap(
    target_career: str,
    experience_level: str,
    skill_gap: SkillGap,
    ai_provider: AIProvider,
) -> Tuple[RoadmapPlan, List[str]]:
    warnings: List[str] = []
    phases = _build_rule_based_phases(experience_level, skill_gap)
    summary = _build_rule_based_summary(target_career, experience_level, skill_gap)
    generated_by = "rule_based"

    try:
        skills_text = ", ".join(_build_skill_queue(skill_gap)) or "no major gaps"
        prompt = (
            f"Write a short (2-3 sentence), encouraging career-roadmap summary for someone "
            f"targeting a '{target_career}' role at '{experience_level}' level. Their skill "
            f"gaps, in priority order, are: {skills_text}. Do not use markdown, do not invent "
            f"specific job offers or guarantees of employment."
        )
        ai_summary = await ai_provider.generate_text(prompt, max_tokens=200)
        if ai_summary:
            summary = ai_summary
            generated_by = f"ai:{ai_provider.name}"
    except AIProviderUnavailable as exc:
        # Expected/common path (e.g. AI_PROVIDER=none) -- not a real error,
        # just informs the caller the rule-based summary was used.
        logger.debug("AI roadmap enrichment unavailable, using rule-based summary: %s", exc)
    except Exception as exc:  # noqa: BLE001 - never let AI enrichment break the roadmap
        logger.warning("AI roadmap enrichment failed, using rule-based summary: %s", exc)
        warnings.append("AI-generated summary was unavailable; showing a rule-based summary instead.")

    return RoadmapPlan(summary=summary, phases=phases, generated_by=generated_by), warnings
