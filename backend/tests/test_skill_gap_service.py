from app.schemas.career import SkillDemand
from app.services.skill_gap_service import (
    HIGH_DEMAND_THRESHOLD,
    LOW_DEMAND_THRESHOLD,
    PRIORITY_LIMIT,
    compute_skill_gap,
)


def _sd(skill, percentage, frequency=1):
    return SkillDemand(skill=skill, frequency=frequency, percentage=percentage)


def test_user_skill_present_in_market_is_strong():
    market = [_sd("Python", 90.0)]
    gap = compute_skill_gap(["Python"], market)
    assert gap.strong_skills == ["Python"]
    assert gap.missing_skills == []
    assert gap.develop_skills == []


def test_high_demand_absent_skill_is_missing():
    market = [_sd("Docker", HIGH_DEMAND_THRESHOLD)]
    gap = compute_skill_gap([], market)
    assert gap.missing_skills == ["Docker"]
    assert gap.develop_skills == []


def test_moderate_demand_absent_skill_is_develop():
    market = [_sd("Redis", (HIGH_DEMAND_THRESHOLD + LOW_DEMAND_THRESHOLD) / 2)]
    gap = compute_skill_gap([], market)
    assert gap.develop_skills == ["Redis"]
    assert gap.missing_skills == []


def test_low_demand_absent_skill_is_ignored():
    market = [_sd("Rust", LOW_DEMAND_THRESHOLD - 1)]
    gap = compute_skill_gap([], market)
    assert gap.missing_skills == []
    assert gap.develop_skills == []
    assert gap.strong_skills == []


def test_priority_skills_is_top_slice_of_missing():
    market = [_sd(f"Skill{i}", 90.0 - i) for i in range(PRIORITY_LIMIT + 3)]
    gap = compute_skill_gap([], market)
    assert gap.priority_skills == gap.missing_skills[:PRIORITY_LIMIT]
    assert len(gap.priority_skills) == PRIORITY_LIMIT


def test_user_skills_are_normalized_before_matching():
    # user typed "ml", market reports canonical "Machine Learning"
    market = [_sd("Machine Learning", 80.0)]
    gap = compute_skill_gap(["ml"], market)
    assert gap.strong_skills == ["Machine Learning"]


def test_scoring_note_present_and_non_predictive():
    gap = compute_skill_gap([], [])
    assert gap.scoring_note is not None
    assert "NOT predict" in gap.scoring_note
