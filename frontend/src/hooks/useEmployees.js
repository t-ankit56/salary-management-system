import { useEffect, useState } from 'react'
import { listCountries, listDepartments, listEmployees, listRoles } from '../api/employees'

const initialFilters = {
  department: '',
  role: '',
  country: '',
  status: '',
  search: '',
  page: 1,
}

export function useEmployees() {
  const [filters, setFilters] = useState(initialFilters)
  const [employees, setEmployees] = useState([])
  const [count, setCount] = useState(0)
  const [departments, setDepartments] = useState([])
  const [roles, setRoles] = useState([])
  const [countries, setCountries] = useState([])

  useEffect(() => {
    listDepartments().then(({ data }) => setDepartments(data ?? []))
    listRoles().then(({ data }) => setRoles(data ?? []))
    listCountries().then(({ data }) => setCountries(data ?? []))
  }, [])

  useEffect(() => {
    listEmployees(filters).then(({ data }) => {
      if (data) {
        setEmployees(data.results)
        setCount(data.count)
      }
    })
  }, [filters])

  function setFilter(key, value) {
    setFilters((prev) => ({ ...prev, [key]: value, page: 1 }))
  }

  function setPage(page) {
    setFilters((prev) => ({ ...prev, page }))
  }

  return { employees, count, departments, roles, countries, filters, setFilter, setPage }
}
