import { apiClient } from './client'

export async function fetchRunMetrics(runId, limit = 5000) {
  const res = await apiClient.get(`/runs/${runId}/metrics`, { params: { limit } })
  return res.data.metrics || []
}

export async function uploadMetrics(payload) {
  const res = await apiClient.post('/metrics/upload', payload)
  return res.data
}
