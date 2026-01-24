import { apiClient } from './client'

export async function fetchMitigations(runId) {
  const res = await apiClient.get(`/mitigations/${runId}`)
  return res.data.mitigations || []
}

export async function approveMitigation(runId, mitigationId) {
  const res = await apiClient.post(`/mitigations/${runId}/approve`, null, {
    params: { mitigation_id: mitigationId },
  })
  return res.data
}
