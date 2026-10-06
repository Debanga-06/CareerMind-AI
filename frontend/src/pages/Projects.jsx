import { FolderKanban } from 'lucide-react'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import Badge from '../components/ui/Badge'
import EmptyState from '../components/ui/EmptyState'
import LoadingState from '../components/ui/LoadingState'
import ErrorState from '../components/ui/ErrorState'
import { useAnalysis } from '../hooks/useAnalysis'

const DIFFICULTY_VARIANT = {
  Beginner: 'strong',
  Intermediate: 'develop',
  Advanced: 'missing',
}

export default function Projects() {
  const { result, status, error, formValues, runAnalysis } = useAnalysis()

  if (status === 'loading') {
    return <LoadingState title="Finding project ideas" className="mt-6" />
  }

  if (status === 'error') {
    return <ErrorState description={error?.message} onRetry={formValues ? () => runAnalysis(formValues) : undefined} className="mt-6" />
  }

  if (!result) {
    return (
      <EmptyState
        title="No analysis yet"
        description="Run a career analysis first, then come back here for project ideas."
        actionLabel="Analyze My Career"
        actionTo="/onboarding"
        className="mt-6"
      />
    )
  }

  const projects = result.projects || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink sm:text-3xl">Recommended projects</h1>
        <p className="mt-1 text-sm text-muted">Portfolio ideas built around your skill gap for {result.career}</p>
      </div>

      {projects.length ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
          {projects.map((project) => (
            <Card key={project.title}>
              <CardHeader
                title={project.title}
                action={
                  project.difficulty && (
                    <Badge variant={DIFFICULTY_VARIANT[project.difficulty] || 'neutral'}>{project.difficulty}</Badge>
                  )
                }
              />
              <CardBody>
                <p className="text-sm text-muted">{project.description}</p>
                {project.skills_used?.length > 0 && (
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {project.skills_used.map((s) => (
                      <Badge key={s} variant="neutral">
                        {s}
                      </Badge>
                    ))}
                  </div>
                )}
              </CardBody>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState
          icon={FolderKanban}
          title="No project recommendations yet"
          description="Project ideas aren't wired up in this build yet — this page will fill in automatically once they are, using your skill gap from this analysis."
        />
      )}
    </div>
  )
}
