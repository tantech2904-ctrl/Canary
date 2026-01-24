import React, { useMemo } from 'react'
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
  Area,
} from 'recharts'

function formatPct(x) {
  if (typeof x !== 'number') return ''
  return `${Math.round(x * 100)}%`
}

export default function PosteriorChart({ probabilities, changePoints, thresholds = [0.8, 0.9] }) {
  const data = useMemo(() => {
    const probs = Array.isArray(probabilities) ? probabilities : []
    return probs.map((p, idx) => ({ t: idx, p }))
  }, [probabilities])

  return (
    <div className="h-72 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="t" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 1]} tickFormatter={formatPct} tick={{ fontSize: 12 }} />
          <Tooltip
            formatter={(value) => formatPct(value)}
            labelFormatter={(label) => `t=${label}`}
          />

          <Area type="monotone" dataKey="p" stroke="none" fill="#94a3b8" fillOpacity={0.18} />
          <Line type="monotone" dataKey="p" stroke="#0f172a" dot={false} strokeWidth={2} />

          {thresholds.map((thr) => (
            <ReferenceLine
              key={thr}
              y={thr}
              stroke={thr >= 0.9 ? '#be123c' : '#b45309'}
              strokeDasharray="6 6"
            />
          ))}

          {(changePoints || []).map((cp) => (
            <ReferenceLine key={cp} x={cp} stroke="#7c3aed" strokeWidth={2} />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
