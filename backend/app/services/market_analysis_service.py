"""
Market analysis: how often each skill appears across a set of real,
currently-live job listings.

Formula (transparent, documented per project requirements):

    frequency(skill)  = number of jobs whose description/highlights
                         mention that skill at least once
    percentage(skill) = round(frequency(skill) / sample_size * 100, 1)

    where sample_size = number of jobs actually analyzed (len(jobs)).

Example: if 50 jobs are analyzed and "Python" is mentioned in 46 of them,
frequency = 46 and percentage = 92.0.

A skill is counted at most once per job (a job description that says
"Python" three times still counts as 1 toward Python's frequency) so that
verbose listings don't distort the demand signal.
"""
from collections import Counter
from typing import List

from app.schemas.career import MarketAnalysis, SkillDemand, NormalizedJob


def compute_market_analysis(jobs: List[NormalizedJob]) -> MarketAnalysis:
    sample_size = len(jobs)
    if sample_size == 0:
        return MarketAnalysis(sample_size=0, skills=[])

    frequency: Counter = Counter()
    for job in jobs:
        # set(...) ensures at most one count per job, per the formula above.
        for skill in set(job.extracted_skills):
            frequency[skill] += 1

    skills = [
        SkillDemand(
            skill=skill,
            frequency=count,
            percentage=round((count / sample_size) * 100, 1),
        )
        for skill, count in frequency.items()
    ]

    # Highest demand first; alphabetical tiebreak for determinism.
    skills.sort(key=lambda s: (-s.frequency, s.skill))
    return MarketAnalysis(sample_size=sample_size, skills=skills)
