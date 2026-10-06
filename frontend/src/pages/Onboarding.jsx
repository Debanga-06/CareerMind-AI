import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { ArrowRight, MapPin, Sparkles, X } from 'lucide-react'
import Button from '../components/ui/Button'
import Card from '../components/ui/Card'
import AnalysisLoadingScreen from '../components/ui/AnalysisLoadingScreen'
import { useAnalysis } from '../hooks/useAnalysis'

const EXPERIENCE_LEVELS = ['Beginner', 'Intermediate', 'Advanced', 'Expert']

const EXAMPLE = {
  target_career: 'AI Engineer',
  skills: ['Python', 'React', 'JavaScript', 'Git'],
  experience_level: 'Beginner',
  location: 'India',
}

function SkillsInput({ skills, onChange }) {
  const [draft, setDraft] = useState('')

  const addSkill = () => {
    const value = draft.trim()
    if (!value) return
    if (!skills.some((s) => s.toLowerCase() === value.toLowerCase())) {
      onChange([...skills, value])
    }
    setDraft('')
  }

  const removeSkill = (skill) => {
    onChange(skills.filter((s) => s !== skill))
  }

  return (
    <div>
      <div className="flex flex-wrap gap-2 rounded-xl border border-line bg-white p-2.5 focus-within:border-ink/30">
        {skills.map((skill) => (
          <span
            key={skill}
            className="inline-flex items-center gap-1 rounded-full bg-ink/5 px-2.5 py-1 text-sm text-ink"
          >
            {skill}
            <button type="button" onClick={() => removeSkill(skill)} aria-label={`Remove ${skill}`}>
              <X className="h-3 w-3 text-muted hover:text-ink" />
            </button>
          </span>
        ))}
        <input
          value={draft}
          onChange={(e) => setDraft(e.target.value)}
          onKeyDown={(e) => {
            if (e.key === 'Enter' || e.key === ',') {
              e.preventDefault()
              addSkill()
            }
            if (e.key === 'Backspace' && !draft && skills.length) {
              removeSkill(skills[skills.length - 1])
            }
          }}
          onBlur={addSkill}
          placeholder={skills.length ? 'Add another…' : 'e.g. Python, then press Enter'}
          className="min-w-[140px] flex-1 bg-transparent px-1.5 py-1 text-sm text-ink outline-none placeholder:text-muted"
        />
      </div>
      <p className="mt-1.5 text-xs text-muted">Press Enter or comma to add each skill.</p>
    </div>
  )
}

export default function Onboarding() {
  const navigate = useNavigate()
  const { runAnalysis, status, error } = useAnalysis()

  const [targetCareer, setTargetCareer] = useState('')
  const [skills, setSkills] = useState([])
  const [experienceLevel, setExperienceLevel] = useState('Beginner')
  const [location, setLocation] = useState('')

  const loading = status === 'loading'

  const fillExample = () => {
    setTargetCareer(EXAMPLE.target_career)
    setSkills(EXAMPLE.skills)
    setExperienceLevel(EXAMPLE.experience_level)
    setLocation(EXAMPLE.location)
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!targetCareer.trim()) return

    try {
      await runAnalysis({
        target_career: targetCareer.trim(),
        skills,
        experience_level: experienceLevel,
        location: location.trim() || undefined,
      })
      navigate('/dashboard')
    } catch {
      // error is already captured in context; surfaced below.
    }
  }

  return (
    <div className="min-h-screen bg-paper py-14">
      <div className="container-page max-w-2xl">
        <p className="text-sm text-muted">Step 1 of 1</p>
        <h1 className="mt-1 font-display text-3xl font-semibold text-ink">Tell us where you're headed</h1>
        <p className="mt-2 text-muted">
          We'll search live job listings for this role and measure your skills against what they
          actually ask for.
        </p>

        <Card className="mt-8 p-6 sm:p-8">
          {loading ? (
            <AnalysisLoadingScreen />
          ) : (
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <div className="flex items-center justify-between">
                <label htmlFor="target_career" className="text-sm font-medium text-ink">
                  Target career
                </label>
                <button
                  type="button"
                  onClick={fillExample}
                  className="inline-flex items-center gap-1 text-xs text-signal-600 hover:text-signal-700"
                >
                  <Sparkles className="h-3 w-3" /> Use example
                </button>
              </div>
              <input
                id="target_career"
                value={targetCareer}
                onChange={(e) => setTargetCareer(e.target.value)}
                placeholder="e.g. AI Engineer"
                required
                className="mt-2 w-full rounded-xl border border-line bg-white px-3.5 py-2.5 text-sm text-ink outline-none focus:border-ink/30"
              />
            </div>

            <div>
              <label className="text-sm font-medium text-ink">Current skills</label>
              <div className="mt-2">
                <SkillsInput skills={skills} onChange={setSkills} />
              </div>
            </div>

            <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
              <div>
                <label htmlFor="experience_level" className="text-sm font-medium text-ink">
                  Experience level
                </label>
                <select
                  id="experience_level"
                  value={experienceLevel}
                  onChange={(e) => setExperienceLevel(e.target.value)}
                  className="mt-2 w-full rounded-xl border border-line bg-white px-3.5 py-2.5 text-sm text-ink outline-none focus:border-ink/30"
                >
                  {EXPERIENCE_LEVELS.map((level) => (
                    <option key={level} value={level}>
                      {level}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label htmlFor="location" className="text-sm font-medium text-ink">
                  Location <span className="font-normal text-muted">(optional)</span>
                </label>
                <div className="relative mt-2">
                  <MapPin className="pointer-events-none absolute left-3.5 top-1/2 h-4 w-4 -translate-y-1/2 text-muted" />
                  <input
                    id="location"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                    placeholder="e.g. India"
                    className="w-full rounded-xl border border-line bg-white py-2.5 pl-10 pr-3.5 text-sm text-ink outline-none focus:border-ink/30"
                  />
                </div>
              </div>
            </div>

            {status === 'error' && (
              <div className="rounded-xl border border-rose-100 bg-rose-50/60 px-4 py-3 text-sm text-rose-600">
                {error?.message || 'Could not run the analysis. Check that the backend is running.'}
              </div>
            )}

            <Button
              type="submit"
              variant="accent"
              size="lg"
              disabled={!targetCareer.trim()}
              icon={ArrowRight}
              iconPosition="right"
              className="w-full"
            >
              Analyze Career
            </Button>
          </form>
          )}
        </Card>
      </div>
    </div>
  )
}
