import { apiFetch } from './client'

export function uploadRoster(file) {
  const formData = new FormData()
  formData.append('file', file)
  return apiFetch('/api/imports/roster/', { method: 'POST', body: formData })
}
