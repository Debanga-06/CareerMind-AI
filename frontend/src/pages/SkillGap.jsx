import { ShieldCheck } from 'lucide-react'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import SkillBadge from '../components/ui/SkillBadge'
import EmptyState from '../components/ui/EmptyState'
import LoadingState from '../components/ui/LoadingState'
import ErrorState from '../components/ui/ErrorState'
import { SKILL_GAP_CATEGORIES } from '../lib/skillMeta'
import { useAnalysis } from '../hooks/useAnalysis'

export default function SkillGap() {
  const { result, status, error, formValues, runAnalysis } = useAnalysis()

  if (status === 'loading') {
    return <LoadingState title="Scoring your skill gap" className="mt-6" />
  }

  if (status === 'error') {
    return <ErrorState description={error?.message} onRetry={formValues ? () => runAnalysis(formValues) : undefined} className="mt-6" />
  }

  if (!result) {
    return (
      <EmptyState
        title="No skill gap yet"
        description="Run a career analysis to compare your skills against the current market."
        actionLabel="Analyze My Career"
        actionTo="/onboarding"
        className="mt-6"
      />
    )
  }

  const { skill_gap: skillGap, career } = result

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink sm:text-3xl">Skill gap</h1>
        <p className="mt-1 text-sm text-muted">Your skills measured against live listings for {career}</p>
      </div>

      <div className="grid grid-cols-1 gap-4 sm:grid-cols-2">
        {SKILL_GAP_CATEGORIES.map((category) => {
          const items = skillGap?.[category.key] || []
          return (
            <Card key={category.key}>
              <CardHeader title={category.label} subtitle={category.description} />
              <CardBody>
                {items.length ? (
                  <div className="flex flex-wrap gap-1.5">
                    {items.map((s) => (
                      <SkillBadge key={s} skill={s} category={category.variant} />
                    ))}
                  </div>
                ) : (
                  <p className="text-sm text-muted">None in this category for this search.</p>
                )}
              </CardBody>
            </Card>
          )
        })}
      </div>

      <Card accent="signal">
        <CardHeader title="How this is scored" action={<ShieldCheck className="h-4 w-4 text-signal-500" />} />
        <CardBody className="space-y-3 text-sm text-muted">
          <p>
            Every market skill detected across the analyzed job listings is compared, by name, against
            your stated skills.
          </p>
          <ul className="list-disc space-y-1.5 pl-5">
            <li>
              <span className="font-medium text-ink">Strong</span> — a market skill you already listed.
            </li>
            <li>
              <span className="font-medium text-ink">Missing</span> — a market skill you don't have, appearing
              in 30% or more of the analyzed listings.
            </li>
            <li>
              <span className="font-medium text-ink">Develop</span> — a market skill you don't have, appearing
              in 10–30% of listings.
            </li>
            <li>
              <span className="font-medium text-ink">Priority</span> — the highest-demand skills from your
              missing list, worth learning first.
            </li>
          </ul>
          {skillGap?.scoring_note && (
            <p className="border-t border-line pt-3 text-ink">{skillGap.scoring_note}</p>
          )}
          <p className="italic">
            This reflects overlap with a sample of current listings — it is not a prediction of whether
            you'll be hired.
          </p>
        </CardBody>
      </Card>
    </div>
  )
}
