import React, { createContext, useCallback, useContext, useMemo, useState } from 'react'
import { login as apiLogin } from '../api/auth'
import { decodeJwtPayload, roleRank } from '../utils/jwt'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [token, setToken] = useState(() => localStorage.getItem('rss_token'))
  const [role, setRole] = useState(() => localStorage.getItem('rss_role') || 'viewer')

  const isAuthenticated = Boolean(token)

  const login = useCallback(async (username, password) => {
    const data = await apiLogin(username, password)
    localStorage.setItem('rss_token', data.access_token)

    const payload = decodeJwtPayload(data.access_token)
    const newRole = payload?.role || 'viewer'
    localStorage.setItem('rss_role', newRole)

    setToken(data.access_token)
    setRole(newRole)
  }, [])

  const logout = useCallback(() => {
    localStorage.removeItem('rss_token')
    localStorage.removeItem('rss_role')
    setToken(null)
    setRole('viewer')
  }, [])

  const hasRole = useCallback((minRole) => roleRank(role) >= roleRank(minRole), [role])

  const value = useMemo(() => ({ token, role, isAuthenticated, login, logout, hasRole }), [
    token,
    role,
    isAuthenticated,
    login,
    logout,
    hasRole,
  ])

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}

export function useAuth() {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used within AuthProvider')
  return ctx
}
