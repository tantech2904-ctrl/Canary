export function decodeJwtPayload(token) {
  try {
    const [, payload] = token.split('.')
    const json = atob(payload.replace(/-/g, '+').replace(/_/g, '/'))
    return JSON.parse(json)
  } catch {
    return null
  }
}

export function roleRank(role) {
  const ranks = { viewer: 1, analyst: 2, admin: 3 }
  return ranks[role] || 0
}
