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
  Brush,
} from 'recharts'

function fmtTime(ms) {
  try {
    const d = new Date(ms)
    return d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  } catch {
    return ''
  }
}

export default function MetricSeriesChart({ metrics, changePoints }) {
  const data = useMemo(() => {
    const arr = Array.isArray(metrics) ? metrics : []
    return arr
      .map((m, idx) => {
        const t = typeof m.timestamp === 'string' ? Date.parse(m.timestamp) : NaN
        return { idx, t, v: Number(m.value) }
      })
      .filter((d) => Number.isFinite(d.t) && Number.isFinite(d.v))
  }, [metrics])

  const cpLines = useMemo(() => {
    const cps = Array.isArray(changePoints) ? changePoints : []
    const points = []
    for (const cp of cps) {
      const row = data[cp]
      if (row) points.push({ cp, t: row.t })
    }
    return points
  }, [changePoints, data])

  return (
    <div className="h-80 w-full">
      <ResponsiveContainer>
        <LineChart data={data} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis
            dataKey="t"
            type="number"
            domain={['auto', 'auto']}
            tickFormatter={fmtTime}
            tick={{ fontSize: 12 }}
          />
          <YAxis tick={{ fontSize: 12 }} />
          <Tooltip
            labelFormatter={(label) => {
              const ms = Number(label)
              return Number.isFinite(ms) ? new Date(ms).toLocaleString() : String(label)
            }}
            formatter={(value) => [Number(value).toFixed(4), 'value']}
          />

          <Line type="monotone" dataKey="v" stroke="#0f172a" dot={false} strokeWidth={2} />

          {cpLines.map((l) => (
            <ReferenceLine key={l.cp} x={l.t} stroke="#7c3aed" strokeWidth={2} />
          ))}

          <Brush
            dataKey="t"
            height={24}
            stroke="#0f172a"
            travellerWidth={10}
            tickFormatter={fmtTime}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
