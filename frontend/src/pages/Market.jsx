import { Layers, TrendingUp } from 'lucide-react'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import StatCard from '../components/ui/StatCard'
import Badge from '../components/ui/Badge'
import SkillDemandChart from '../components/charts/SkillDemandChart'
import EmptyState from '../components/ui/EmptyState'
import LoadingState from '../components/ui/LoadingState'
import ErrorState from '../components/ui/ErrorState'
import { useAnalysis } from '../hooks/useAnalysis'

export default function Market() {
  const { result, status, error, formValues, runAnalysis } = useAnalysis()

  if (status === 'loading') {
    return <LoadingState title="Analyzing market demand" className="mt-6" />
  }

  if (status === 'error') {
    return <ErrorState description={error?.message} onRetry={formValues ? () => runAnalysis(formValues) : undefined} className="mt-6" />
  }

  if (!result) {
    return (
      <EmptyState
        title="No market data yet"
        description="Run a career analysis to see skill demand across live job listings."
        actionLabel="Analyze My Career"
        actionTo="/onboarding"
        className="mt-6"
      />
    )
  }

  const { career, market } = result
  const skills = market?.skills || []

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink sm:text-3xl">Market intelligence</h1>
        <p className="mt-1 text-sm text-muted">Skill demand for {career}, measured across live listings</p>
      </div>

      <div className="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <StatCard icon={Layers} label="Jobs analyzed" value={market?.sample_size ?? 0} />
        <StatCard icon={TrendingUp} label="Distinct skills found" value={skills.length} tone="signal" />
        <StatCard
          icon={TrendingUp}
          label="Top skill"
          value={skills[0]?.skill || '—'}
          sublabel={skills[0] ? `${skills[0].percentage}% of listings` : undefined}
          tone="amber"
        />
      </div>

      <Card>
        <CardHeader
          title="Skill demand"
          subtitle={`How often each skill appears across ${market?.sample_size ?? 0} analyzed job listings`}
        />
        <CardBody>
          {skills.length ? (
            <SkillDemandChart skills={skills} limit={12} />
          ) : (
            <p className="py-8 text-center text-sm text-muted">No skill data available for this search.</p>
          )}
        </CardBody>
      </Card>

      {skills.length > 0 && (
        <Card>
          <CardHeader title="All detected skills" subtitle="Frequency and share of analyzed listings" />
          <CardBody>
            <div className="overflow-x-auto">
              <table className="w-full min-w-[420px] text-left text-sm">
                <thead>
                  <tr className="border-b border-line text-muted">
                    <th className="py-2 pr-4 font-medium">Skill</th>
                    <th className="py-2 pr-4 font-medium">Listings</th>
                    <th className="py-2 font-medium">Share</th>
                  </tr>
                </thead>
                <tbody>
                  {skills.map((s) => (
                    <tr key={s.skill} className="border-b border-line/60 last:border-0">
                      <td className="py-2.5 pr-4 text-ink">{s.skill}</td>
                      <td className="py-2.5 pr-4 text-muted">{s.frequency}</td>
                      <td className="py-2.5">
                        <Badge variant="neutral">{s.percentage}%</Badge>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </CardBody>
        </Card>
      )}
    </div>
  )
}
