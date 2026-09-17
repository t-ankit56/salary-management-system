import { useCallback, useEffect, useState } from 'react'
import { getCorrections, getSalaryHistory } from '../api/salary'

/**
 * Salary periods for an employee, plus on-demand corrections for whichever period is
 * currently expanded.
 */
export function useSalaryHistory(employeeId) {
  const [history, setHistory] = useState([])
  const [expandedPeriodId, setExpandedPeriodId] = useState(null)
  const [corrections, setCorrections] = useState([])

  const refetch = useCallback(() => {
    return getSalaryHistory(employeeId).then(({ data }) => setHistory(data ?? []))
  }, [employeeId])

  useEffect(() => {
    refetch()
  }, [refetch])

  async function toggleCorrections(periodId) {
    if (expandedPeriodId === periodId) {
      setExpandedPeriodId(null)
      return
    }
    const { data } = await getCorrections(employeeId, periodId)
    setCorrections(data ?? [])
    setExpandedPeriodId(periodId)
  }

  return { history, expandedPeriodId, corrections, toggleCorrections, refetch }
}
