import { useState } from 'react'

const REPORTS = [
  {
    title: 'Total Payroll Cost',
    excluded: 3,
    rows: [{ label: 'All Employees (USD)', value: '$2,450,000' }],
  },
  {
    title: 'Headcount by Department',
    excluded: 2,
    rows: [
      { label: 'Engineering', value: '42' },
      { label: 'Sales', value: '28' },
      { label: 'Finance', value: '15' },
      { label: 'HR', value: '9' },
    ],
  },
  {
    title: 'Headcount by Country',
    excluded: 1,
    rows: [
      { label: 'United States', value: '38' },
      { label: 'India', value: '22' },
      { label: 'Brazil', value: '14' },
      { label: 'United Kingdom', value: '12' },
    ],
  },
  {
    title: 'Average Salary by Department',
    excluded: 2,
    rows: [
      { label: 'Engineering', value: '$98,200' },
      { label: 'Sales', value: '$76,400' },
      { label: 'Finance', value: '$84,900' },
      { label: 'HR', value: '$71,300' },
    ],
  },
  {
    title: 'Average Salary by Country',
    excluded: 1,
    rows: [
      { label: 'United States', value: '$92,000' },
      { label: 'India', value: '$58,000' },
      { label: 'Brazil', value: '$61,500' },
      { label: 'United Kingdom', value: '$88,000' },
    ],
  },
  {
    title: 'Average Bonus by Department',
    excluded: 4,
    rows: [
      { label: 'Engineering', value: '$8,200' },
      { label: 'Sales', value: '$12,400' },
      { label: 'Finance', value: '$6,900' },
      { label: 'HR', value: '$4,300' },
    ],
  },
]

function ReportsPage() {
  const [asOf, setAsOf] = useState('')
  const [hasError] = useState(false)

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

        {hasError && (
          <div
            role="alert"
            className="flex items-start gap-2 px-3 py-2.5 mb-5 bg-red-50 border border-red-200 rounded-md text-red-700 text-[13px] leading-snug"
          >
            <span className="flex-shrink-0 w-4 h-4 rounded-full bg-red-500 text-white text-[11px] font-bold flex items-center justify-center mt-px">
              !
            </span>
            <span>The selected date is earlier than the earliest available payroll record.</span>
          </div>
        )}

        <div className="grid grid-cols-3 gap-4">
          {REPORTS.map((report) => (
            <div
              key={report.title}
              className="bg-white border border-slate-200 rounded-lg px-[18px] pt-[18px] pb-3.5 min-w-0"
            >
              <div className="text-sm font-bold text-slate-800 mb-3">{report.title}</div>
              <table className="w-full border-collapse text-[13px]">
                <tbody>
                  {report.rows.map((row) => (
                    <tr key={row.label} className="border-b border-slate-100">
                      <td className="py-1.5 text-slate-600">{row.label}</td>
                      <td className="py-1.5 text-slate-800 font-semibold text-right">{row.value}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
              <div className="mt-3 text-[11px] text-slate-400 text-right">
                Excluded: {report.excluded}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}

export default ReportsPage
