import { matchTone } from '../../lib/skillMeta'

const TONE_BAR = {
  strong: 'bg-signal-500',
  develop: 'bg-amber-500',
  missing: 'bg-rose-400',
  neutral: 'bg-ink/15',
}

const TONE_TEXT = {
  strong: 'text-signal-600',
  develop: 'text-amber-600',
  missing: 'text-rose-500',
  neutral: 'text-muted',
}

/** Shows a job's match_percentage as a labeled bar, or an honest "unavailable" note. */
export default function MatchMeter({ percentage, note }) {
  if (percentage === null || percentage === undefined) {
    return (
      <div className="text-right">
        <p className="text-xs font-medium text-muted">Match score unavailable</p>
        {note && <p className="mt-0.5 max-w-[10rem] text-[11px] leading-snug text-muted/80">{note}</p>}
      </div>
    )
  }

  const tone = matchTone(percentage)

  return (
    <div>
      <div className="mb-1.5 flex items-baseline justify-between">
        <span className="text-xs text-muted">Match</span>
        <span className={`font-display text-sm font-semibold ${TONE_TEXT[tone]}`}>{Math.round(percentage)}%</span>
      </div>
      <div className="h-1.5 w-full overflow-hidden rounded-full bg-ink/5">
        <div
          className={`h-full rounded-full ${TONE_BAR[tone]} transition-all duration-500`}
          style={{ width: `${Math.min(100, Math.max(0, percentage))}%` }}
        />
      </div>
    </div>
  )
}
