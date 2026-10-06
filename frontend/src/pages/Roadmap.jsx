import { Map, Clock, ExternalLink, BookOpen } from 'lucide-react'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import EmptyState from '../components/ui/EmptyState'
import LoadingState from '../components/ui/LoadingState'
import ErrorState from '../components/ui/ErrorState'
import { useAnalysis } from '../hooks/useAnalysis'

export default function Roadmap() {
  const { result, status, error, formValues, runAnalysis } = useAnalysis()

  if (status === 'loading') {
    return <LoadingState title="Building your roadmap" className="mt-6" />
  }

  if (status === 'error') {
    return <ErrorState description={error?.message} onRetry={formValues ? () => runAnalysis(formValues) : undefined} className="mt-6" />
  }

  if (!result) {
    return (
      <EmptyState
        title="No analysis yet"
        description="Run a career analysis first, then come back here for your roadmap."
        actionLabel="Analyze My Career"
        actionTo="/onboarding"
        className="mt-6"
      />
    )
  }

  const roadmap = result.roadmap
  const resources = result.resources || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink sm:text-3xl">Career roadmap</h1>
        <p className="mt-1 text-sm text-muted">A phased learning path toward {result.career}</p>
      </div>

      {roadmap && roadmap.phases?.length ? (
        <div className="space-y-4">
          {roadmap.summary && (
            <Card>
              <CardBody className="text-sm text-ink">{roadmap.summary}</CardBody>
            </Card>
          )}
          {roadmap.phases.map((phase) => (
            <Card key={phase.phase_number}>
              <CardHeader
                title={phase.title}
                subtitle={phase.description}
                action={
                  phase.duration_weeks && (
                    <Badge variant="neutral" icon={Clock}>
                      {phase.duration_weeks} wk
                    </Badge>
                  )
                }
              />
              {phase.focus_skills?.length > 0 && (
                <CardBody>
                  <div className="flex flex-wrap gap-1.5">
                    {phase.focus_skills.map((s) => (
                      <Badge key={s} variant="develop">
                        {s}
                      </Badge>
                    ))}
                  </div>
                </CardBody>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={Map}
          title="Your personalized roadmap will appear here after analysis."
          description="Roadmap generation isn't wired up in this build yet — this page will fill in automatically once it is, using your skill gap from this analysis."
        />
      )}

      <Card>
        <CardHeader title="Resources" subtitle="Learning links for your priority skills" action={<BookOpen className="h-4 w-4 text-muted" />} />
        <CardBody>
          {resources.length ? (
            <ul className="space-y-3">
              {resources.map((r, i) => (
                <li key={i} className="flex items-start justify-between gap-3 border-b border-line pb-3 last:border-0 last:pb-0">
                  <div className="min-w-0">
                    <p className="truncate text-sm font-medium text-ink">{r.title}</p>
                    <p className="mt-0.5 text-xs text-muted">
                      {r.skill}
                      {r.source ? ` · ${r.source}` : ''}
                    </p>
                  </div>
                  <a
                    href={r.link}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="inline-flex shrink-0 items-center gap-1 text-xs text-signal-600 hover:text-signal-700"
                  >
                    Open <ExternalLink className="h-3 w-3" />
                  </a>
                </li>
              ))}
            </ul>
          ) : (
            <p className="text-sm text-muted">Resource links aren't available yet.</p>
          )}
        </CardBody>
      </Card>
    </div>
  )
}
