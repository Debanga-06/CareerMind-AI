import pytest

from app.schemas.career import SkillGap
from app.services.ai_service import AIProviderUnavailable, NullAIProvider
from app.services.roadmap_service import generate_roadmap


class _FakeAIProvider:
    name = "fake"

    def __init__(self, text=None, raise_exc=None):
        self._text = text
        self._raise_exc = raise_exc

    async def generate_text(self, prompt, max_tokens=600):
        if self._raise_exc:
            raise self._raise_exc
        return self._text


@pytest.mark.asyncio
async def test_roadmap_falls_back_to_rule_based_when_ai_unavailable():
    skill_gap = SkillGap(
        strong_skills=["Python"],
        develop_skills=["SQL"],
        missing_skills=["Docker", "Machine Learning"],
        priority_skills=["Docker", "Machine Learning"],
        scoring_note="note",
    )
    plan, warnings = await generate_roadmap("AI Engineer", "Beginner", skill_gap, NullAIProvider())
    assert plan.generated_by == "rule_based"
    assert len(plan.phases) >= 2
    assert warnings == []  # AIProviderUnavailable is expected, not a warning-worthy failure


@pytest.mark.asyncio
async def test_roadmap_uses_ai_summary_when_available():
    skill_gap = SkillGap(priority_skills=["Docker"], scoring_note="note")
    fake = _FakeAIProvider(text="A custom AI-written summary.")
    plan, warnings = await generate_roadmap("AI Engineer", "Beginner", skill_gap, fake)
    assert plan.generated_by == "ai:fake"
    assert plan.summary == "A custom AI-written summary."
    assert warnings == []


@pytest.mark.asyncio
async def test_roadmap_handles_unexpected_ai_failure_gracefully():
    skill_gap = SkillGap(priority_skills=["Docker"], scoring_note="note")
    fake = _FakeAIProvider(raise_exc=RuntimeError("boom"))
    plan, warnings = await generate_roadmap("AI Engineer", "Beginner", skill_gap, fake)
    assert plan.generated_by == "rule_based"
    assert len(warnings) == 1


@pytest.mark.asyncio
async def test_roadmap_phases_sequence_priority_skills_first():
    skill_gap = SkillGap(
        priority_skills=["A", "B", "C"],
        develop_skills=["D", "E"],
        scoring_note="note",
    )
    plan, _ = await generate_roadmap("Role", "Intermediate", skill_gap, NullAIProvider())
    # Phase 1 should be built from priority skills before develop skills.
    assert plan.phases[0].focus_skills == ["A", "B", "C"]


@pytest.mark.asyncio
async def test_roadmap_handles_empty_skill_gap():
    skill_gap = SkillGap(strong_skills=["Python"], scoring_note="note")
    plan, warnings = await generate_roadmap("Role", "Advanced", skill_gap, NullAIProvider())
    assert len(plan.phases) == 1
    assert "Portfolio" in plan.phases[0].title
