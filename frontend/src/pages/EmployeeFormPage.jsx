import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'
import { listCountries, listDepartments, listRoles } from '../api/employees'

const initialForm = {
  employee_code: '',
  first_name: '',
  last_name: '',
  email: '',
  department: '',
  role: '',
  country: '',
  hire_date: '',
  base: '',
  allowance: '',
  yearly_bonus: '',
  currency: '',
  salary_effective_from: '',
}

const labelClass = 'text-[13px] font-semibold text-slate-600'
const inputClass =
  'w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700'
const selectClass =
  'w-full px-2.5 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 bg-white focus:outline-none focus:border-blue-700'

function EmployeeFormPage() {
  const { id } = useParams()
  const isEdit = Boolean(id)

  const [form, setForm] = useState(initialForm)
  const [departments, setDepartments] = useState([])
  const [roles, setRoles] = useState([])
  const [countries, setCountries] = useState([])

  useEffect(() => {
    listDepartments().then(({ data }) => setDepartments(data ?? []))
    listRoles().then(({ data }) => setRoles(data ?? []))
    listCountries().then(({ data }) => setCountries(data ?? []))
  }, [])

  function updateField(key, value) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-[760px] mx-auto">
        <h1 className="text-[22px] font-bold text-slate-800 m-0 mb-5">
          {isEdit ? 'Edit Employee' : 'New Employee'}
        </h1>

        <div className="bg-white border border-slate-200 rounded-lg p-7">
          <div className="grid grid-cols-2 gap-4">
            <div className="flex flex-col gap-1.5">
              <label htmlFor="employee_code" className={labelClass}>
                Employee Code
              </label>
              <input
                id="employee_code"
                value={form.employee_code}
                onChange={(e) => updateField('employee_code', e.target.value)}
                className={inputClass}
              />
            </div>
            <div />
            <div className="flex flex-col gap-1.5">
              <label htmlFor="first_name" className={labelClass}>
                First Name
              </label>
              <input
                id="first_name"
                value={form.first_name}
                onChange={(e) => updateField('first_name', e.target.value)}
                className={inputClass}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label htmlFor="last_name" className={labelClass}>
                Last Name
              </label>
              <input
                id="last_name"
                value={form.last_name}
                onChange={(e) => updateField('last_name', e.target.value)}
                className={inputClass}
              />
            </div>
            <div className="flex flex-col gap-1.5 col-span-2">
              <label htmlFor="email" className={labelClass}>
                Email
              </label>
              <input
                id="email"
                type="email"
                value={form.email}
                onChange={(e) => updateField('email', e.target.value)}
                className={inputClass}
              />
            </div>
            <div className="flex flex-col gap-1.5">
              <label htmlFor="department" className={labelClass}>
                Department
              </label>
              <select
                id="department"
                value={form.department}
                onChange={(e) => updateField('department', e.target.value)}
                className={selectClass}
              >
                <option value="">Select department</option>
                {departments.map((department) => (
                  <option key={department.id} value={department.id}>
                    {department.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label htmlFor="role" className={labelClass}>
                Role
              </label>
              <select
                id="role"
                value={form.role}
                onChange={(e) => updateField('role', e.target.value)}
                className={selectClass}
              >
                <option value="">Select role</option>
                {roles.map((role) => (
                  <option key={role.id} value={role.id}>
                    {role.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label htmlFor="country" className={labelClass}>
                Country
              </label>
              <select
                id="country"
                value={form.country}
                onChange={(e) => updateField('country', e.target.value)}
                className={selectClass}
              >
                <option value="">Select country</option>
                {countries.map((country) => (
                  <option key={country.id} value={country.id}>
                    {country.name}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex flex-col gap-1.5">
              <label htmlFor="hire_date" className={labelClass}>
                Hire Date
              </label>
              <input
                id="hire_date"
                type="date"
                value={form.hire_date}
                onChange={(e) => updateField('hire_date', e.target.value)}
                className={inputClass}
              />
            </div>
          </div>

          {!isEdit && (
            <div className="mt-7 pt-5 border-t border-slate-200">
              <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wide mb-4">
                Initial Salary
              </h2>
              <div className="grid grid-cols-2 gap-4">
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="base" className={labelClass}>
                    Opening Base
                  </label>
                  <input
                    id="base"
                    type="number"
                    placeholder="0.00"
                    value={form.base}
                    onChange={(e) => updateField('base', e.target.value)}
                    className={inputClass}
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="allowance" className={labelClass}>
                    Allowance
                  </label>
                  <input
                    id="allowance"
                    type="number"
                    placeholder="0.00"
                    value={form.allowance}
                    onChange={(e) => updateField('allowance', e.target.value)}
                    className={inputClass}
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="yearly_bonus" className={labelClass}>
                    Yearly Bonus
                  </label>
                  <input
                    id="yearly_bonus"
                    type="number"
                    placeholder="0.00"
                    value={form.yearly_bonus}
                    onChange={(e) => updateField('yearly_bonus', e.target.value)}
                    className={inputClass}
                  />
                </div>
                <div className="flex flex-col gap-1.5">
                  <label htmlFor="currency" className={labelClass}>
                    Currency
                  </label>
                  <select
                    id="currency"
                    value={form.currency}
                    onChange={(e) => updateField('currency', e.target.value)}
                    className={selectClass}
                  >
                    <option value="">Select currency</option>
                    <option value="USD">USD</option>
                    <option value="EUR">EUR</option>
                    <option value="GBP">GBP</option>
                    <option value="INR">INR</option>
                  </select>
                </div>
                <div className="flex flex-col gap-1.5 col-span-2">
                  <label htmlFor="salary_effective_from" className={labelClass}>
                    Salary Effective From
                  </label>
                  <input
                    id="salary_effective_from"
                    type="date"
                    value={form.salary_effective_from}
                    onChange={(e) => updateField('salary_effective_from', e.target.value)}
                    className={inputClass}
                  />
                </div>
              </div>
            </div>
          )}

          <div className="flex justify-end gap-2.5 mt-7 pt-5 border-t border-slate-200">
            <button
              type="button"
              className="px-4 py-2.5 text-sm font-semibold text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
            >
              Cancel
            </button>
            <button
              type="button"
              className="px-5 py-2.5 text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors"
            >
              {isEdit ? 'Save Changes' : 'Create Employee'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default EmployeeFormPage
