import { Compass } from 'lucide-react'
import Button from '../components/ui/Button'

export default function NotFound() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-paper px-6 text-center">
      <div className="flex h-14 w-14 items-center justify-center rounded-full bg-ink/5">
        <Compass className="h-7 w-7 text-muted" strokeWidth={1.75} />
      </div>
      <h1 className="mt-5 font-display text-2xl font-semibold text-ink">Page not found</h1>
      <p className="mt-2 max-w-sm text-sm text-muted">
        That route doesn't exist. Head back to the homepage or start a new analysis.
      </p>
      <div className="mt-6 flex gap-3">
        <Button variant="outline" to="/">
          Home
        </Button>
        <Button variant="accent" to="/onboarding">
          Analyze My Career
        </Button>
      </div>
    </div>
  )
}
