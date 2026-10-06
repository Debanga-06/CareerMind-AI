import { ArrowRight, Search, GitBranch, Briefcase, TrendingUp } from 'lucide-react'
import Button from '../components/ui/Button'
import HeroGraph from '../components/hero/HeroGraph'

const STEPS = [
  {
    icon: Search,
    title: 'We pull live job listings',
    description:
      'Your target career and location are searched against current job postings, not a cached dataset.',
  },
  {
    icon: GitBranch,
    title: 'We read what those jobs actually ask for',
    description:
      'Skills are extracted from real job descriptions and compared against what you already know.',
  },
  {
    icon: TrendingUp,
    title: 'You see the gap and the path through it',
    description:
      'Strong skills, skills worth developing, and the highest-priority gaps to close first — all from the same sample of listings.',
  },
]

export default function Landing() {
  return (
    <>
      {/* Hero */}
      <section className="container-page grid grid-cols-1 items-center gap-12 pb-20 pt-16 lg:grid-cols-2 lg:pt-24">
        <div className="animate-fade-up">
          <h1 className="font-display text-4xl font-semibold leading-[1.1] tracking-tight text-ink sm:text-5xl">
            See where the market is going.
            <br />
            Discover where you stand.
          </h1>
          <p className="mt-5 max-w-lg text-lg text-muted">
            Build the path to get there. CareerGraph AI reads live job listings for the role you
            want, measures your skill gap against them, and shows exactly what to work on next.
          </p>
          <div className="mt-8 flex flex-col gap-3 sm:flex-row">
            <Button size="lg" variant="accent" to="/onboarding" icon={ArrowRight} iconPosition="right">
              Analyze My Career
            </Button>
            <Button size="lg" variant="outline" to="/market">
              Explore Market
            </Button>
          </div>
          <p className="mt-6 text-sm text-muted">
            Live search across current job postings — no invented statistics, no guessed hiring odds.
          </p>
        </div>

        <div className="flex justify-center lg:justify-end">
          <HeroGraph className="w-full max-w-md" />
        </div>
      </section>

      {/* How it works */}
      <section id="how-it-works" className="border-t border-line bg-white py-20">
        <div className="container-page">
          <h2 className="font-display text-2xl font-semibold text-ink sm:text-3xl">How an analysis works</h2>
          <p className="mt-2 max-w-xl text-muted">
            Three steps, all run against real data pulled the moment you ask for it.
          </p>

          <div className="mt-12 grid grid-cols-1 gap-8 md:grid-cols-3">
            {STEPS.map((step, i) => (
              <div key={step.title} className="relative">
                <div className="flex items-center gap-3">
                  <span className="flex h-10 w-10 shrink-0 items-center justify-center rounded-xl bg-ink text-white">
                    <step.icon className="h-5 w-5" strokeWidth={1.75} />
                  </span>
                  <span className="font-display text-sm text-muted">Step {i + 1}</span>
                </div>
                <h3 className="mt-4 font-display text-lg font-semibold text-ink">{step.title}</h3>
                <p className="mt-1.5 text-sm text-muted">{step.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Market data */}
      <section id="market-data" className="py-20">
        <div className="container-page grid grid-cols-1 items-center gap-12 lg:grid-cols-2">
          <div>
            <h2 className="font-display text-2xl font-semibold text-ink sm:text-3xl">
              Built on job postings, not assumptions
            </h2>
            <p className="mt-4 text-muted">
              Every analysis searches Google Jobs for your target role, so the skills, sample size, and
              match percentages you see come from listings that exist right now — not a model's memory
              of what a role "usually" needs.
            </p>
            <ul className="mt-6 space-y-3 text-sm text-ink">
              <li className="flex items-start gap-2.5">
                <Briefcase className="mt-0.5 h-4 w-4 shrink-0 text-signal-500" />
                Job details link straight through to the original posting to apply.
              </li>
              <li className="flex items-start gap-2.5">
                <TrendingUp className="mt-0.5 h-4 w-4 shrink-0 text-signal-500" />
                Skill demand is shown as a plain frequency — how many of the analyzed jobs mention it.
              </li>
              <li className="flex items-start gap-2.5">
                <GitBranch className="mt-0.5 h-4 w-4 shrink-0 text-signal-500" />
                We never claim to predict whether you'll get hired — only where the gaps are.
              </li>
            </ul>
          </div>
          <div className="rounded-2xl border border-line bg-white p-8 shadow-card">
            <p className="font-display text-sm font-semibold text-ink">A typical analysis returns</p>
            <div className="mt-5 space-y-4 text-sm text-muted">
              <div className="flex items-center justify-between border-b border-line pb-3">
                <span>Sample of current listings</span>
                <span className="font-display font-semibold text-ink">real-time</span>
              </div>
              <div className="flex items-center justify-between border-b border-line pb-3">
                <span>Skill frequency across those listings</span>
                <span className="font-display font-semibold text-ink">measured</span>
              </div>
              <div className="flex items-center justify-between border-b border-line pb-3">
                <span>Your skill gap vs. the market</span>
                <span className="font-display font-semibold text-ink">scored</span>
              </div>
              <div className="flex items-center justify-between">
                <span>Per-job match percentage</span>
                <span className="font-display font-semibold text-ink">calculated</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Closing CTA */}
      <section className="border-t border-line bg-ink py-20">
        <div className="container-page flex flex-col items-start justify-between gap-6 sm:flex-row sm:items-center">
          <div>
            <h2 className="font-display text-2xl font-semibold text-white sm:text-3xl">
              Ready to see your gap?
            </h2>
            <p className="mt-2 max-w-md text-white/60">
              Tell us your target career, current skills, and location — get a live read on the
              market in under a minute.
            </p>
          </div>
          <Button size="lg" variant="accent" to="/onboarding" icon={ArrowRight} iconPosition="right">
            Analyze My Career
          </Button>
        </div>
      </section>
    </>
  )
}
