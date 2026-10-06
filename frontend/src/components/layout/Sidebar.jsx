import { NavLink, Link } from 'react-router-dom'
import {
  LayoutDashboard,
  Briefcase,
  TrendingUp,
  Target,
  Map,
  FolderKanban,
  Share2,
  Plus,
  X,
} from 'lucide-react'

const NAV_ITEMS = [
  { to: '/dashboard', label: 'Overview', icon: LayoutDashboard },
  { to: '/jobs', label: 'Job matches', icon: Briefcase },
  { to: '/market', label: 'Market', icon: TrendingUp },
  { to: '/skill-gap', label: 'Skill gap', icon: Target },
  { to: '/roadmap', label: 'Roadmap', icon: Map },
  { to: '/projects', label: 'Projects', icon: FolderKanban },
]

function NavItems({ onNavigate }) {
  return (
    <nav className="flex flex-1 flex-col gap-1 px-3">
      {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
        <NavLink
          key={to}
          to={to}
          onClick={onNavigate}
          className={({ isActive }) =>
            `flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-medium transition-colors ${
              isActive ? 'bg-ink text-white' : 'text-muted hover:bg-ink/5 hover:text-ink'
            }`
          }
        >
          <Icon className="h-4 w-4 shrink-0" strokeWidth={2} />
          {label}
        </NavLink>
      ))}
    </nav>
  )
}

export function Sidebar() {
  return (
    <aside className="hidden w-60 shrink-0 flex-col border-r border-line bg-white py-5 lg:flex">
      <Link to="/" className="flex items-center gap-2 px-5 pb-6">
        <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink text-white">
          <Share2 className="h-4 w-4" strokeWidth={2.25} />
        </span>
        <span className="font-display text-base font-semibold tracking-tight text-ink">CareerGraph</span>
      </Link>
      <NavItems />
      <div className="mt-4 px-3">
        <Link
          to="/onboarding"
          className="flex items-center justify-center gap-2 rounded-lg border border-dashed border-line px-3 py-2.5 text-sm font-medium text-muted hover:border-ink/30 hover:text-ink transition-colors"
        >
          <Plus className="h-4 w-4" /> New analysis
        </Link>
      </div>
    </aside>
  )
}

export function MobileSidebar({ open, onClose }) {
  if (!open) return null
  return (
    <div className="fixed inset-0 z-50 lg:hidden">
      <div className="absolute inset-0 bg-ink/30" onClick={onClose} />
      <div className="absolute inset-y-0 left-0 flex w-72 flex-col bg-white py-5 shadow-xl">
        <div className="flex items-center justify-between px-5 pb-6">
          <Link to="/" className="flex items-center gap-2">
            <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-ink text-white">
              <Share2 className="h-4 w-4" strokeWidth={2.25} />
            </span>
            <span className="font-display text-base font-semibold tracking-tight text-ink">CareerGraph</span>
          </Link>
          <button onClick={onClose} className="flex h-8 w-8 items-center justify-center rounded-lg text-muted hover:bg-ink/5" aria-label="Close menu">
            <X className="h-5 w-5" />
          </button>
        </div>
        <NavItems onNavigate={onClose} />
        <div className="mt-4 px-3">
          <Link
            to="/onboarding"
            onClick={onClose}
            className="flex items-center justify-center gap-2 rounded-lg border border-dashed border-line px-3 py-2.5 text-sm font-medium text-muted"
          >
            <Plus className="h-4 w-4" /> New analysis
          </Link>
        </div>
      </div>
    </div>
  )
}
