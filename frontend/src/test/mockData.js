// Mirrors the real /api/careers/analyze response shape from the backend
// (see CareerAnalyzeResponse / JobMatch / MarketAnalysis / SkillGap
// schemas), including the honest edge cases: a job with no computable
// match_percentage (match_note set instead), and roadmap/projects empty.
export const mockAnalysisResult = {
  career: 'AI Engineer',
  market: {
    sample_size: 23,
    skills: [
      { skill: 'Python', frequency: 21, percentage: 91.3 },
      { skill: 'Machine Learning', frequency: 14, percentage: 60.9 },
      { skill: 'Docker', frequency: 9, percentage: 39.1 },
      { skill: 'SQL', frequency: 7, percentage: 30.4 },
      { skill: 'AWS', frequency: 5, percentage: 21.7 },
    ],
  },
  skill_gap: {
    strong_skills: ['Python', 'Git'],
    develop_skills: ['SQL'],
    missing_skills: ['Machine Learning', 'Docker'],
    priority_skills: ['Machine Learning', 'Docker'],
    scoring_note:
      "Skills are compared by name only (not proficiency depth). This does NOT predict whether you will get hired.",
  },
  jobs: [
    {
      job_id: 'job-1',
      title: 'AI Engineer - Entry Level',
      company_name: 'Example Corp',
      location: 'Bengaluru, Karnataka, India',
      via: 'via LinkedIn',
      posted_at: '3 days ago',
      apply_link: 'https://example.com/apply/1',
      detected_skills: ['Python', 'Machine Learning', 'Docker'],
      match_percentage: 66.7,
      matched_skills: ['Python'],
      missing_skills: ['Machine Learning', 'Docker'],
      match_note: null,
    },
    {
      job_id: 'job-2',
      title: 'Junior ML Engineer',
      company_name: 'Beta Labs',
      location: 'Remote',
      via: 'via Indeed',
      posted_at: '5 days ago',
      apply_link: 'https://example.com/apply/2',
      detected_skills: ['Python', 'SQL', 'Git'],
      match_percentage: 100.0,
      matched_skills: ['Python', 'SQL', 'Git'],
      missing_skills: [],
      match_note: null,
    },
    {
      job_id: 'job-3',
      title: 'AI/ML Developer',
      company_name: 'Ghost Listing Co',
      location: 'Hyderabad',
      via: null,
      posted_at: null,
      apply_link: null,
      detected_skills: [],
      match_percentage: null,
      matched_skills: [],
      missing_skills: [],
      match_note:
        'No skills could be reliably detected in this job listing text, so a match score was not calculated (to avoid fabricating a percentage).',
    },
  ],
  roadmap: null,
  projects: [],
  resources: [],
  warnings: [],
}

export const mockEmptyResult = {
  career: 'Extremely Rare Job Title',
  market: { sample_size: 0, skills: [] },
  skill_gap: {
    strong_skills: [],
    develop_skills: [],
    missing_skills: [],
    priority_skills: [],
    scoring_note: null,
  },
  jobs: [],
  roadmap: null,
  projects: [],
  resources: [],
  warnings: ['No live job listings were found for this search.'],
}
