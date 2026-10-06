import { useEffect, useState } from 'react'
import { Search, ListChecks, TrendingUp, GitCompare, Network } from 'lucide-react'
import { Spinner } from './LoadingState'

// These describe the real steps the backend performs for
// POST /api/careers/analyze (live SerpApi search -> skill extraction ->
// market analysis -> skill-gap + match scoring). Deliberately doesn't
// mention a roadmap/AI step, since that endpoint isn't called here.
const STAGES = [
  { icon: Search, label: 'Searching live job market…' },
  { icon: ListChecks, label: 'Analyzing job requirements…' },
  { icon: TrendingUp, label: 'Identifying in-demand skills…' },
  { icon: GitCompare, label: 'Comparing your skills…' },
  { icon: Network, label: 'Building your career intelligence…' },
]

const STAGE_INTERVAL_MS = 1400

export default function AnalysisLoadingScreen({ className = '' }) {
  const [stageIndex, setStageIndex] = useState(0)

  useEffect(() => {
    // Cycles through the stage copy for as long as the request is in
    // flight. This is UI pacing only -- the backend doesn't stream real
    // sub-progress, so we never claim a stage "completed," only that it's
    // in progress, and we never mention roadmap/AI output that this
    // request doesn't produce.
    const id = setInterval(() => {
      setStageIndex((i) => Math.min(i + 1, STAGES.length - 1))
    }, STAGE_INTERVAL_MS)
    return () => clearInterval(id)
  }, [])

  return (
    <div className={`flex flex-col items-center py-8 text-center ${className}`}>
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-signal-50">
        <Spinner className="h-6 w-6 text-signal-500" />
      </div>
      <p className="mt-5 font-display text-lg font-semibold text-ink">Running your analysis</p>
      <p className="mt-1 text-sm text-muted">This calls the live backend — usually takes a few seconds.</p>

      <ul className="mt-7 w-full max-w-xs space-y-3 text-left">
        {STAGES.map((stage, i) => {
          const isActive = i === stageIndex
          const isDone = i < stageIndex
          return (
            <li
              key={stage.label}
              className={`flex items-center gap-3 rounded-lg px-3 py-2 text-sm transition-colors ${
                isActive ? 'bg-ink/5 text-ink font-medium' : isDone ? 'text-muted' : 'text-muted/50'
              }`}
            >
              <span
                className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full ${
                  isActive ? 'bg-signal-500 text-white' : isDone ? 'bg-ink/10 text-ink' : 'bg-ink/5 text-muted/50'
                }`}
              >
                <stage.icon className="h-3.5 w-3.5" strokeWidth={2.25} />
              </span>
              {stage.label}
            </li>
          )
        })}
      </ul>
    </div>
  )
}
