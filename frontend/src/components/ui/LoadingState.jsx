import { Loader2 } from 'lucide-react'

export function Spinner({ className = 'h-4 w-4' }) {
  return <Loader2 className={`animate-spin ${className}`} strokeWidth={2.5} />
}

export default function LoadingState({ title = 'Loading', description, className = '' }) {
  return (
    <div className={`flex flex-col items-center justify-center rounded-2xl border border-line bg-white px-6 py-14 text-center ${className}`}>
      <Spinner className="h-6 w-6 text-signal-500" />
      <h3 className="mt-4 font-display text-base font-semibold text-ink">{title}</h3>
      {description && <p className="mt-1.5 max-w-sm text-sm text-muted">{description}</p>}
    </div>
  )
}

/** A lightweight skeleton block for card-shaped placeholders. */
export function SkeletonBlock({ className = '' }) {
  return <div className={`animate-pulse rounded-xl bg-ink/5 ${className}`} />
}
