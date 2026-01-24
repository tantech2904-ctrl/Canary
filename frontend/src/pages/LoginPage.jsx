import React, { useState } from 'react'
import { useNavigate, Link } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.jsx'
import { API_BASE_URL } from '../api/client'
import { Card } from '../components/ui/card'
import { Input } from '../components/ui/input'
import { Button } from '../components/ui/button'

export default function LoginPage() {
  const { login } = useAuth()
  const navigate = useNavigate()

  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function onSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      await login(username, password)
      navigate('/dashboard')
    } catch (err) {
      const status = err?.response?.status
      const endpoint = `${API_BASE_URL}/auth/login`

      if (!err?.response) {
        setError(`Cannot reach API at ${API_BASE_URL}. Start the backend (and Postgres/Redis) and try again.`)
      } else if (status === 404) {
        setError(`Auth endpoint not found (${endpoint}). Check VITE_API_BASE_URL and that the backend is running.`)
      } else {
        const detail =
          (typeof err?.response?.data === 'object' && err?.response?.data?.detail) ||
          err?.response?.data ||
          'Login failed'
        setError(String(detail))
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-50">
      <div className="mx-auto flex max-w-md flex-col gap-4 px-4 py-16">
        <div className="text-center">
          <h1 className="text-2xl font-semibold">Sign in</h1>
          <p className="mt-1 text-sm text-slate-600">
            Use your role-based account to access the dashboard.
          </p>
        </div>

        <Card>
          <form className="space-y-3" onSubmit={onSubmit}>
            <div>
              <label className="text-sm font-medium">Username</label>
              <Input value={username} onChange={(e) => setUsername(e.target.value)} autoFocus />
            </div>
            <div>
              <label className="text-sm font-medium">Password</label>
              <Input type="password" value={password} onChange={(e) => setPassword(e.target.value)} />
            </div>
            {error ? <div className="rounded bg-rose-50 p-2 text-sm text-rose-700">{error}</div> : null}
            <Button disabled={loading} className="w-full">
              {loading ? 'Signing in…' : 'Sign in'}
            </Button>
          </form>
        </Card>

        <div className="text-center text-sm text-slate-600">
          <Link className="text-slate-900 underline" to="/">
            Back to landing
          </Link>
        </div>
      </div>
    </div>
  )
}
