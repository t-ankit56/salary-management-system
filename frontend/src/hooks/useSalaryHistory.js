import { useEffect, useState } from 'react'
import { getCorrections, getSalaryHistory } from '../api/salary'

export function useSalaryHistory(employeeId) {
  const [history, setHistory] = useState([])
  const [expandedPeriodId, setExpandedPeriodId] = useState(null)
  const [corrections, setCorrections] = useState([])

  useEffect(() => {
    getSalaryHistory(employeeId).then(({ data }) => setHistory(data ?? []))
  }, [employeeId])

  async function toggleCorrections(periodId) {
    if (expandedPeriodId === periodId) {
      setExpandedPeriodId(null)
      return
    }
    const { data } = await getCorrections(employeeId, periodId)
    setCorrections(data ?? [])
    setExpandedPeriodId(periodId)
  }

  return { history, expandedPeriodId, corrections, toggleCorrections }
}
