import React, { useMemo } from 'react'
import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  ReferenceLine,
} from 'recharts'

function formatPct(x) {
  if (typeof x !== 'number') return ''
  return `${Math.round(x * 100)}%`
}

export default function ChangePointPosteriorChart({ cpPosterior }) {
  const data = useMemo(() => {
    const arr = Array.isArray(cpPosterior) ? cpPosterior : []
    return arr.map((p, idx) => ({ t: idx, p }))
  }, [cpPosterior])

  return (
    <div className="h-60 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="t" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 'auto']} tickFormatter={formatPct} tick={{ fontSize: 12 }} />
          <Tooltip formatter={(value) => formatPct(value)} labelFormatter={(label) => `t=${label}`} />
          <ReferenceLine y={0} stroke="#94a3b8" />
          <Bar dataKey="p" fill="#2563eb" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
