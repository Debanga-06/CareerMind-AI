from app.schemas.career import NormalizedJob
from app.services.market_analysis_service import compute_market_analysis


def _job(skills):
    return NormalizedJob(extracted_skills=skills)


def test_market_analysis_frequency_and_percentage():
    jobs = [_job(["Python", "Docker"]) for _ in range(46)] + [_job(["Docker"]) for _ in range(4)]
    market = compute_market_analysis(jobs)

    assert market.sample_size == 50
    python_entry = next(s for s in market.skills if s.skill == "Python")
    assert python_entry.frequency == 46
    assert python_entry.percentage == 92.0

    docker_entry = next(s for s in market.skills if s.skill == "Docker")
    assert docker_entry.frequency == 50
    assert docker_entry.percentage == 100.0


def test_market_analysis_counts_skill_once_per_job():
    # Even if extraction somehow yields duplicates within one job, it must
    # only count once toward that skill's frequency.
    jobs = [NormalizedJob(extracted_skills=["Python", "Python", "Python"])]
    market = compute_market_analysis(jobs)
    assert market.skills[0].frequency == 1
    assert market.skills[0].percentage == 100.0


def test_market_analysis_empty_jobs_list():
    market = compute_market_analysis([])
    assert market.sample_size == 0
    assert market.skills == []


def test_market_analysis_sorted_by_demand_descending():
    jobs = [_job(["Python"])] * 10 + [_job(["Docker"])] * 3 + [_job(["AWS"])] * 5
    market = compute_market_analysis(jobs)
    skill_order = [s.skill for s in market.skills]
    assert skill_order.index("Python") < skill_order.index("AWS") < skill_order.index("Docker")
