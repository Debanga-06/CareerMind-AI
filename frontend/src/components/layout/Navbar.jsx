import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Menu, X, Share2 } from 'lucide-react'
import Button from '../ui/Button'

const LINKS = [
  { label: 'How it works', href: '#how-it-works' },
  { label: 'Market data', href: '#market-data' },
]

export default function Navbar() {
  const [open, setOpen] = useState(false)

  return (
    <header className="sticky top-0 z-40 border-b border-line bg-paper/85 backdrop-blur">
      <div className="container-page flex h-16 items-center justify-between">
        <Link to="/" className="flex items-center gap-2">
          <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink text-white">
            <Share2 className="h-4 w-4" strokeWidth={2.25} />
          </span>
          <span className="font-display text-lg font-semibold tracking-tight text-ink">CareerGraph AI</span>
        </Link>

        <nav className="hidden items-center gap-8 md:flex">
          {LINKS.map((l) => (
            <a key={l.href} href={l.href} className="text-sm text-muted hover:text-ink transition-colors">
              {l.label}
            </a>
          ))}
        </nav>

        <div className="hidden items-center gap-3 md:flex">
          <Button variant="ghost" size="sm" to="/onboarding">
            Sign in
          </Button>
          <Button variant="accent" size="sm" to="/onboarding">
            Analyze My Career
          </Button>
        </div>

        <button
          className="flex h-9 w-9 items-center justify-center rounded-lg text-ink md:hidden"
          onClick={() => setOpen((o) => !o)}
          aria-label="Toggle menu"
        >
          {open ? <X className="h-5 w-5" /> : <Menu className="h-5 w-5" />}
        </button>
      </div>

      {open && (
        <div className="border-t border-line bg-paper px-5 py-4 md:hidden">
          <nav className="flex flex-col gap-3">
            {LINKS.map((l) => (
              <a key={l.href} href={l.href} onClick={() => setOpen(false)} className="text-sm text-muted hover:text-ink">
                {l.label}
              </a>
            ))}
            <Button variant="accent" size="sm" to="/onboarding" className="mt-2 w-full">
              Analyze My Career
            </Button>
          </nav>
        </div>
      )}
    </header>
  )
}
