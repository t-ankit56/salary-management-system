import { useCallback, useEffect, useState } from 'react'
import { getEmployee } from '../api/employees'

export function useEmployee(id) {
  const [employee, setEmployee] = useState(null)

  const refetch = useCallback(() => {
    return getEmployee(id).then(({ data }) => setEmployee(data))
  }, [id])

  useEffect(() => {
    refetch()
  }, [refetch])

  return { employee, refetch }
}
