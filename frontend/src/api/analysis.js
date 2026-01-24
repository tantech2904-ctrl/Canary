import { apiClient } from './client'

export async function fetchAnalysis(runId) {
  const res = await apiClient.get(`/analysis/${runId}`)
  return res.data
}

export async function fetchPosterior(runId) {
  const res = await apiClient.get(`/analysis/${runId}/posterior`)
  return res.data
}
