const BASE = '/api'

async function get(path) {
  const res = await fetch(`${BASE}${path}`)
  if (!res.ok) {
    const body = await res.json().catch(() => ({}))
    throw new Error(body.detail || `Request failed: ${res.status}`)
  }
  return res.json()
}

export function getModels() {
  return get('/models')
}

export function getDatasets() {
  return get('/datasets')
}

export function getDatasetDetail(id) {
  return get(`/datasets/${id}`)
}

export function getModelDetail(id) {
  return get(`/models/${id}`)
}
