import { Link } from 'react-router-dom'
import { Target, TrendingUp, Layers, ArrowRight, Map, FolderKanban, Flag } from 'lucide-react'
import Card, { CardHeader, CardBody } from '../components/ui/Card'
import StatCard from '../components/ui/StatCard'
import Badge from '../components/ui/Badge'
import SkillBadge from '../components/ui/SkillBadge'
import JobCard from '../components/jobs/JobCard'
import EmptyState from '../components/ui/EmptyState'
import LoadingState from '../components/ui/LoadingState'
import ErrorState from '../components/ui/ErrorState'
import Button from '../components/ui/Button'
import { useAnalysis } from '../hooks/useAnalysis'

export default function Dashboard() {
  const { result, status, error, formValues, runAnalysis } = useAnalysis()

  if (status === 'loading') {
    return <LoadingState title="Running your analysis" description="Searching live job listings and scoring your skill gap…" className="mt-6" />
  }

  if (status === 'error') {
    return (
      <ErrorState
        description={error?.message}
        onRetry={formValues ? () => runAnalysis(formValues) : undefined}
        className="mt-6"
      />
    )
  }

  if (!result) {
    return (
      <EmptyState
        title="No analysis yet"
        description="Run a career analysis to see market data, your skill gap, and job matches here."
        actionLabel="Analyze My Career"
        actionTo="/onboarding"
        className="mt-6"
      />
    )
  }

  const { career, market, skill_gap: skillGap, jobs = [], roadmap, projects = [] } = result
  const topJobs = [...jobs].sort((a, b) => (b.match_percentage ?? -1) - (a.match_percentage ?? -1)).slice(0, 3)

  return (
    <div className="space-y-8">
      <div>
        <p className="text-sm text-muted">Analysis for</p>
        <h1 className="font-display text-2xl font-semibold text-ink sm:text-3xl">{career}</h1>
      </div>

      <div className="grid grid-cols-2 gap-4 lg:grid-cols-4">
        <StatCard icon={Flag} label="Career" value={career} tone="ink" />
        <StatCard icon={Layers} label="Jobs analyzed" value={market?.sample_size ?? 0} tone="ink" />
        <StatCard
          icon={TrendingUp}
          label="Top market skill"
          value={market?.skills?.[0]?.skill ?? '—'}
          sublabel={market?.skills?.[0] ? `${market.skills[0].percentage}% of listings` : 'No skill data'}
          tone="signal"
        />
        <StatCard
          icon={Target}
          label="Priority skills"
          value={skillGap?.priority_skills?.length ?? 0}
          sublabel={skillGap?.priority_skills?.length ? skillGap.priority_skills.slice(0, 3).join(', ') : 'None identified'}
          tone="amber"
        />
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
        {/* Market overview */}
        <Card className="lg:col-span-2">
          <CardHeader title="Market overview" subtitle={`Top skills across ${market?.sample_size ?? 0} listings`} action={
            <Link to="/market" className="text-sm text-signal-600 hover:text-signal-700 inline-flex items-center gap-1">
              View all <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          } />
          <CardBody>
            {market?.skills?.length ? (
              <ul className="space-y-3">
                {market.skills.slice(0, 5).map((s) => (
                  <li key={s.skill} className="flex items-center gap-3">
                    <span className="w-28 shrink-0 truncate text-sm text-ink">{s.skill}</span>
                    <div className="h-2 flex-1 overflow-hidden rounded-full bg-ink/5">
                      <div className="h-full rounded-full bg-signal-500" style={{ width: `${s.percentage}%` }} />
                    </div>
                    <span className="w-12 shrink-0 text-right text-sm text-muted">{s.percentage}%</span>
                  </li>
                ))}
              </ul>
            ) : (
              <p className="text-sm text-muted">No skill data available for this search.</p>
            )}
          </CardBody>
        </Card>

        {/* Skill gap summary */}
        <Card>
          <CardHeader title="Skill gap" subtitle="Your skills vs. the market" action={
            <Link to="/skill-gap" className="text-sm text-signal-600 hover:text-signal-700 inline-flex items-center gap-1">
              Details <ArrowRight className="h-3.5 w-3.5" />
            </Link>
          } />
          <CardBody className="space-y-4">
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">Strong</span>
              <Badge variant="strong">{skillGap?.strong_skills?.length ?? 0}</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">Develop</span>
              <Badge variant="develop">{skillGap?.develop_skills?.length ?? 0}</Badge>
            </div>
            <div className="flex items-center justify-between text-sm">
              <span className="text-muted">Missing</span>
              <Badge variant="missing">{skillGap?.missing_skills?.length ?? 0}</Badge>
            </div>
            {skillGap?.priority_skills?.length > 0 && (
              <div className="border-t border-line pt-3">
                <p className="mb-2 text-xs text-muted">Top priority</p>
                <div className="flex flex-wrap gap-1.5">
                  {skillGap.priority_skills.slice(0, 4).map((s) => (
                    <SkillBadge key={s} skill={s} category="priority" />
                  ))}
                </div>
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Job matches */}
      <div>
        <div className="mb-4 flex items-center justify-between">
          <h2 className="font-display text-lg font-semibold text-ink">Top job matches</h2>
          <Link to="/jobs" className="text-sm text-signal-600 hover:text-signal-700 inline-flex items-center gap-1">
            View all {jobs.length} <ArrowRight className="h-3.5 w-3.5" />
          </Link>
        </div>
        {topJobs.length ? (
          <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
            {topJobs.map((job) => (
              <JobCard key={job.job_id || job.title} job={job} />
            ))}
          </div>
        ) : (
          <EmptyState title="No jobs found" description="No live listings came back for this search. Try a broader target career or location." />
        )}
      </div>

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <Card>
          <CardHeader title="Career roadmap" subtitle="Your suggested learning path" action={<Map className="h-4 w-4 text-muted" />} />
          <CardBody>
            {roadmap ? (
              <p className="text-sm text-ink">{roadmap.summary}</p>
            ) : (
              <EmptyState
                title="No roadmap yet"
                description="Personalized roadmap data isn't available yet."
                actionLabel="View roadmap page"
                actionTo="/roadmap"
              />
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Recommended projects" subtitle="Build something to prove it" action={<FolderKanban className="h-4 w-4 text-muted" />} />
          <CardBody>
            {projects?.length ? (
              <ul className="space-y-2">
                {projects.slice(0, 3).map((p) => (
                  <li key={p.title} className="text-sm text-ink">
                    {p.title}
                  </li>
                ))}
              </ul>
            ) : (
              <EmptyState
                title="No projects yet"
                description="Personalized project recommendations aren't available yet."
                actionLabel="View projects page"
                actionTo="/projects"
              />
            )}
          </CardBody>
        </Card>
      </div>

      <div className="flex justify-center pt-2">
        <Button variant="outline" to="/onboarding">
          Run a new analysis
        </Button>
      </div>
    </div>
  )
}
