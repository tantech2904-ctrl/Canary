import React, { useMemo, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import AppShell from '../components/layout/AppShell'
import { Card } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'
import { cn } from '../components/ui/cn'
import { uploadMetrics } from '../api/metrics'

function computePreview(metrics) {
  if (!Array.isArray(metrics) || metrics.length === 0) return null

  let min = Number.POSITIVE_INFINITY
  let max = Number.NEGATIVE_INFINITY
  let start = null
  let end = null

  for (const m of metrics) {
    const value = Number(m?.value)
    if (!Number.isFinite(value)) continue
    min = Math.min(min, value)
    max = Math.max(max, value)

    const dt = new Date(m?.timestamp)
    if (!Number.isFinite(dt.getTime())) continue
    if (!start || dt < start) start = dt
    if (!end || dt > end) end = dt
  }

  if (!Number.isFinite(min) || !Number.isFinite(max)) return null
  return { count: metrics.length, min, max, start, end }
}

function validatePayload(obj) {
  if (!obj || typeof obj !== 'object') return 'Invalid JSON: expected an object'
  if (typeof obj.run_name !== 'string' || obj.run_name.trim().length === 0) return 'Missing run_name'
  if (!Array.isArray(obj.metrics) || obj.metrics.length === 0) return 'Missing metrics[]'

  for (let i = 0; i < Math.min(obj.metrics.length, 50); i++) {
    const p = obj.metrics[i]
    if (!p || typeof p !== 'object') return `Invalid metrics[${i}]`
    if (typeof p.timestamp !== 'string' && typeof p.timestamp !== 'number') return `Missing metrics[${i}].timestamp`
    const dt = new Date(p.timestamp)
    if (!Number.isFinite(dt.getTime())) return `Invalid metrics[${i}].timestamp`
    const value = Number(p.value)
    if (!Number.isFinite(value)) return `Invalid metrics[${i}].value`
  }

  return ''
}

function buildSamplePayload() {
  const base = new Date()
  const metrics = []
  for (let i = 0; i < 120; i++) {
    metrics.push({ timestamp: new Date(base.getTime() + i * 60_000).toISOString(), value: 0.0 })
  }
  for (let i = 120; i < 240; i++) {
    metrics.push({ timestamp: new Date(base.getTime() + i * 60_000).toISOString(), value: 2.5 })
  }
  return {
    run_name: `sample-mean-shift-${Date.now()}`,
    description: 'Sample payload: mean shift 0.0 → 2.5 at t=120',
    metrics,
  }
}

function downloadJson(obj, filename) {
  const blob = new Blob([JSON.stringify(obj, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  a.remove()
  URL.revokeObjectURL(url)
}

export default function UploadMetricsPage() {
  const navigate = useNavigate()

  const [fileName, setFileName] = useState('')
  const [runName, setRunName] = useState('')
  const [description, setDescription] = useState('')
  const [metrics, setMetrics] = useState([])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const preview = useMemo(() => computePreview(metrics), [metrics])

  async function onFileChange(e) {
    setError('')
    setSuccess('')

    const file = e.target.files?.[0]
    if (!file) return

    if (file.size > 5_000_000) {
      setError('File too large. Please keep uploads under 5MB for now.')
      return
    }

    setFileName(file.name)

    try {
      const text = await file.text()
      const obj = JSON.parse(text)

      const validationError = validatePayload(obj)
      if (validationError) {
        setError(validationError)
        setRunName('')
        setDescription('')
        setMetrics([])
        return
      }

      setRunName(String(obj.run_name || '').trim())
      setDescription(String(obj.description || ''))
      setMetrics(Array.isArray(obj.metrics) ? obj.metrics : [])
    } catch (err) {
      setError(err?.message || 'Failed to parse JSON')
      setRunName('')
      setDescription('')
      setMetrics([])
    }
  }

  async function onUpload() {
    setError('')
    setSuccess('')
    setLoading(true)
    try {
      const payload = {
        run_name: runName,
        description,
        metrics,
      }
      const validationError = validatePayload(payload)
      if (validationError) throw new Error(validationError)

      const res = await uploadMetrics(payload)
      const runId = res?.run_id
      if (!runId) throw new Error('Upload succeeded but run_id was missing from response')

      setSuccess(`Uploaded ${res.count ?? metrics.length} points to run #${runId}`)
      navigate(`/runs/${runId}`)
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Upload failed')
    } finally {
      setLoading(false)
    }
  }

  function onDownloadSample() {
    try {
      const sample = buildSamplePayload()
      downloadJson(sample, 'sample_metrics_mean_shift.json')
    } catch (err) {
      setError(err?.message || 'Failed to generate sample')
    }
  }

  function onLoadSample() {
    try {
      setError('')
      setSuccess('')
      const sample = buildSamplePayload()
      setFileName('')
      setRunName(String(sample.run_name || ''))
      setDescription(String(sample.description || ''))
      setMetrics(Array.isArray(sample.metrics) ? sample.metrics : [])
    } catch (err) {
      setError(err?.message || 'Failed to load sample')
    }
  }

  const canUpload = runName.trim().length > 0 && metrics.length > 0 && !loading

  return (
    <AppShell title="Upload Metrics">
      <div className="grid gap-4">
        <Card>
          <div className="text-sm font-semibold">Upload metrics JSON</div>
          <div className="mt-1 text-sm text-slate-600">
            Choose a JSON file with keys: <span className="font-medium">run_name</span>,{' '}
            <span className="font-medium">description</span> (optional), and <span className="font-medium">metrics</span>
            (array of {`{timestamp, value}`} objects).
          </div>

          <div className="mt-4 grid gap-3">
            <div>
              <label className="text-sm font-medium">Metrics JSON file</label>
              <Input
                data-testid="upload-file"
                type="file"
                accept="application/json,.json"
                onChange={onFileChange}
              />
              {fileName ? <div className="mt-1 text-xs text-slate-600">selected: {fileName}</div> : null}
            </div>

            <div className="grid gap-3 md:grid-cols-2">
              <div>
                <label className="text-sm font-medium">Run name</label>
                <Input value={runName} onChange={(e) => setRunName(e.target.value)} placeholder="my-run" />
              </div>
              <div>
                <label className="text-sm font-medium">Points</label>
                <Input value={metrics.length ? String(metrics.length) : ''} readOnly placeholder="—" />
              </div>
            </div>

            <div>
              <label className="text-sm font-medium">Description</label>
              <textarea
                className={cn(
                  'min-h-[96px] w-full rounded-md border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-slate-400',
                )}
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                placeholder="Optional notes about the run"
              />
            </div>

            {error ? <div className="rounded bg-rose-50 p-3 text-sm text-rose-700">{error}</div> : null}
            {success ? <div className="rounded bg-emerald-50 p-3 text-sm text-emerald-800">{success}</div> : null}

            <div className="flex flex-wrap items-center justify-between gap-2">
              <div className="flex flex-wrap items-center gap-2">
                <Button variant="secondary" onClick={onLoadSample} disabled={loading}>
                  Load sample into form
                </Button>
                <Button variant="secondary" onClick={onDownloadSample} disabled={loading}>
                  Download sample JSON
                </Button>
              </div>

              <div className="flex items-center justify-end gap-2">
              <Button variant="secondary" onClick={() => navigate('/dashboard')} disabled={loading}>
                Cancel
              </Button>
              <Button onClick={onUpload} disabled={!canUpload}>
                {loading ? 'Uploading…' : 'Upload'}
              </Button>
              </div>
            </div>
          </div>
        </Card>

        <Card data-testid="upload-preview">
          <div className="text-sm font-semibold">Preview</div>
          {preview ? (
            <div className="mt-2 grid gap-2 text-sm text-slate-700 md:grid-cols-2">
              <div>
                <div className="text-xs text-slate-600">points</div>
                <div className="font-medium">{preview.count}</div>
              </div>
              <div>
                <div className="text-xs text-slate-600">range</div>
                <div className="font-medium">
                  {preview.start ? preview.start.toISOString() : '—'} → {preview.end ? preview.end.toISOString() : '—'}
                </div>
              </div>
              <div>
                <div className="text-xs text-slate-600">min</div>
                <div className="font-medium">{preview.min.toFixed(4)}</div>
              </div>
              <div>
                <div className="text-xs text-slate-600">max</div>
                <div className="font-medium">{preview.max.toFixed(4)}</div>
              </div>
            </div>
          ) : (
            <div className="mt-2 text-sm text-slate-600">Select a valid file to see a preview.</div>
          )}
          <div className="mt-3 text-xs text-slate-600">
            Tip: you can generate a sample file in the repo at <span className="font-medium">datasets/synthetic/run_mean_shift.json</span>.
          </div>
        </Card>
      </div>
    </AppShell>
  )
}
