import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts'

const BAR_COLOR = '#00B37E'
const BAR_COLOR_MUTED = '#0B1220'

function ChartTooltip({ active, payload }) {
  if (!active || !payload?.length) return null
  const { skill, frequency, percentage } = payload[0].payload
  return (
    <div className="rounded-lg border border-line bg-white px-3 py-2 text-xs shadow-card">
      <p className="font-medium text-ink">{skill}</p>
      <p className="mt-0.5 text-muted">
        {percentage}% of jobs · {frequency} listing{frequency === 1 ? '' : 's'}
      </p>
    </div>
  )
}

/** Horizontal bar chart of skill demand percentages. `skills` = MarketAnalysis.skills. */
export default function SkillDemandChart({ skills = [], limit = 10, height = 360 }) {
  const data = skills.slice(0, limit).map((s) => ({ ...s, name: s.skill }))

  return (
    <ResponsiveContainer width="100%" height={height}>
      <BarChart data={data} layout="vertical" margin={{ top: 4, right: 24, bottom: 4, left: 4 }}>
        <XAxis type="number" domain={[0, 100]} tickFormatter={(v) => `${v}%`} tick={{ fontSize: 12, fill: '#5B6472' }} axisLine={false} tickLine={false} />
        <YAxis
          type="category"
          dataKey="skill"
          width={120}
          tick={{ fontSize: 12, fill: '#0B1220' }}
          axisLine={false}
          tickLine={false}
        />
        <Tooltip cursor={{ fill: 'rgba(11,18,32,0.04)' }} content={<ChartTooltip />} />
        <Bar dataKey="percentage" radius={[0, 6, 6, 0]} barSize={16}>
          {data.map((entry, index) => (
            <Cell key={entry.skill} fill={index === 0 ? BAR_COLOR : BAR_COLOR_MUTED} fillOpacity={index === 0 ? 1 : 0.16 + (0.5 * (data.length - index)) / data.length} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  )
}
