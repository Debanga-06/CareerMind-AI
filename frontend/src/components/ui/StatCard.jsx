import Card from './Card'

export default function StatCard({ icon: Icon, label, value, sublabel, tone = 'ink' }) {
  const toneClasses = {
    ink: 'text-ink bg-ink/5',
    signal: 'text-signal-600 bg-signal-50',
    amber: 'text-amber-600 bg-amber-50',
    rose: 'text-rose-600 bg-rose-50',
  }[tone]

  return (
    <Card className="p-5">
      <div className="flex items-center gap-3">
        {Icon && (
          <div className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-xl ${toneClasses}`}>
            <Icon className="h-5 w-5" strokeWidth={2} />
          </div>
        )}
        <div className="min-w-0">
          <p className="truncate text-sm text-muted">{label}</p>
          <p className="font-display text-2xl font-semibold text-ink leading-tight">{value}</p>
        </div>
      </div>
      {sublabel && <p className="mt-2 text-xs text-muted">{sublabel}</p>}
    </Card>
  )
}
