import { Link, useNavigate } from 'react-router-dom'
import { useEmployees } from '../hooks/useEmployees'

const PAGE_SIZE = 25

const selectClass =
  'px-2.5 py-[9px] text-sm border border-slate-300 rounded-md text-slate-600 bg-white'

const pageButtonClass =
  'px-3 py-[7px] text-[13px] font-semibold rounded-md border border-slate-300 bg-white text-slate-600'

const activePageButtonClass =
  'px-3 py-[7px] text-[13px] font-semibold rounded-md border border-blue-700 bg-blue-700 text-white'

const PAGE_NEIGHBORS = 2

function pageNumbersWithEllipses(current, total) {
  const pages = []
  for (let page = 1; page <= total; page++) {
    if (
      page === 1 ||
      page === total ||
      (page >= current - PAGE_NEIGHBORS && page <= current + PAGE_NEIGHBORS)
    ) {
      pages.push(page)
    }
  }

  const withEllipses = []
  let previous
  for (const page of pages) {
    if (previous !== undefined && page - previous > 1) {
      withEllipses.push('…')
    }
    withEllipses.push(page)
    previous = page
  }
  return withEllipses
}

function StatusBadge({ status }) {
  const isActive = status === 'active'
  return (
    <span
      className={`inline-block px-2.5 py-[3px] text-xs font-semibold rounded-full ${
        isActive ? 'bg-green-100 text-green-700' : 'bg-slate-100 text-slate-600'
      }`}
    >
      {isActive ? 'Active' : 'Inactive'}
    </span>
  )
}

function EmployeeListPage() {
  const navigate = useNavigate()
  const {
    employees,
    count,
    departments,
    roles,
    countries,
    filters,
    setFilter,
    setPage,
    clearFilters,
  } = useEmployees()

  const totalPages = Math.max(1, Math.ceil(count / PAGE_SIZE))
  const pageNumbers = pageNumbersWithEllipses(filters.page, totalPages)
  const rangeStart = count === 0 ? 0 : (filters.page - 1) * PAGE_SIZE + 1
  const rangeEnd = Math.min(filters.page * PAGE_SIZE, count)

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-[1240px] mx-auto">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-6">
          <h1 className="text-[22px] font-bold text-slate-800 m-0">Employees</h1>
          <Link
            to="/employees/new"
            className="px-[18px] py-2.5 text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors"
          >
            + New Employee
          </Link>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg p-4 mb-4 flex flex-wrap gap-3 items-center">
          <input
            type="text"
            placeholder="Search by name or employee code"
            value={filters.search}
            onChange={(e) => setFilter('search', e.target.value)}
            className="flex-1 min-w-[220px] px-3 py-[9px] text-sm border border-slate-300 rounded-md text-slate-800"
          />
          <select
            aria-label="Department"
            value={filters.department}
            onChange={(e) => setFilter('department', e.target.value)}
            className={selectClass}
          >
            <option value="">All Departments</option>
            {departments.map((department) => (
              <option key={department.id} value={department.id}>
                {department.name}
              </option>
            ))}
          </select>
          <select
            aria-label="Role"
            value={filters.role}
            onChange={(e) => setFilter('role', e.target.value)}
            className={selectClass}
          >
            <option value="">All Roles</option>
            {roles.map((role) => (
              <option key={role.id} value={role.id}>
                {role.name}
              </option>
            ))}
          </select>
          <select
            aria-label="Country"
            value={filters.country}
            onChange={(e) => setFilter('country', e.target.value)}
            className={selectClass}
          >
            <option value="">All Countries</option>
            {countries.map((country) => (
              <option key={country.id} value={country.id}>
                {country.name}
              </option>
            ))}
          </select>
          <select
            aria-label="Status"
            value={filters.status}
            onChange={(e) => setFilter('status', e.target.value)}
            className={selectClass}
          >
            <option value="">All Statuses</option>
            <option value="active">Active</option>
            <option value="inactive">Inactive</option>
          </select>
          <button
            type="button"
            onClick={clearFilters}
            className="px-3 py-[9px] text-sm font-semibold text-slate-600 hover:text-slate-800"
          >
            Clear Filters
          </button>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-slate-100">
                <th className="text-left px-4 py-3 text-[12px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200">
                  Employee Code
                </th>
                <th className="text-left px-4 py-3 text-[12px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200">
                  Name
                </th>
                <th className="text-left px-4 py-3 text-[12px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200">
                  Department
                </th>
                <th className="text-left px-4 py-3 text-[12px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200">
                  Role
                </th>
                <th className="text-left px-4 py-3 text-[12px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200">
                  Country
                </th>
                <th className="text-left px-4 py-3 text-[12px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200">
                  Status
                </th>
              </tr>
            </thead>
            <tbody>
              {employees.map((employee) => (
                <tr
                  key={employee.id}
                  onClick={() => navigate(`/employees/${employee.id}`)}
                  className="border-b border-slate-100 cursor-pointer hover:bg-slate-50"
                >
                  <td className="px-4 py-[13px] text-slate-600 font-mono">{employee.employee_code}</td>
                  <td className="px-4 py-[13px] text-slate-800 font-semibold">
                    {employee.first_name} {employee.last_name}
                  </td>
                  <td className="px-4 py-[13px] text-slate-600">{employee.department_name}</td>
                  <td className="px-4 py-[13px] text-slate-600">{employee.role_name}</td>
                  <td className="px-4 py-[13px] text-slate-600">{employee.country_name}</td>
                  <td className="px-4 py-[13px]">
                    <StatusBadge status={employee.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between mt-4">
          <span className="text-[13px] text-slate-500">
            Showing {rangeStart}–{rangeEnd} of {count} employees
          </span>
          <div className="flex gap-1.5 items-center">
            <button
              type="button"
              onClick={() => setPage(Math.max(1, filters.page - 1))}
              className={pageButtonClass}
            >
              Prev
            </button>
            {pageNumbers.map((page, index) =>
              page === '…' ? (
                <span key={`ellipsis-${index}`} className="px-1.5 text-[13px] text-slate-400 select-none">
                  …
                </span>
              ) : (
                <button
                  key={page}
                  type="button"
                  onClick={() => setPage(page)}
                  className={page === filters.page ? activePageButtonClass : pageButtonClass}
                >
                  {page}
                </button>
              ),
            )}
            <button
              type="button"
              onClick={() => setPage(Math.min(totalPages, filters.page + 1))}
              className={pageButtonClass}
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmployeeListPage
