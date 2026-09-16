import { apiFetch } from './client'

export function getSalaryHistory(employeeId) {
  return apiFetch(`/api/employees/${employeeId}/salary-periods/`)
}

export function getCorrections(employeeId, periodId) {
  return apiFetch(`/api/employees/${employeeId}/salary-periods/${periodId}/corrections/`)
}
