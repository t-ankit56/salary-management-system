import { Fragment, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import SalaryChangeModal from '../components/modals/SalaryChangeModal'
import SalaryCorrectionModal from '../components/modals/SalaryCorrectionModal'
import StatusChangeModal from '../components/modals/StatusChangeModal'
import { useEmployee } from '../hooks/useEmployee'
import { useSalaryHistory } from '../hooks/useSalaryHistory'

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

/** Employee profile, salary history, and the change/correction/status modals. */
function EmployeeDetailPage() {
  const { id } = useParams()
  const [openModal, setOpenModal] = useState(null)
  const [correctingPeriod, setCorrectingPeriod] = useState(null)
  const { employee, refetch: refetchEmployee } = useEmployee(id)
  const { history, expandedPeriodId, corrections, toggleCorrections, refetch: refetchHistory } =
    useSalaryHistory(id)

  if (!employee) {
    return null
  }

  const isActive = employee.status === 'active'

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-[960px] mx-auto">
        <Link
          to="/employees"
          className="inline-block text-[13px] font-semibold text-slate-600 hover:text-slate-800 mb-4"
        >
          ‹ Back to Employees
        </Link>
        <div className="bg-white border border-slate-200 rounded-lg px-7 py-6 mb-5">
          <div className="flex items-center gap-3 flex-wrap mb-1">
            <h1 className="text-[22px] font-bold text-slate-800 m-0">
              {employee.first_name} {employee.last_name}
            </h1>
            <span className="text-[13px] font-mono text-slate-500">{employee.employee_code}</span>
            <StatusBadge status={employee.status} />
          </div>
          <p className="text-[13px] text-slate-500 mt-0 mb-[18px]">
            {employee.department_name} · {employee.role_name} · {employee.country_name}
          </p>

          <div className="flex gap-2.5 flex-wrap">
            <button
              type="button"
              onClick={() => setOpenModal('change')}
              className="px-4 py-2.5 text-[13px] font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors"
            >
              Change Salary
            </button>
            <button
              type="button"
              onClick={() => setOpenModal('status')}
              className={
                isActive
                  ? 'px-4 py-2.5 text-[13px] font-semibold text-red-700 bg-white border border-red-300 rounded-md hover:bg-red-50 transition-colors'
                  : 'px-4 py-2.5 text-[13px] font-semibold text-green-700 bg-white border border-green-300 rounded-md hover:bg-green-50 transition-colors'
              }
            >
              {isActive ? 'Deactivate' : 'Reactivate'}
            </button>
            <Link
              to={`/employees/${employee.id}/edit`}
              className="px-4 py-2.5 text-[13px] font-semibold text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
            >
              Edit
            </Link>
          </div>
        </div>

        <div className="bg-white border border-slate-200 rounded-lg overflow-hidden">
          <div className="px-5 py-4 border-b border-slate-200 text-[15px] font-bold text-slate-800">
            Salary History
          </div>
          <table className="w-full border-collapse text-sm">
            <thead>
              <tr className="bg-slate-100">
                <th className="text-left px-4 py-[11px] text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Effective From
                </th>
                <th className="text-left px-4 py-[11px] text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Effective To
                </th>
                <th className="text-right px-4 py-[11px] text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Base
                </th>
                <th className="text-right px-4 py-[11px] text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Allowance
                </th>
                <th className="text-right px-4 py-[11px] text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Yearly Bonus
                </th>
                <th className="text-left px-4 py-[11px] text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Currency
                </th>
                <th className="text-center px-4 py-[11px] text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Corrections
                </th>
                <th className="text-right px-4 py-[11px] text-xs font-bold text-slate-500 uppercase tracking-wide">
                  Actions
                </th>
              </tr>
            </thead>
            <tbody>
              {history.map((period) => (
                <Fragment key={period.id}>
                  <tr className="border-b border-slate-100">
                    <td className="px-4 py-3 text-slate-600">{period.effective_from}</td>
                    <td className="px-4 py-3 text-slate-600">{period.effective_to ?? '—'}</td>
                    <td className="px-4 py-3 text-slate-800 text-right">{period.base}</td>
                    <td className="px-4 py-3 text-slate-800 text-right">{period.allowance}</td>
                    <td className="px-4 py-3 text-slate-800 text-right">{period.yearly_bonus}</td>
                    <td className="px-4 py-3 text-slate-600">{period.currency}</td>
                    <td className="px-4 py-3 text-center">
                      {period.correction_count > 0 ? (
                        <button
                          type="button"
                          onClick={() => toggleCorrections(period.id)}
                          className="font-semibold text-blue-700 underline cursor-pointer"
                        >
                          {period.correction_count}
                        </button>
                      ) : (
                        <span className="text-slate-500">{period.correction_count}</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right">
                      <button
                        type="button"
                        onClick={() => {
                          setCorrectingPeriod(period)
                          setOpenModal('correct')
                        }}
                        className="text-[13px] font-semibold text-blue-700 hover:text-blue-800"
                      >
                        Correct
                      </button>
                    </td>
                  </tr>
                  {expandedPeriodId === period.id && (
                    <tr className="border-b border-slate-100 bg-slate-50">
                      <td colSpan={8} className="px-4 py-3">
                        <div className="flex flex-col gap-2">
                          {corrections.map((correction) => (
                            <div key={correction.id} className="text-[13px] text-slate-600">
                              <span className="font-semibold text-slate-800">{correction.created_at}</span>{' '}
                              — base {correction.previous_base} → {correction.new_base}, allowance{' '}
                              {correction.previous_allowance} → {correction.new_allowance}, bonus{' '}
                              {correction.previous_yearly_bonus} → {correction.new_yearly_bonus}
                              <div className="text-slate-500">{correction.reason}</div>
                            </div>
                          ))}
                        </div>
                      </td>
                    </tr>
                  )}
                </Fragment>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {openModal === 'change' && (
        <SalaryChangeModal
          employeeId={employee.id}
          onClose={() => setOpenModal(null)}
          onSuccess={() => {
            refetchHistory()
            setOpenModal(null)
          }}
        />
      )}
      {openModal === 'correct' && correctingPeriod && (
        <SalaryCorrectionModal
          employeeId={employee.id}
          period={correctingPeriod}
          onClose={() => setOpenModal(null)}
          onSuccess={() => {
            refetchHistory()
            setOpenModal(null)
          }}
        />
      )}
      {openModal === 'status' && (
        <StatusChangeModal
          employeeId={employee.id}
          mode={isActive ? 'deactivate' : 'reactivate'}
          onClose={() => setOpenModal(null)}
          onSuccess={() => {
            refetchEmployee()
            setOpenModal(null)
          }}
        />
      )}
    </div>
  )
}

export default EmployeeDetailPage
