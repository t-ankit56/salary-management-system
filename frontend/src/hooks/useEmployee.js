import { useEffect, useState } from 'react'
import { getEmployee } from '../api/employees'

export function useEmployee(id) {
  const [employee, setEmployee] = useState(null)

  useEffect(() => {
    getEmployee(id).then(({ data }) => setEmployee(data))
  }, [id])

  return { employee }
}
