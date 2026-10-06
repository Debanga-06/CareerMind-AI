// Shared helpers describing the (backend-computed, not-invented-here)
// skill-gap categories, so copy stays consistent across the Dashboard,
// Skill Gap, and Jobs pages.

export const SKILL_GAP_CATEGORIES = [
  {
    key: 'strong_skills',
    label: 'Strong skills',
    variant: 'strong',
    description: 'Skills you already listed that also show up in the market data.',
  },
  {
    key: 'develop_skills',
    label: 'Develop',
    variant: 'develop',
    description: "Market-relevant skills you're missing, in moderate demand (10–30% of jobs).",
  },
  {
    key: 'missing_skills',
    label: 'Missing',
    variant: 'missing',
    description: "Market-relevant skills you're missing, in high demand (30%+ of jobs).",
  },
  {
    key: 'priority_skills',
    label: 'Priority',
    variant: 'priority',
    description: 'The highest-demand missing skills — learn these first.',
  },
]

export function formatPercent(value, digits = 0) {
  if (value === null || value === undefined) return '—'
  return `${Number(value).toFixed(digits)}%`
}

export function matchTone(percentage) {
  if (percentage === null || percentage === undefined) return 'neutral'
  if (percentage >= 70) return 'strong'
  if (percentage >= 40) return 'develop'
  return 'missing'
}
