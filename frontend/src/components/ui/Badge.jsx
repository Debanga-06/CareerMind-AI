const VARIANTS = {
  neutral: 'bg-ink/5 text-muted',
  strong: 'bg-signal-50 text-signal-700 ring-1 ring-inset ring-signal-100',
  develop: 'bg-amber-50 text-amber-600 ring-1 ring-inset ring-amber-100',
  missing: 'bg-rose-50 text-rose-600 ring-1 ring-inset ring-rose-100',
  priority: 'bg-amber-500 text-white',
  outline: 'border border-line text-muted',
}

export default function Badge({ children, variant = 'neutral', className = '', icon: Icon }) {
  return (
    <span
      className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-xs font-medium ${VARIANTS[variant]} ${className}`}
    >
      {Icon && <Icon className="h-3 w-3" strokeWidth={2.5} />}
      {children}
    </span>
  )
}
