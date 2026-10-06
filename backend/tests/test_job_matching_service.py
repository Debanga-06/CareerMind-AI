from app.services.job_matching_service import NO_SKILLS_DETECTED_NOTE, calculate_job_match


def test_full_match():
    result = calculate_job_match(["Python", "Git"], ["Python", "Git", "React"])
    assert result.match_percentage == 100.0
    assert result.matched_skills == ["Python", "Git"]
    assert result.missing_skills == []
    assert result.match_note is None


def test_partial_match():
    result = calculate_job_match(["Python", "Git", "PyTorch", "Docker"], ["Python", "Git"])
    assert result.match_percentage == 50.0
    assert result.matched_skills == ["Python", "Git"]
    assert result.missing_skills == ["PyTorch", "Docker"]


def test_zero_match():
    result = calculate_job_match(["PyTorch", "Docker"], ["Python", "Git"])
    assert result.match_percentage == 0.0
    assert result.matched_skills == []
    assert result.missing_skills == ["PyTorch", "Docker"]


def test_matching_is_case_insensitive_and_normalizes_user_skills():
    result = calculate_job_match(["Machine Learning", "PyTorch"], ["ml", "py torch"])
    assert result.match_percentage == 100.0
    assert set(result.matched_skills) == {"Machine Learning", "PyTorch"}


def test_no_detected_skills_does_not_fabricate_score():
    result = calculate_job_match([], ["Python", "Git"])
    assert result.match_percentage is None
    assert result.matched_skills == []
    assert result.missing_skills == []
    assert result.match_note == NO_SKILLS_DETECTED_NOTE


def test_no_user_skills_gives_zero_percent_not_none():
    # This IS meaningful data (job has requirements, user listed none),
    # so it must be a real 0.0, not None.
    result = calculate_job_match(["Python", "Docker"], [])
    assert result.match_percentage == 0.0
    assert result.missing_skills == ["Python", "Docker"]
