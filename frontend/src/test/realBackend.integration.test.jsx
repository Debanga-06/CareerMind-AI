import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithAnalysis } from './testUtils'
import Dashboard from '../pages/Dashboard'
import Jobs from '../pages/Jobs'
import Market from '../pages/Market'
import SkillGap from '../pages/SkillGap'
import realBackendResponse from './realBackendResponse.json'

// This fixture was captured live from `POST /api/careers/analyze` against
// the real FastAPI backend (Stage 5) with a mocked SerpApi upstream, using
// exactly the example request from the spec:
//   { target_career: "AI Engineer", skills: ["Python","React","JavaScript","Git"],
//     experience_level: "Beginner", location: "India" }
// This proves the frontend renders the *actual* shape the backend emits,
// not just our hand-written mock.
describe('Pages render the real captured backend response without crashing', () => {
  const analysisValue = { result: realBackendResponse, status: 'success' }

  it('Dashboard', () => {
    renderWithAnalysis(<Dashboard />, { analysisValue })
    expect(screen.getAllByText('AI Engineer').length).toBeGreaterThan(0)
    expect(screen.getAllByText(String(realBackendResponse.market.sample_size)).length).toBeGreaterThan(0)
  })

  it('Jobs', () => {
    renderWithAnalysis(<Jobs />, { analysisValue })
    for (const job of realBackendResponse.jobs) {
      if (job.title) expect(screen.getAllByText(job.title).length).toBeGreaterThan(0)
    }
  })

  it('Market', () => {
    renderWithAnalysis(<Market />, { analysisValue })
    expect(screen.getAllByText(realBackendResponse.market.skills[0].skill).length).toBeGreaterThan(0)
  })

  it('SkillGap', () => {
    renderWithAnalysis(<SkillGap />, { analysisValue })
    expect(screen.getByText(realBackendResponse.skill_gap.scoring_note)).toBeInTheDocument()
  })
})
