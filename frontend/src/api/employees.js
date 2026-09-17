/** Employee and reference-data (departments/roles/countries) endpoint calls. */

import { apiFetch } from './client'

export function getEmployee(id) {
  return apiFetch(`/api/employees/${id}/`)
}

export function createEmployee(fields) {
  return apiFetch('/api/employees/', {
    method: 'POST',
    body: JSON.stringify(fields),
  })
}

export function updateEmployee(id, fields) {
  return apiFetch(`/api/employees/${id}/`, {
    method: 'PATCH',
    body: JSON.stringify(fields),
  })
}

export function deactivateEmployee(id, effective_date) {
  return apiFetch(`/api/employees/${id}/deactivate/`, {
    method: 'POST',
    body: JSON.stringify({ effective_date }),
  })
}

export function reactivateEmployee(id, effective_date) {
  return apiFetch(`/api/employees/${id}/reactivate/`, {
    method: 'POST',
    body: JSON.stringify({ effective_date }),
  })
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
