import { MemoryRouter } from 'react-router-dom'
import { render } from '@testing-library/react'
import { AnalysisContext } from '../context/AnalysisContext'

export function renderWithAnalysis(ui, { analysisValue, route = '/' } = {}) {
  const value = {
    result: null,
    formValues: null,
    status: 'idle',
    error: null,
    runAnalysis: () => Promise.resolve(),
    reset: () => {},
    ...analysisValue,
  }

  return render(
    <MemoryRouter initialEntries={[route]}>
      <AnalysisContext.Provider value={value}>{ui}</AnalysisContext.Provider>
    </MemoryRouter>
  )
}
