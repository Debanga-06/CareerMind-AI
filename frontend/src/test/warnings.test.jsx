import { describe, it, expect } from 'vitest'
import { screen } from '@testing-library/react'
import { render } from '@testing-library/react'
import { MemoryRouter, Routes, Route } from 'react-router-dom'
import WarningsBanner from '../components/ui/WarningsBanner'
import DashboardLayout from '../components/layout/DashboardLayout'
import { AnalysisContext } from '../context/AnalysisContext'
import { mockAnalysisResult, mockEmptyResult } from './mockData'

describe('WarningsBanner', () => {
  it('renders nothing when there are no warnings', () => {
    const { container } = render(<WarningsBanner warnings={[]} />)
    expect(container).toBeEmptyDOMElement()
  })

  it('renders each warning message', () => {
    render(<WarningsBanner warnings={['First warning', 'Second warning']} />)
    expect(screen.getByText('First warning')).toBeInTheDocument()
    expect(screen.getByText('Second warning')).toBeInTheDocument()
  })
})

function renderLayoutWithResult(result) {
  const value = { result, formValues: null, status: 'success', error: null, runAnalysis: () => {}, reset: () => {} }
  return render(
    <MemoryRouter initialEntries={['/dashboard']}>
      <AnalysisContext.Provider value={value}>
        <Routes>
          <Route element={<DashboardLayout />}>
            <Route path="/dashboard" element={<div>Page content</div>} />
          </Route>
        </Routes>
      </AnalysisContext.Provider>
    </MemoryRouter>
  )
}

describe('DashboardLayout warnings surfacing', () => {
  it('shows the backend warnings banner when the analysis result has warnings', () => {
    renderLayoutWithResult(mockEmptyResult)
    expect(screen.getByText(mockEmptyResult.warnings[0])).toBeInTheDocument()
  })

  it('shows no warnings banner when warnings is empty', () => {
    renderLayoutWithResult(mockAnalysisResult)
    // Page content should render fine, and nothing warning-shaped should appear.
    expect(screen.getByText('Page content')).toBeInTheDocument()
    expect(screen.queryByText(/No live job listings were found/i)).not.toBeInTheDocument()
  })
})
