import React, { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import AppShell from '../components/layout/AppShell'
import { Card } from '../components/ui/card'
import { Button } from '../components/ui/button'
import { Input } from '../components/ui/input'
import { fetchAuditLogs } from '../api/audit'

export default function AuditLogsPage() {
  const [searchParams, setSearchParams] = useSearchParams()

  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  const initial = useMemo(
    () => ({
      runId: searchParams.get('run_id') || '',
      userId: searchParams.get('user_id') || '',
      action: searchParams.get('action') || '',
      since: searchParams.get('since') || '',
      until: searchParams.get('until') || '',
      limit: searchParams.get('limit') || '500',
    }),
    // eslint-disable-next-line react-hooks/exhaustive-deps
    [],
  )

  const [runId, setRunId] = useState(initial.runId)
  const [userId, setUserId] = useState(initial.userId)
  const [action, setAction] = useState(initial.action)
  const [since, setSince] = useState(initial.since)
  const [until, setUntil] = useState(initial.until)
  const [limit, setLimit] = useState(initial.limit)

  const buildParams = useCallback(() => {
    const params = {}
    const runIdNum = Number(runId)
    const userIdNum = Number(userId)
    const limitNum = Number(limit)

    if (Number.isFinite(limitNum) && limitNum > 0) params.limit = Math.min(limitNum, 2000)
    if (runId && Number.isFinite(runIdNum)) params.run_id = runIdNum
    if (userId && Number.isFinite(userIdNum)) params.user_id = userIdNum
    if (action.trim()) params.action = action.trim()
    if (since) params.since = new Date(since).toISOString()
    if (until) params.until = new Date(until).toISOString()

    return params
  }, [action, limit, runId, since, until, userId])

  const syncUrl = useCallback(() => {
    const params = buildParams()
    const sp = new URLSearchParams()
    if (params.limit) sp.set('limit', String(params.limit))
    if (params.run_id !== undefined) sp.set('run_id', String(params.run_id))
    if (params.user_id !== undefined) sp.set('user_id', String(params.user_id))
    if (params.action) sp.set('action', String(params.action))
    if (params.since) sp.set('since', String(params.since))
    if (params.until) sp.set('until', String(params.until))
    setSearchParams(sp)
  }, [buildParams, setSearchParams])

  const load = useCallback(async () => {
    setLoading(true)
    setError('')
    try {
      const data = await fetchAuditLogs(buildParams())
      setLogs(data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load audit logs')
    } finally {
      setLoading(false)
    }
  }, [buildParams])

  useEffect(() => {
    load()
  }, [load])

  function clearFilters() {
    setRunId('')
    setUserId('')
    setAction('')
    setSince('')
    setUntil('')
    setLimit('500')
  }

  return (
    <AppShell title="Audit logs">
      <div className="mb-4 flex items-center justify-between">
        <div className="text-sm text-slate-600">Immutable approval trail (latest 500).</div>
        <div className="flex items-center gap-2">
          <Button variant="secondary" onClick={clearFilters} disabled={loading}>
            Clear
          </Button>
          <Button
            variant="secondary"
            onClick={() => {
              syncUrl()
              load()
            }}
            disabled={loading}
          >
            Apply
          </Button>
        </div>
      </div>

      {error ? <div className="mb-4 rounded bg-rose-50 p-3 text-sm text-rose-700">{error}</div> : null}

      <Card className="mb-4">
        <div className="grid gap-3 md:grid-cols-3">
          <div>
            <label className="text-sm font-medium">Run ID</label>
            <Input value={runId} onChange={(e) => setRunId(e.target.value)} placeholder="e.g. 12" />
          </div>
          <div>
            <label className="text-sm font-medium">User ID</label>
            <Input value={userId} onChange={(e) => setUserId(e.target.value)} placeholder="e.g. 1" />
          </div>
          <div>
            <label className="text-sm font-medium">Action</label>
            <Input value={action} onChange={(e) => setAction(e.target.value)} placeholder="e.g. mitigation_approved" />
          </div>
          <div>
            <label className="text-sm font-medium">Since</label>
            <Input type="datetime-local" value={since} onChange={(e) => setSince(e.target.value)} />
          </div>
          <div>
            <label className="text-sm font-medium">Until</label>
            <Input type="datetime-local" value={until} onChange={(e) => setUntil(e.target.value)} />
          </div>
          <div>
            <label className="text-sm font-medium">Limit</label>
            <Input value={limit} onChange={(e) => setLimit(e.target.value)} placeholder="500" />
          </div>
        </div>
      </Card>

      <Card>
        {loading ? (
          <div className="text-sm text-slate-600">Loading…</div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b text-left text-slate-600">
                  <th className="py-2">Time</th>
                  <th className="py-2">User</th>
                  <th className="py-2">Run</th>
                  <th className="py-2">Action</th>
                  <th className="py-2">Details</th>
                </tr>
              </thead>
              <tbody>
                {logs.map((l) => (
                  <tr key={l.id} className="border-b">
                    <td className="py-2 whitespace-nowrap">
                      {l.created_at ? new Date(l.created_at).toLocaleString() : '—'}
                    </td>
                    <td className="py-2">{l.user_id ?? '—'}</td>
                    <td className="py-2">
                      <Link className="text-slate-900 underline" to={`/runs/${l.run_id}`}>
                        {l.run_id}
                      </Link>
                    </td>
                    <td className="py-2">{l.action}</td>
                    <td className="py-2">
                      <details>
                        <summary className="cursor-pointer text-slate-900 underline">View</summary>
                        <pre className="mt-2 max-w-xl overflow-auto rounded bg-slate-50 p-2 text-xs">
                          {JSON.stringify(l.details, null, 2)}
                        </pre>
                      </details>
                    </td>
                  </tr>
                ))}
                {logs.length === 0 ? (
                  <tr>
                    <td colSpan={5} className="py-4 text-slate-600">
                      No audit events.
                    </td>
                  </tr>
                ) : null}
              </tbody>
            </table>
          </div>
        )}
      </Card>
    </AppShell>
  )
}
