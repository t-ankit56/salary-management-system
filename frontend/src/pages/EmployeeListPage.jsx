import { Link } from 'react-router-dom'

const EMPLOYEES = [
  {
    code: 'EMP-1001',
    name: 'Sarah Chen',
    department: 'Engineering',
    role: 'Senior Engineer',
    country: 'United States',
    status: 'active',
  },
  {
    code: 'EMP-1002',
    name: 'James Okafor',
    department: 'Sales',
    role: 'Account Executive',
    country: 'United Kingdom',
    status: 'active',
  },
  {
    code: 'EMP-1003',
    name: 'Priya Nair',
    department: 'Finance',
    role: 'Financial Analyst',
    country: 'India',
    status: 'inactive',
  },
  {
    code: 'EMP-1004',
    name: 'Diego Martins',
    department: 'Engineering',
    role: 'Engineering Manager',
    country: 'Brazil',
    status: 'active',
  },
]

const selectClass =
  'px-2.5 py-[9px] text-sm border border-slate-300 rounded-md text-slate-600 bg-white'

const pageButtonClass =
  'px-3 py-[7px] text-[13px] font-semibold rounded-md border border-slate-300 bg-white text-slate-600'

const activePageButtonClass =
  'px-3 py-[7px] text-[13px] font-semibold rounded-md border border-blue-700 bg-blue-700 text-white'

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
            className="flex-1 min-w-[220px] px-3 py-[9px] text-sm border border-slate-300 rounded-md text-slate-800"
          />
          <select className={selectClass}>
            <option>All Departments</option>
            <option>Engineering</option>
            <option>Sales</option>
            <option>Finance</option>
            <option>HR</option>
            <option>Operations</option>
          </select>
          <select className={selectClass}>
            <option>All Roles</option>
            <option>Manager</option>
            <option>Engineer</option>
            <option>Analyst</option>
            <option>Executive</option>
            <option>Specialist</option>
          </select>
          <select className={selectClass}>
            <option>All Countries</option>
            <option>United States</option>
            <option>United Kingdom</option>
            <option>India</option>
            <option>Brazil</option>
          </select>
          <select className={selectClass}>
            <option>All Statuses</option>
            <option>Active</option>
            <option>Inactive</option>
          </select>
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
              {EMPLOYEES.map((employee) => (
                <tr key={employee.code} className="border-b border-slate-100">
                  <td className="px-4 py-[13px] text-slate-600 font-mono">{employee.code}</td>
                  <td className="px-4 py-[13px] text-slate-800 font-semibold">{employee.name}</td>
                  <td className="px-4 py-[13px] text-slate-600">{employee.department}</td>
                  <td className="px-4 py-[13px] text-slate-600">{employee.role}</td>
                  <td className="px-4 py-[13px] text-slate-600">{employee.country}</td>
                  <td className="px-4 py-[13px]">
                    <StatusBadge status={employee.status} />
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between mt-4">
          <span className="text-[13px] text-slate-500">Showing 1–4 of 94 employees</span>
          <div className="flex gap-1.5 items-center">
            <button type="button" className={pageButtonClass}>
              Prev
            </button>
            <button type="button" className={activePageButtonClass}>
              1
            </button>
            <button type="button" className={pageButtonClass}>
              2
            </button>
            <button type="button" className={pageButtonClass}>
              3
            </button>
            <button type="button" className={pageButtonClass}>
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmployeeListPage
