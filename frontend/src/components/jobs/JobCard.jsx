import { Building2, MapPin, Clock, ExternalLink, Globe2 } from 'lucide-react'
import Card from '../ui/Card'
import Badge from '../ui/Badge'
import SkillBadge from '../ui/SkillBadge'
import MatchMeter from '../ui/MatchMeter'
import Button from '../ui/Button'

export default function JobCard({ job }) {
  const {
    title,
    company_name,
    location,
    via,
    posted_at,
    apply_link,
    detected_skills = [],
    match_percentage,
    matched_skills = [],
    missing_skills = [],
    match_note,
  } = job

  return (
    <Card className="flex flex-col p-5">
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0">
          <h3 className="font-display text-base font-semibold text-ink leading-snug">{title || 'Untitled role'}</h3>
          <div className="mt-1.5 flex flex-wrap items-center gap-x-3 gap-y-1 text-sm text-muted">
            {company_name && (
              <span className="inline-flex items-center gap-1">
                <Building2 className="h-3.5 w-3.5" /> {company_name}
              </span>
            )}
            {location && (
              <span className="inline-flex items-center gap-1">
                <MapPin className="h-3.5 w-3.5" /> {location}
              </span>
            )}
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-x-3 gap-y-1 text-xs text-muted">
            {via && (
              <span className="inline-flex items-center gap-1">
                <Globe2 className="h-3 w-3" /> {via}
              </span>
            )}
            {posted_at && (
              <span className="inline-flex items-center gap-1">
                <Clock className="h-3 w-3" /> {posted_at}
              </span>
            )}
          </div>
        </div>
        <div className="w-24 shrink-0">
          <MatchMeter percentage={match_percentage} note={match_note} />
        </div>
      </div>

      {(matched_skills.length > 0 || missing_skills.length > 0) && (
        <div className="mt-4 space-y-2">
          {matched_skills.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {matched_skills.map((s) => (
                <SkillBadge key={`m-${s}`} skill={s} category="strong" />
              ))}
            </div>
          )}
          {missing_skills.length > 0 && (
            <div className="flex flex-wrap gap-1.5">
              {missing_skills.map((s) => (
                <SkillBadge key={`x-${s}`} skill={s} category="missing" />
              ))}
            </div>
          )}
        </div>
      )}

      {matched_skills.length === 0 && missing_skills.length === 0 && (
        <div className="mt-4">
          {detected_skills.length > 0 ? (
            <div className="flex flex-wrap gap-1.5">
              {detected_skills.slice(0, 6).map((s) => (
                <Badge key={s} variant="neutral">
                  {s}
                </Badge>
              ))}
            </div>
          ) : (
            <p className="text-xs text-muted">Skills could not be reliably detected for this listing.</p>
          )}
        </div>
      )}

      <div className="mt-5 flex items-center justify-between border-t border-line pt-4">
        <span className="text-xs text-muted">{via ? `via ${via.replace(/^via\s+/i, '')}` : 'Source listed on apply'}</span>
        {apply_link ? (
          <Button size="sm" variant="outline" href={apply_link} target="_blank" rel="noopener noreferrer" icon={ExternalLink} iconPosition="right">
            Apply
          </Button>
        ) : (
          <span className="text-xs text-muted">No apply link</span>
        )}
      </div>
    </Card>
  )
}
