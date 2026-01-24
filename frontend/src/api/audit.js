import { apiClient } from './client'

export async function fetchAuditLogs(params = {}) {
  const res = await apiClient.get('/audit/logs', { params })
  return res.data.logs || []
}
