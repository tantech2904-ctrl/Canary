import React, { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import AppShell from '../components/layout/AppShell'
import { Card } from '../components/ui/card'
import { Badge } from '../components/ui/badge'
import { Button } from '../components/ui/button'
import { fetchRuns } from '../api/runs'

export default function DashboardPage() {
  const [runs, setRuns] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  async function load() {
    setLoading(true)
    setError('')
    try {
      const data = await fetchRuns()
      setRuns(data)
    } catch (err) {
      setError(err?.response?.data?.detail || 'Failed to load runs')
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    load()
  }, [])

  return (
    <AppShell title="Dashboard">
      <div className="mb-4 flex items-center justify-between">
        <div className="text-sm text-slate-600">
          Live runs and historical analyses. Select a run to inspect posteriors and mitigations.
        </div>
        <div className="flex items-center gap-2">
          <Link to="/upload">
            <Button>Upload metrics</Button>
          </Link>
          <Button variant="secondary" onClick={load}>
            Refresh
          </Button>
        </div>
      </div>

      {error ? <div className="mb-4 rounded bg-rose-50 p-3 text-sm text-rose-700">{error}</div> : null}

      {loading ? (
        <div className="text-sm text-slate-600">Loading…</div>
      ) : runs.length === 0 ? (
        <Card>
          <div className="text-sm">No runs found.</div>
          <div className="mt-1 text-sm text-slate-600">
            Upload a JSON payload to create your first run.
          </div>
          <div className="mt-4">
            <Link to="/upload">
              <Button>Upload metrics</Button>
            </Link>
          </div>
        </Card>
      ) : (
        <div className="grid gap-3 md:grid-cols-2">
          {runs.map((r) => (
            <Card key={r.id}>
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-sm font-semibold">{r.name}</div>
                  <div className="mt-1 text-sm text-slate-600">{r.description || '—'}</div>
                </div>
                <Badge variant="default">run #{r.id}</Badge>
              </div>
              <div className="mt-4">
                <Link to={`/runs/${r.id}`}>
                  <Button>Open</Button>
                </Link>
              </div>
            </Card>
          ))}
        </div>
      )}
    </AppShell>
  )
}
