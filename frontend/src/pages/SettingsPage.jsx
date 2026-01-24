import React from 'react'
import AppShell from '../components/layout/AppShell'
import { Card } from '../components/ui/card'

export default function SettingsPage() {
  return (
    <AppShell title="Settings">
      <Card>
        <div className="text-sm font-semibold">Operational settings</div>
        <div className="mt-2 text-sm text-slate-600">
          This page is reserved for production controls (rate limits, thresholds, RBAC policies, API keys).
        </div>
        <ul className="mt-4 list-disc pl-5 text-sm text-slate-700">
          <li>Posterior thresholds (e.g. 80%, 90%)</li>
          <li>Mitigation gating rules</li>
          <li>Alert routing (Slack, email, PagerDuty)</li>
          <li>Data retention / export policies</li>
        </ul>
      </Card>
    </AppShell>
  )
}
