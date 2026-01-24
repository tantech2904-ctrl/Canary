import React from 'react'
import { Link, NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../hooks/useAuth.jsx'
import { Button } from '../ui/button'
import { cn } from '../ui/cn'

export default function AppShell({ title, children }) {
  const { role, logout, hasRole } = useAuth()
  const navigate = useNavigate()

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="sticky top-0 z-10 border-b bg-white">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-3">
          <div className="flex items-center gap-3">
            <Link to="/dashboard" className="font-semibold tracking-tight">
              RegimeShift Sentinel
            </Link>
            <span className="rounded bg-slate-100 px-2 py-1 text-xs">role: {role}</span>
          </div>

          <nav className="flex items-center gap-2">
            <TopNavLink to="/dashboard">Dashboard</TopNavLink>
            <TopNavLink to="/upload">Upload</TopNavLink>
            {hasRole('analyst') ? <TopNavLink to="/audit">Audit</TopNavLink> : null}
            {hasRole('admin') ? <TopNavLink to="/settings">Settings</TopNavLink> : null}
            <Button
              variant="secondary"
              onClick={() => {
                logout()
                navigate('/')
              }}
            >
              Logout
            </Button>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-6">
        <div className="mb-6">
          <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
          <p className="mt-1 text-sm text-slate-600">
            Early-warning Bayesian change-point detection with human-in-the-loop mitigation.
          </p>
        </div>
        {children}
      </main>

      <footer className="border-t bg-white">
        <div className="mx-auto max-w-6xl px-4 py-4 text-xs text-slate-500">
          RegimeShift Sentinel • Auditable • Reversible • Human-approved actions only
        </div>
      </footer>
    </div>
  )
}

function TopNavLink({ to, children }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) =>
        cn(
          'rounded px-3 py-2 text-sm transition-colors',
          isActive
            ? 'bg-slate-900 text-white'
            : 'text-slate-700 hover:bg-slate-100 hover:text-slate-900',
        )
      }
    >
      {children}
    </NavLink>
  )
}
