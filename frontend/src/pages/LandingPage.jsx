import React from 'react'
import { Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import { Button } from '../components/ui/button'
import { Card } from '../components/ui/card'

export default function LandingPage() {
  const { isAuthenticated } = useAuth()

  return (
    <div className="min-h-screen bg-slate-950 text-slate-50">
      <header className="mx-auto flex max-w-6xl items-center justify-between px-4 py-6">
        <div className="text-lg font-semibold tracking-tight">RegimeShift Sentinel</div>
        <div className="flex items-center gap-2">
          <Link to={isAuthenticated ? '/dashboard' : '/login'}>
            <Button variant="secondary">{isAuthenticated ? 'Open app' : 'Login'}</Button>
          </Link>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 pb-16">
        <section className="py-12">
          <h1 className="max-w-3xl text-4xl font-semibold leading-tight tracking-tight">
            Early-warning detection of regime shifts in high-stakes computational systems.
          </h1>
          <p className="mt-4 max-w-3xl text-slate-300">
            Bayesian change-point detection with uncertainty, confidence-gated mitigations, and mandatory
            human approval for every action.
          </p>
          <div className="mt-8 flex gap-3">
            <Link to={isAuthenticated ? '/dashboard' : '/login'}>
              <Button>{isAuthenticated ? 'Go to dashboard' : 'Get started'}</Button>
            </Link>
            <Link to="/upload">
              <Button variant="secondary">Upload metrics</Button>
            </Link>
          </div>
          <p className="mt-3 text-xs text-slate-400">
            Demo users: admin/admin123, analyst/analyst123, viewer/viewer123.
          </p>
        </section>

        <section className="grid gap-4 md:grid-cols-3">
          <Card className="border-slate-800 bg-slate-900">
            <div className="text-sm font-semibold">Bayesian posterior</div>
            <div className="mt-2 text-sm text-slate-300">
              Posterior probabilities over time with credible intervals and interpretable thresholds.
            </div>
          </Card>
          <Card className="border-slate-800 bg-slate-900">
            <div className="text-sm font-semibold">Human-in-the-loop</div>
            <div className="mt-2 text-sm text-slate-300">
              Mitigation suggestions are advisory and require explicit approvals with audit logging.
            </div>
          </Card>
          <Card className="border-slate-800 bg-slate-900">
            <div className="text-sm font-semibold">Safe + auditable</div>
            <div className="mt-2 text-sm text-slate-300">
              Rate limits, input validation, RBAC, immutable audit trails, and reversible actions.
            </div>
          </Card>
        </section>

        <section className="mt-10 grid gap-4 md:grid-cols-2">
          <Card className="border-slate-800 bg-slate-900">
            <div className="text-sm font-semibold">How it works</div>
            <ol className="mt-2 space-y-2 text-sm text-slate-300">
              <li>1. Upload a time-series metric stream (JSON).</li>
              <li>2. Run detection to surface candidate change points.</li>
              <li>3. Review suggested mitigations and approve with a reason.</li>
              <li>4. Audit every action with immutable event logs.</li>
            </ol>
          </Card>
          <Card className="border-slate-800 bg-slate-900">
            <div className="text-sm font-semibold">Built for production</div>
            <ul className="mt-2 space-y-2 text-sm text-slate-300">
              <li>JWT auth + role-based access control</li>
              <li>Server-side filtering on audit logs</li>
              <li>Rate limiting with Redis fallback</li>
              <li>Docker Compose + CI + Playwright E2E</li>
            </ul>
          </Card>
        </section>
      </main>
    </div>
  )
}
