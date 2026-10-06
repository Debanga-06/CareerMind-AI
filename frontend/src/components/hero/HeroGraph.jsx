// A decorative node-graph illustration -- the literal "graph" in
// CareerGraph AI. Skill nodes connect to a role node; one path lights up
// and draws in on load, standing in for "the path to get there."
// Purely illustrative brand art -- not a rendering of real API data.

const NODES = [
  { id: 'python', x: 40, y: 60, r: 15, label: 'Python' },
  { id: 'react', x: 40, y: 200, r: 13, label: 'React' },
  { id: 'sql', x: 40, y: 320, r: 12, label: 'SQL' },
  { id: 'docker', x: 220, y: 40, r: 12, label: 'Docker' },
  { id: 'ml', x: 230, y: 150, r: 16, label: 'ML' },
  { id: 'cloud', x: 220, y: 280, r: 12, label: 'Cloud' },
  { id: 'role', x: 400, y: 160, r: 22, label: 'AI Engineer' },
]

const EDGES = [
  ['python', 'ml'],
  ['python', 'docker'],
  ['react', 'ml'],
  ['sql', 'cloud'],
  ['docker', 'role'],
  ['ml', 'role'],
  ['cloud', 'role'],
]

const HIGHLIGHT_PATH = ['python', 'ml', 'role']

function nodeById(id) {
  return NODES.find((n) => n.id === id)
}

export default function HeroGraph({ className = '' }) {
  const highlightPoints = HIGHLIGHT_PATH.map((id) => nodeById(id))
  const highlightD = highlightPoints.map((p, i) => `${i === 0 ? 'M' : 'L'} ${p.x} ${p.y}`).join(' ')

  return (
    <svg viewBox="0 0 440 360" className={className} role="img" aria-label="Illustration of a skill graph connecting to a target career">
      {EDGES.map(([a, b]) => {
        const from = nodeById(a)
        const to = nodeById(b)
        return (
          <line
            key={`${a}-${b}`}
            x1={from.x}
            y1={from.y}
            x2={to.x}
            y2={to.y}
            stroke="#E4E7EC"
            strokeWidth="1.5"
          />
        )
      })}

      <path
        d={highlightD}
        fill="none"
        stroke="#00B37E"
        strokeWidth="2.5"
        strokeLinecap="round"
        strokeDasharray="1000"
        strokeDashoffset="1000"
        className="animate-draw-line"
      />

      {NODES.map((n) => {
        const isRole = n.id === 'role'
        const isOnPath = HIGHLIGHT_PATH.includes(n.id)
        return (
          <g key={n.id}>
            <circle
              cx={n.x}
              cy={n.y}
              r={n.r}
              fill={isRole ? '#0B1220' : isOnPath ? '#00B37E' : '#FFFFFF'}
              stroke={isOnPath || isRole ? 'transparent' : '#E4E7EC'}
              strokeWidth="1.5"
            />
            <text
              x={n.x}
              y={n.y + n.r + 16}
              textAnchor="middle"
              className="fill-ink"
              style={{ fontSize: 11, fontFamily: 'Inter, sans-serif', fontWeight: isRole ? 600 : 500 }}
            >
              {n.label}
            </text>
          </g>
        )
      })}
    </svg>
  )
}
