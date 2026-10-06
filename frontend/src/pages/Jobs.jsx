import { useMemo, useState } from 'react'
import { Search, SlidersHorizontal } from 'lucide-react'
import JobCard from '../components/jobs/JobCard'
import EmptyState from '../components/ui/EmptyState'
import LoadingState from '../components/ui/LoadingState'
import ErrorState from '../components/ui/ErrorState'
import { useAnalysis } from '../hooks/useAnalysis'

const SORTS = [
  { value: 'match', label: 'Best match' },
  { value: 'recent', label: 'Most recent' },
];

function jobMatchesQuery(job, query) {
  if (!query) return true
  const haystack = [job.title, job.company_name, job.location, ...(job.detected_skills || [])]
    .filter(Boolean)
    .join(' ')
    .toLowerCase()
  return haystack.includes(query.toLowerCase())
}

export default function Jobs() {
  const { result, status, error, formValues, runAnalysis } = useAnalysis()
  const [query, setQuery] = useState('')
  const [sort, setSort] = useState('match')

  const jobs = result?.jobs || []

  const filtered = useMemo(() => {
    const list = jobs.filter((j) => jobMatchesQuery(j, query))
    if (sort === 'match') {
      return [...list].sort((a, b) => (b.match_percentage ?? -1) - (a.match_percentage ?? -1))
    }
    return list
  }, [jobs, query, sort])

  if (status === 'loading') {
    return <LoadingState title="Searching live job listings" className="mt-6" />
  }

  if (status === 'error') {
    return <ErrorState description={error?.message} onRetry={formValues ? () => runAnalysis(formValues) : undefined} className="mt-6" />
  }

  if (!result) {
    return (
      <EmptyState
        title="No job matches yet"
        description="Run a career analysis to pull live job listings for your target career."
        actionLabel="Analyze My Career"
        actionTo="/onboarding"
        className="mt-6"
      />
    )
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-2xl font-semibold text-ink sm:text-3xl">Job matches</h1>
        <p className="mt-1 text-sm text-muted">
          {jobs.length} live listing{jobs.length === 1 ? '' : 's'} for {result.career}
        </p>
      </div>

      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
        <div className="relative max-w-sm flex-1">
          <Search className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search title, company, or skill…"
            className="w-full rounded-xl border border-line bg-white py-2.5 pl-10 pr-3.5 text-sm text-ink outline-none focus:border-ink/30"
          />
        </div>
        <div className="flex items-center gap-2">
          <SlidersHorizontal className="h-4 w-4 text-muted" />
          <select
            value={sort}
            onChange={(e) => setSort(e.target.value)}
            className="rounded-xl border border-line bg-white px-3 py-2.5 text-sm text-ink outline-none focus:border-ink/30"
          >
            {SORTS.map((s) => (
              <option key={s.value} value={s.value}>
                {s.label}
              </option>
            ))}
          </select>
        </div>
      </div>

      {filtered.length ? (
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filtered.map((job) => (
            <JobCard key={job.job_id || `${job.title}-${job.company_name}`} job={job} />
          ))}
        </div>
      ) : jobs.length ? (
        <EmptyState title="No matches for that search" description="Try a different keyword or clear the search." />
      ) : (
        <EmptyState
          title="No live listings found"
          description="SerpApi returned no jobs for this search. Try a broader target career or a different location."
        />
      )}
    </div>
  )
}
