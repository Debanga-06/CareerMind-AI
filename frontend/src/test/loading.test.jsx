import { describe, it, expect, vi } from 'vitest'
import { screen } from '@testing-library/react'
import AnalysisLoadingScreen from '../components/ui/AnalysisLoadingScreen'
import Onboarding from '../pages/Onboarding'
import { renderWithAnalysis } from './testUtils'

describe('AnalysisLoadingScreen', () => {
  it('renders all stage labels and never mentions AI/roadmap generation', () => {
    renderWithAnalysis(<AnalysisLoadingScreen />)
    expect(screen.getByText('Searching live job market…')).toBeInTheDocument()
    expect(screen.getByText('Analyzing job requirements…')).toBeInTheDocument()
    expect(screen.getByText('Identifying in-demand skills…')).toBeInTheDocument()
    expect(screen.getByText('Comparing your skills…')).toBeInTheDocument()
    expect(screen.getByText('Building your career intelligence…')).toBeInTheDocument()
    expect(screen.queryByText(/roadmap/i)).not.toBeInTheDocument()
  })
})

describe('Onboarding loading state', () => {
  it('replaces the form with the staged loading screen while status is loading', () => {
    renderWithAnalysis(<Onboarding />, { analysisValue: { status: 'loading' } })
    expect(screen.getByText('Running your analysis')).toBeInTheDocument()
    expect(screen.getByText('Searching live job market…')).toBeInTheDocument()
    // The form itself should not be present while loading.
    expect(screen.queryByLabelText('Target career')).not.toBeInTheDocument()
  })

  it('shows the form (not the loading screen) when idle', () => {
    renderWithAnalysis(<Onboarding />, { analysisValue: { status: 'idle' } })
    expect(screen.getByLabelText('Target career')).toBeInTheDocument()
    expect(screen.queryByText('Running your analysis')).not.toBeInTheDocument()
  })

  it('does not navigate until runAnalysis resolves successfully', async () => {
    const { default: userEvent } = await import('@testing-library/user-event')
    let resolveAnalysis
    const runAnalysis = vi.fn(
      () =>
        new Promise((resolve) => {
          resolveAnalysis = resolve
        })
    )
    renderWithAnalysis(<Onboarding />, { analysisValue: { status: 'idle', runAnalysis } })

    await userEvent.type(screen.getByLabelText('Target career'), 'AI Engineer')
    await userEvent.click(screen.getByRole('button', { name: /Analyze Career/i }))

    expect(runAnalysis).toHaveBeenCalledTimes(1)
    // Still on the onboarding form/page -- navigation only happens after resolve.
    expect(screen.getByText(/Tell us where you're headed/i)).toBeInTheDocument()

    resolveAnalysis({})
  })
})
