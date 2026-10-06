import { useContext } from 'react'
import { AnalysisContext } from '../context/AnalysisContext'

export function useAnalysis() {
  const ctx = useContext(AnalysisContext)
  if (!ctx) {
    throw new Error('useAnalysis must be used within an AnalysisProvider')
  }
  return ctx
}
