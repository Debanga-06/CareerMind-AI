import { describe, it, expect } from 'vitest'
import { render, screen } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import App from '../App'

const ROUTES = [
  { path: '/', expectText: /Analyze My Career/i },
  { path: '/onboarding', expectText: /Tell us where you're headed/i },
  { path: '/dashboard', expectText: /No analysis yet/i },
  { path: '/jobs', expectText: /No job matches yet/i },
  { path: '/market', expectText: /No market data yet/i },
  { path: '/skill-gap', expectText: /No skill gap yet/i },
  { path: '/roadmap', expectText: /No analysis yet/i },
  { path: '/projects', expectText: /No analysis yet/i },
  { path: '/this-route-does-not-exist', expectText: /Page not found/i },
]

describe('App routes render without crashing (idle / no-analysis state)', () => {
  for (const { path, expectText } of ROUTES) {
    it(`renders ${path}`, () => {
      render(
        <MemoryRouter initialEntries={[path]}>
          <App />
        </MemoryRouter>
      )
      expect(screen.getAllByText(expectText).length).toBeGreaterThan(0)
    })
  }
})
