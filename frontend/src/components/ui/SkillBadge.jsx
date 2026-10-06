import Badge from './Badge'

const VARIANT_BY_CATEGORY = {
  strong: 'strong',
  develop: 'develop',
  missing: 'missing',
  priority: 'priority',
  matched: 'strong',
  gap: 'missing',
  neutral: 'neutral',
}

/** A skill name rendered as a Badge, colored by its skill-gap category. */
export default function SkillBadge({ skill, category = 'neutral', className = '' }) {
  return (
    <Badge variant={VARIANT_BY_CATEGORY[category] || 'neutral'} className={className}>
      {skill}
    </Badge>
  )
}
