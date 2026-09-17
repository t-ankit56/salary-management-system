import { useState } from 'react'
import { useReports } from '../hooks/useReports'

function formatMoney(value) {
  return `$${value}`
}

function todayString() {
  const now = new Date()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  return `${now.getFullYear()}-${month}-${day}`
}

function toRows(value) {
  if (typeof value === 'object' && value !== null) {
    return Object.entries(value).map(([label, amount]) => ({
      label,
      value: typeof amount === 'string' ? formatMoney(amount) : String(amount),
    }))
  }
  return [{ label: 'All Employees', value: formatMoney(value) }]
}

const REPORT_DEFS = [
  { name: 'total_payroll_cost', title: 'Total Payroll Cost' },
  { name: 'headcount_by_department', title: 'Headcount by Department' },
  { name: 'headcount_by_country', title: 'Headcount by Country' },
  { name: 'average_salary_by_department', title: 'Average Salary by Department' },
  { name: 'average_salary_by_country', title: 'Average Salary by Country' },
  { name: 'average_bonus_by_department', title: 'Average Bonus by Department' },
]

function ReportsPage() {
  const [asOf, setAsOf] = useState(todayString)
  const { reports, error } = useReports(asOf)

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-[1240px] mx-auto">
        <div className="flex items-center justify-between flex-wrap gap-4 mb-5">
          <h1 className="text-[22px] font-bold text-slate-800 m-0">Payroll Reports</h1>
          <div className="flex items-center gap-2.5">
            <label htmlFor="as_of" className="text-[13px] font-semibold text-slate-600">
              As Of
            </label>
            <input
              id="as_of"
              type="date"
              value={asOf}
              onChange={(e) => setAsOf(e.target.value)}
              className="px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
            />
          </div>
        </div>

        {error && (
          <div
            role="alert"
            className="flex items-start gap-2 px-3 py-2.5 mb-5 bg-red-50 border border-red-200 rounded-md text-red-700 text-[13px] leading-snug"
          >
            <span className="flex-shrink-0 w-4 h-4 rounded-full bg-red-500 text-white text-[11px] font-bold flex items-center justify-center mt-px">
              !
            </span>
            <span>
              {error.detail} Earliest available date: {error.earliestAvailableDate}.
            </span>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4">
          {REPORT_DEFS.map((def) => {
            const report = reports[def.name]
            return (
              <div
                key={def.name}
                className="bg-white border border-slate-200 rounded-lg px-[18px] pt-[18px] pb-3.5 min-w-0"
              >
                <div className="text-sm font-bold text-slate-800 mb-3">{def.title}</div>
                <table className="w-full border-collapse text-[13px]">
                  <tbody>
                    {report &&
                      toRows(report.value).map((row) => (
                        <tr key={row.label} className="border-b border-slate-100">
                          <td className="py-1.5 text-slate-600">{row.label}</td>
                          <td className="py-1.5 text-slate-800 font-semibold text-right">
                            {row.value}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
                {report && (
                  <div className="mt-3 text-[11px] text-slate-400 text-right">
                    Excluded: {report.excluded_count}
                  </div>
                )}
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}

export default ReportsPage
