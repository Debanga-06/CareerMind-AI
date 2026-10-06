const ACCENTS = {
  none: '',
  signal: 'border-l-2 border-l-signal-500',
  amber: 'border-l-2 border-l-amber-500',
  rose: 'border-l-2 border-l-rose-500',
}

export default function Card({ children, className = '', accent = 'none', as: Comp = 'div', ...rest }) {
  return (
    <Comp
      className={`rounded-2xl border border-line bg-white shadow-card ${ACCENTS[accent]} ${className}`}
      {...rest}
    >
      {children}
    </Comp>
  )
}

export function CardHeader({ title, subtitle, action, className = '' }) {
  return (
    <div className={`flex items-start justify-between gap-4 px-6 pt-5 ${className}`}>
      <div>
        <h3 className="font-display text-base font-semibold text-ink">{title}</h3>
        {subtitle && <p className="mt-0.5 text-sm text-muted">{subtitle}</p>}
      </div>
      {action}
    </div>
  )
}

export function CardBody({ children, className = '' }) {
  return <div className={`px-6 py-5 ${className}`}>{children}</div>
}
