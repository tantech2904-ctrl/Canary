import React from 'react'
import { Link } from 'react-router-dom'
import { Button } from '../components/ui/button'

export default function NotFoundPage() {
  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto flex max-w-2xl flex-col gap-4 px-4 py-16">
        <div>
          <div className="text-sm font-medium text-slate-500">404</div>
          <h1 className="mt-1 text-3xl font-semibold tracking-tight text-slate-900">Page not found</h1>
          <p className="mt-2 text-sm text-slate-600">
            The page you’re looking for doesn’t exist or has moved.
          </p>
        </div>

        <div className="flex flex-wrap gap-2">
          <Link to="/">
            <Button>Go to landing</Button>
          </Link>
          <Link to="/dashboard">
            <Button variant="secondary">Open dashboard</Button>
          </Link>
        </div>

        <div className="text-xs text-slate-500">
          Tip: If you’re not signed in, protected pages will redirect you to Login.
        </div>
      </div>
    </div>
  )
}
