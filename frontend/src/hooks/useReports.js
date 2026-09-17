import { useEffect, useState } from 'react'
import { getReport } from '../api/reports'

export const REPORT_NAMES = [
  'total_payroll_cost',
  'headcount_by_department',
  'headcount_by_country',
  'average_salary_by_department',
  'average_salary_by_country',
  'average_bonus_by_department',
]

export function useReports(asOf) {
  const [reports, setReports] = useState({})
  const [error, setError] = useState(null)

  useEffect(() => {
    if (!asOf) return

    setError(null)

    REPORT_NAMES.forEach((name) => {
      getReport(name, asOf).then(({ status, data }) => {
        if (status === 200) {
          setReports((prev) => ({
            ...prev,
            [name]: { value: data[name], excluded_count: data.excluded_count },
          }))
          return
        }
        setReports((prev) => {
          const next = { ...prev }
          delete next[name]
          return next
        })
        if (data?.detail) {
          setError({ detail: data.detail, earliestAvailableDate: data.earliest_available_date })
        }
      })
    })
  }, [asOf])

  return { reports, error }
}
