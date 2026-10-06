import { AlertCircle } from 'lucide-react'

/** Surfaces the backend's `warnings` array (e.g. partial SerpApi failures, no results found). */
export default function WarningsBanner({ warnings, className = '' }) {
  if (!warnings || warnings.length === 0) return null

  return (
    <div className={`rounded-xl border border-amber-100 bg-amber-50/70 px-4 py-3 ${className}`}>
      <div className="flex gap-2.5">
        <AlertCircle className="mt-0.5 h-4 w-4 shrink-0 text-amber-600" />
        <div className="space-y-1">
          {warnings.map((w, i) => (
            <p key={i} className="text-sm text-amber-700">
              {w}
            </p>
          ))}
        </div>
      </div>
    </div>
  )
}
