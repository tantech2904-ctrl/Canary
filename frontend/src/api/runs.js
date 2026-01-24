import { apiClient } from './client'

export async function fetchRuns() {
  const res = await apiClient.get('/runs')
  return res.data.runs || []
}
