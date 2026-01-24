import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import AppShell from '../components/layout/AppShell'
import { Card } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Badge } from '../components/ui/badge'
import PosteriorChart from '../components/charts/PosteriorChart'
import ChangePointPosteriorChart from '../components/charts/ChangePointPosteriorChart'
import MetricSeriesChart from '../components/charts/MetricSeriesChart'
import { fetchAnalysis, fetchPosterior } from '../api/analysis'
import { fetchRunMetrics } from '../api/metrics'
import { fetchMitigations, approveMitigation } from '../api/mitigations'
import { fetchAuditLogs } from '../api/audit'
import { useAuth } from '../hooks/useAuth.jsx'

export default function RunDetailsPage() {
  const { runId } = useParams()
  const { hasRole } = useAuth()

  const [analysis, setAnalysis] = useState(null)
  const [posterior, setPosterior] = useState(null)
  const [mitigations, setMitigations] = useState([])
  const [metrics, setMetrics] = useState([])
  const [auditEvents, setAuditEvents] = useState([])
  const [auditError, setAuditError] = useState('')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const canApprove = hasRole('analyst')
  const canViewAudit = hasRole('analyst')

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    setAuditError('')
    try {
      const paramsRunId = Number(runId)
      const runIdForAudit = Number.isFinite(paramsRunId) ? paramsRunId : undefined

      const auditPromise = canViewAudit && runIdForAudit ? fetchAuditLogs({ run_id: runIdForAudit, limit: 10 }) : []

      const [a, p, m, series, audit] = await Promise.all([
        fetchAnalysis(runId),
        fetchPosterior(runId),
        fetchMitigations(runId),
        fetchRunMetrics(runId, 5000),
        auditPromise,
      ])
      setAnalysis(a)
      setPosterior(p)
      setMitigations(m)
      setMetrics(series)
      setAuditEvents(Array.isArray(audit) ? audit : [])
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load run analysis')
    } finally {
      setLoading(false)
    }
  }, [canViewAudit, runId])

  const loadAuditOnly = useCallback(async () => {
    if (!canViewAudit) return
    const paramsRunId = Number(runId)
    if (!Number.isFinite(paramsRunId)) return

    setAuditError('')
    try {
      const audit = await fetchAuditLogs({ run_id: paramsRunId, limit: 10 })
      setAuditEvents(Array.isArray(audit) ? audit : [])
    } catch (err) {
      setAuditError(err?.response?.data?.detail || 'Failed to load audit events')
    }
  }, [canViewAudit, runId])

  useEffect(() => {
    load()
  }, [load])

  const headline = useMemo(() => {
    const maxP = Math.max(0, ...(analysis?.probabilities || []))
    if (maxP >= 0.9) return { label: 'High regime-shift probability', variant: 'danger' }
    if (maxP >= 0.8) return { label: 'Elevated regime-shift probability', variant: 'warning' }
    return { label: 'No strong regime-shift signal', variant: 'success' }
  }, [analysis])

  return (
    <AppShell title={`Run #${runId}`}> 
      <div className="mb-4 flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Badge variant={headline.variant}>{headline.label}</Badge>
        </div>
        <div className="flex items-center gap-2">
          {canViewAudit ? (
            <Link to={`/audit?run_id=${encodeURIComponent(runId)}`}>
              <Button variant="secondary">View audit</Button>
            </Link>
          ) : null}
          <Button variant="secondary" onClick={load}>
            Refresh
          </Button>
        </div>
      </div>

      {error ? <div className="mb-4 rounded bg-rose-50 p-3 text-sm text-rose-700">{error}</div> : null}

      {loading ? (
        <div className="text-sm text-slate-600">Loading…</div>
      ) : (
        <div className="grid gap-4">
          {canViewAudit ? (
            <Card>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-sm font-semibold">Recent audit events</div>
                  <div className="mt-1 text-sm text-slate-600">
                    Latest immutable approvals/actions for this run.
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <Link to={`/audit?run_id=${encodeURIComponent(runId)}`}>
                    <Button variant="secondary" size="sm">
                      Open audit
                    </Button>
                  </Link>
                  <Button variant="secondary" size="sm" onClick={loadAuditOnly}>
                    Refresh
                  </Button>
                </div>
              </div>

              {auditError ? (
                <div className="mt-3 rounded bg-rose-50 p-3 text-sm text-rose-700">{auditError}</div>
              ) : null}

              <div className="mt-4 overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b text-left text-slate-600">
                      <th className="py-2">Time</th>
                      <th className="py-2">User</th>
                      <th className="py-2">Action</th>
                      <th className="py-2">Details</th>
                    </tr>
                  </thead>
                  <tbody>
                    {auditEvents.map((e) => (
                      <tr key={e.id} className="border-b">
                        <td className="py-2 whitespace-nowrap">
                          {e.created_at ? new Date(e.created_at).toLocaleString() : '—'}
                        </td>
                        <td className="py-2">{e.user_id ?? '—'}</td>
                        <td className="py-2">{e.action}</td>
                        <td className="py-2">
                          <details>
                            <summary className="cursor-pointer text-slate-900 underline">View</summary>
                            <pre className="mt-2 max-w-xl overflow-auto rounded bg-slate-50 p-2 text-xs">
                              {JSON.stringify(e.details, null, 2)}
                            </pre>
                          </details>
                        </td>
                      </tr>
                    ))}
                    {auditEvents.length === 0 ? (
                      <tr>
                        <td colSpan={4} className="py-4 text-slate-600">
                          No audit events for this run yet.
                        </td>
                      </tr>
                    ) : null}
                  </tbody>
                </table>
              </div>
            </Card>
          ) : null}

          <Card>
            <div className="text-sm font-semibold">Metric time series</div>
            <div className="mt-1 text-sm text-slate-600">
              Raw metric values with zoom/inspect (brush). Regime-shift markers are aligned to detected change indices.
            </div>
            <div className="mt-4">
              <MetricSeriesChart metrics={metrics} changePoints={analysis?.change_points || []} />
            </div>
            <div className="mt-3 text-xs text-slate-600">
              points: <span className="font-medium">{metrics.length}</span>
            </div>
          </Card>

          <Card>
            <div className="text-sm font-semibold">Online posterior $P(change | t)$</div>
            <div className="mt-1 text-sm text-slate-600">
              Shaded uncertainty proxy + thresholds (80%, 90%) + vertical markers for detected shifts.
            </div>
            <div className="mt-4">
              <PosteriorChart
                probabilities={analysis?.probabilities || []}
                changePoints={analysis?.change_points || []}
              />
            </div>
          </Card>

          <Card>
            <div className="text-sm font-semibold">Offline posterior over change-point index</div>
            <div className="mt-1 text-sm text-slate-600">Computed via PyMC when available.</div>
            <div className="mt-4">
              <ChangePointPosteriorChart cpPosterior={posterior?.cp_posterior || []} />
            </div>
            <div className="mt-3 text-xs text-slate-600">
              method: <span className="font-medium">{posterior?.method || 'unknown'}</span>
            </div>
          </Card>

          <Card>
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm font-semibold">Mitigation suggestions (advisory)</div>
                <div className="mt-1 text-sm text-slate-600">
                  Approvals are mandatory and audited. Nothing is auto-executed.
                </div>
              </div>
              <Badge variant={canApprove ? 'success' : 'warning'}>
                {canApprove ? 'Can approve' : 'Read-only'}
              </Badge>
            </div>

            <div className="mt-4 overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b text-left text-slate-600">
                    <th className="py-2">Suggestion</th>
                    <th className="py-2">Confidence</th>
                    <th className="py-2">Risk</th>
                    <th className="py-2">Reversible</th>
                    <th className="py-2">Status</th>
                    <th className="py-2">Action</th>
                  </tr>
                </thead>
                <tbody>
                  {mitigations.map((m) => (
                    <tr key={m.id} className="border-b">
                      <td className="py-2">
                        <div className="font-medium">{m.suggestion}</div>
                        <div className="text-xs text-slate-600">{m.explanation}</div>
                      </td>
                      <td className="py-2">{Math.round(m.confidence * 100)}%</td>
                      <td className="py-2">{m.risk_level}</td>
                      <td className="py-2">{m.reversible ? 'yes' : 'no'}</td>
                      <td className="py-2">{m.approved ? 'approved' : 'pending'}</td>
                      <td className="py-2">
                        <Button
                          size="sm"
                          disabled={!canApprove || m.approved}
                          onClick={async () => {
                            await approveMitigation(runId, m.id)
                            const refreshed = await fetchMitigations(runId)
                            setMitigations(refreshed)
                          }}
                        >
                          Approve
                        </Button>
                      </td>
                    </tr>
                  ))}
                  {mitigations.length === 0 ? (
                    <tr>
                      <td colSpan={6} className="py-4 text-slate-600">
                        No suggestions.
                      </td>
                    </tr>
                  ) : null}
                </tbody>
              </table>
            </div>
          </Card>
        </div>
      )}
    </AppShell>
  )
}
