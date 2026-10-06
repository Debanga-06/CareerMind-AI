import { createContext, useCallback, useMemo, useState } from 'react'
import { analyzeCareer } from '../api/careerApi'

const STORAGE_KEY = 'cg_last_analysis'

export const AnalysisContext = createContext(null)

function loadCached() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY)
    return raw ? JSON.parse(raw) : null
  } catch {
    return null
  }
}

export function AnalysisProvider({ children }) {
  const [result, setResult] = useState(loadCached)
  const [formValues, setFormValues] = useState(null)
  const [status, setStatus] = useState('idle') // idle | loading | success | error
  const [error, setError] = useState(null)

  const runAnalysis = useCallback(async (values) => {
    setStatus('loading')
    setError(null)
    setFormValues(values)
    try {
      const data = await analyzeCareer(values)
      setResult(data)
      setStatus('success')
      try {
        sessionStorage.setItem(STORAGE_KEY, JSON.stringify(data))
      } catch {
        // sessionStorage can fail in private/incognito contexts -- non-fatal.
      }
      return data
    } catch (err) {
      setStatus('error')
      setError(err)
      throw err
    }
  }, [])

  const reset = useCallback(() => {
    setResult(null)
    setFormValues(null)
    setStatus('idle')
    setError(null)
    sessionStorage.removeItem(STORAGE_KEY)
  }, [])

  const value = useMemo(
    () => ({ result, formValues, status, error, runAnalysis, reset }),
    [result, formValues, status, error, runAnalysis, reset]
  )

  return <AnalysisContext.Provider value={value}>{children}</AnalysisContext.Provider>
}
