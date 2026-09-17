import { apiFetch } from './client'

export function getSalaryHistory(employeeId) {
  return apiFetch(`/api/employees/${employeeId}/salary-periods/`)
}

export function getCorrections(employeeId, periodId) {
  return apiFetch(`/api/employees/${employeeId}/salary-periods/${periodId}/corrections/`)
}

export function recordSalaryChange(employeeId, { base, allowance, yearly_bonus, currency, effective_from }) {
  return apiFetch(`/api/employees/${employeeId}/salary-changes/`, {
    method: 'POST',
    body: JSON.stringify({ base, allowance, yearly_bonus, currency, effective_from }),
  })
}

export function correctSalaryPeriod(employeeId, { salary_period, base, allowance, yearly_bonus, reason }) {
  return apiFetch(`/api/employees/${employeeId}/salary-corrections/`, {
    method: 'POST',
    body: JSON.stringify({ salary_period, base, allowance, yearly_bonus, reason }),
  })
}
