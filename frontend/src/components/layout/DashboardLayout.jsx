import { useState } from 'react'
import { Outlet } from 'react-router-dom'
import { Menu, Share2 } from 'lucide-react'
import { Sidebar, MobileSidebar } from './Sidebar'
import WarningsBanner from '../ui/WarningsBanner'
import { useAnalysis } from '../../hooks/useAnalysis'

export default function DashboardLayout() {
  const [mobileOpen, setMobileOpen] = useState(false)
  const { result } = useAnalysis()

  return (
    <div className="flex min-h-screen bg-paper">
      <Sidebar />
      <MobileSidebar open={mobileOpen} onClose={() => setMobileOpen(false)} />

      <div className="flex min-w-0 flex-1 flex-col">
        <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-line bg-paper/85 px-5 backdrop-blur sm:px-8">
          <div className="flex items-center gap-3">
            <button
              className="flex h-9 w-9 items-center justify-center rounded-lg text-ink lg:hidden"
              onClick={() => setMobileOpen(true)}
              aria-label="Open menu"
            >
              <Menu className="h-5 w-5" />
            </button>
            <span className="flex h-7 w-7 items-center justify-center rounded-md bg-ink text-white lg:hidden">
              <Share2 className="h-3.5 w-3.5" />
            </span>
            <div>
              <p className="text-xs text-muted">Target career</p>
              <p className="font-display text-sm font-semibold text-ink">
                {result?.career || 'No analysis yet'}
              </p>
            </div>
          </div>
        </header>

        <main className="flex-1 px-5 py-6 sm:px-8 sm:py-8">
          {result?.warnings?.length > 0 && <WarningsBanner warnings={result.warnings} className="mb-6" />}
          <Outlet />
        </main>
      </div>
    </div>
  )
}
