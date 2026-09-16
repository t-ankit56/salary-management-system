import { apiFetch } from './client'

export function getEmployee(id) {
  return apiFetch(`/api/employees/${id}/`)
}

export function listEmployees({ department, role, country, status, search, page } = {}) {
  const params = new URLSearchParams()
  if (department) params.set('department', department)
  if (role) params.set('role', role)
  if (country) params.set('country', country)
  if (status) params.set('status', status)
  if (search) params.set('search', search)
  if (page) params.set('page', page)

  const query = params.toString()
  return apiFetch(`/api/employees/${query ? `?${query}` : ''}`)
}

export function listDepartments() {
  return apiFetch('/api/departments/')
}

export function listRoles() {
  return apiFetch('/api/roles/')
}

export function listCountries() {
  return apiFetch('/api/countries/')
}
