import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { renderWithAnalysis } from './testUtils'
import { mockAnalysisResult, mockEmptyResult } from './mockData'
import Dashboard from '../pages/Dashboard'
import Jobs from '../pages/Jobs'
import Market from '../pages/Market'
import SkillGap from '../pages/SkillGap'
import Roadmap from '../pages/Roadmap'
import Projects from '../pages/Projects'

describe('Dashboard with real data shape', () => {
  it('renders stat cards, market summary, skill gap, and job matches', () => {
    renderWithAnalysis(<Dashboard />, { analysisValue: { result: mockAnalysisResult, status: 'success' } })
    expect(screen.getAllByText('AI Engineer').length).toBeGreaterThan(0)
    expect(screen.getAllByText('Python').length).toBeGreaterThan(0)
    expect(screen.getByText('AI Engineer - Entry Level')).toBeInTheDocument()
    // roadmap/projects empty -> honest empty states, not fabricated content
    expect(screen.getByText(/No roadmap yet/i)).toBeInTheDocument()
    expect(screen.getByText(/No projects yet/i)).toBeInTheDocument()
  })

  it('shows loading state', () => {
    renderWithAnalysis(<Dashboard />, { analysisValue: { status: 'loading' } })
    expect(screen.getByText(/Running your analysis/i)).toBeInTheDocument()
  })

  it('shows error state with retry', () => {
    renderWithAnalysis(<Dashboard />, {
      analysisValue: { status: 'error', error: { message: 'Backend unreachable' }, formValues: { target_career: 'x' } },
    })
    expect(screen.getByText('Backend unreachable')).toBeInTheDocument()
    expect(screen.getByText(/Try again/i)).toBeInTheDocument()
  })
})

describe('Jobs page with real data shape', () => {
  it('renders job cards including one with no computable match score', () => {
    renderWithAnalysis(<Jobs />, { analysisValue: { result: mockAnalysisResult, status: 'success' } })
    expect(screen.getByText('AI Engineer - Entry Level')).toBeInTheDocument()
    expect(screen.getByText('Junior ML Engineer')).toBeInTheDocument()
    expect(screen.getByText('AI/ML Developer')).toBeInTheDocument()
    // The ghost listing has match_percentage: null -> must show the honest
    // "unavailable" copy plus the backend's match_note, never a fabricated %.
    expect(screen.getAllByText('Match score unavailable').length).toBeGreaterThan(0)
    expect(screen.getByText(/match score was not calculated/i)).toBeInTheDocument()
    // Same ghost listing has detected_skills: [] -> honest copy, not a blank card.
    expect(screen.getByText(/Skills could not be reliably detected/i)).toBeInTheDocument()
  })

  it('filters jobs by search query', async () => {
    const { default: userEvent } = await import('@testing-library/user-event')
    renderWithAnalysis(<Jobs />, { analysisValue: { result: mockAnalysisResult, status: 'success' } })
    const input = screen.getByPlaceholderText(/Search title, company, or skill/i)
    await userEvent.type(input, 'Beta Labs')
    expect(screen.getByText('Junior ML Engineer')).toBeInTheDocument()
    expect(screen.queryByText('AI Engineer - Entry Level')).not.toBeInTheDocument()
  })

  it('shows an honest empty state when SerpApi found nothing', () => {
    renderWithAnalysis(<Jobs />, { analysisValue: { result: mockEmptyResult, status: 'success' } })
    expect(screen.getByText(/No live listings found/i)).toBeInTheDocument()
  })
})

describe('Market page with real data shape', () => {
  it('renders the skill demand chart and table without crashing', () => {
    renderWithAnalysis(<Market />, { analysisValue: { result: mockAnalysisResult, status: 'success' } })
    expect(screen.getByText('Skill demand')).toBeInTheDocument()
    expect(screen.getAllByText('Python').length).toBeGreaterThan(0)
    expect(screen.getAllByText('23').length).toBeGreaterThan(0) // sample_size stat
  })

  it('handles zero-sample market data honestly', () => {
    renderWithAnalysis(<Market />, { analysisValue: { result: mockEmptyResult, status: 'success' } })
    expect(screen.getByText(/No skill data available/i)).toBeInTheDocument()
  })
})

describe('SkillGap page with real data shape', () => {
  it('renders all four categories and the scoring methodology', () => {
    renderWithAnalysis(<SkillGap />, { analysisValue: { result: mockAnalysisResult, status: 'success' } })
    expect(screen.getByText('Strong skills')).toBeInTheDocument()
    expect(screen.getAllByText('Priority').length).toBeGreaterThan(0)
    expect(screen.getByText(/How this is scored/i)).toBeInTheDocument()
    expect(screen.getByText(/does NOT predict whether you will get hired/i)).toBeInTheDocument()
  })
})

describe('Roadmap page', () => {
  it('shows the exact required honest empty-state copy when roadmap is null', () => {
    renderWithAnalysis(<Roadmap />, { analysisValue: { result: mockAnalysisResult, status: 'success' } })
    expect(
      screen.getByText('Your personalized roadmap will appear here after analysis.')
    ).toBeInTheDocument()
  })
})

describe('Projects page', () => {
  it('does not invent recommendations when projects is an empty array', () => {
    renderWithAnalysis(<Projects />, { analysisValue: { result: mockAnalysisResult, status: 'success' } })
    expect(screen.getByText(/No project recommendations yet/i)).toBeInTheDocument()
  })
})
