import { apiClient } from './client'

export async function login(username, password) {
  const form = new URLSearchParams()
  form.set('username', username)
  form.set('password', password)

  const res = await apiClient.post('/auth/login', form, {
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
  })
  return res.data
}
