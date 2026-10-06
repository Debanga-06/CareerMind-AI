from app.schemas.career import SkillGap
from app.services.project_service import recommend_projects


def test_recommends_known_skill_template():
    skill_gap = SkillGap(priority_skills=["Docker"], scoring_note="note")
    projects = recommend_projects(skill_gap, "Beginner")
    assert len(projects) == 1
    assert "Docker" in projects[0].skills_used


def test_recommends_generic_template_for_unknown_skill():
    skill_gap = SkillGap(priority_skills=["QuantumFlux"], scoring_note="note")
    projects = recommend_projects(skill_gap, "Intermediate")
    assert len(projects) == 1
    assert "QuantumFlux" in projects[0].title


def test_falls_back_to_develop_then_strong_skills():
    skill_gap = SkillGap(strong_skills=["Python"], scoring_note="note")
    projects = recommend_projects(skill_gap, "Beginner")
    assert len(projects) == 1
    assert "Python" in projects[0].skills_used


def test_respects_max_projects_limit():
    skill_gap = SkillGap(
        priority_skills=["Python", "Docker", "React", "SQL", "AWS", "Git"],
        scoring_note="note",
    )
    projects = recommend_projects(skill_gap, "Beginner", max_projects=2)
    assert len(projects) == 2
