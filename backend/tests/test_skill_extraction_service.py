from app.services.skill_extraction_service import (
    extract_skills,
    normalize_skill_list,
    normalize_skill_name,
)


def test_extract_skills_from_description():
    text = (
        "We need strong Python programming experience, familiarity with "
        "Py Torch and ML/Deep Learning. Docker, Kubernetes (k8s) and AWS "
        "required. Git and GitHub. SQL and PostgreSQL."
    )
    skills = extract_skills(text)
    assert "Python" in skills
    assert "PyTorch" in skills
    assert "Machine Learning" in skills
    assert "Deep Learning" in skills
    assert "Docker" in skills
    assert "Kubernetes" in skills
    assert "AWS" in skills
    assert "Git" in skills
    assert "GitHub" in skills
    assert "SQL" in skills
    assert "PostgreSQL" in skills


def test_extract_skills_deduplicates():
    text = "Python, python, PYTHON, Python programming — all the Python you can handle."
    skills = extract_skills(text)
    assert skills.count("Python") == 1


def test_extract_skills_empty_or_none():
    assert extract_skills("") == []
    assert extract_skills(None) == []
    assert extract_skills("no recognizable tech skills mentioned here at all") == []


def test_normalize_skill_name_variations():
    assert normalize_skill_name("ML") == "Machine Learning"
    assert normalize_skill_name("Py Torch") == "PyTorch"
    assert normalize_skill_name("python programming") == "Python"
    assert normalize_skill_name("pytorch") == "PyTorch"
    assert normalize_skill_name("k8s") == "Kubernetes"


def test_normalize_skill_name_preserves_unknown_skill():
    # A niche/custom skill the taxonomy doesn't know should never be dropped.
    result = normalize_skill_name("blender 3d modeling")
    assert "blender" in result.lower()


def test_normalize_skill_list_dedupes_case_insensitively():
    result = normalize_skill_list(["Python", "python", "PYTHON", "ML", "machine learning"])
    assert result.count("Python") == 1
    assert result.count("Machine Learning") == 1
