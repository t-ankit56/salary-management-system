import { useState } from 'react'
import { deactivateEmployee, reactivateEmployee } from '../../api/employees'

const confirmButtonClass = {
  deactivate:
    'px-[18px] py-2.5 text-sm font-semibold text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors',
  reactivate:
    'px-[18px] py-2.5 text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors',
}

function StatusChangeModal({ employeeId, mode, onClose, onSuccess }) {
  const isDeactivate = mode === 'deactivate'
  const [effectiveDate, setEffectiveDate] = useState('')
  const [bannerError, setBannerError] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})

  async function handleSubmit(e) {
    e.preventDefault()
    setBannerError('')
    setFieldErrors({})

    const changeStatus = isDeactivate ? deactivateEmployee : reactivateEmployee
    const { status, data } = await changeStatus(employeeId, effectiveDate)

    if (status === 200) {
      onSuccess()
      return
    }
    if (data?.detail) {
      setBannerError(data.detail)
    } else {
      setFieldErrors(data ?? {})
    }
  }

  return (
    <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-6 z-50">
      <form
        onSubmit={handleSubmit}
        className="w-full max-w-[400px] bg-white rounded-[10px] shadow-xl px-7 pt-7 pb-6"
      >
        <h2 className="text-lg font-bold text-slate-800 m-0 mb-1">
          {isDeactivate ? 'Deactivate Employee' : 'Reactivate Employee'}
        </h2>
        <p className="text-[13px] text-slate-500 m-0 mb-[18px]">
          {isDeactivate
            ? 'This employee will lose access as of the effective date.'
            : 'This employee will regain access as of the effective date.'}
        </p>

        {bannerError && (
          <div
            role="alert"
            className="flex items-start gap-2 px-3 py-2.5 mb-4 bg-red-50 border border-red-200 rounded-md text-red-700 text-[13px] leading-snug"
          >
            <span className="flex-shrink-0 w-4 h-4 rounded-full bg-red-500 text-white text-[11px] font-bold flex items-center justify-center mt-px">
              !
            </span>
            <span>{bannerError}</span>
          </div>
        )}

        <div className="flex flex-col gap-1.5">
          <label htmlFor="effective_date" className="text-[13px] font-semibold text-slate-600">
            Effective Date
          </label>
          <input
            id="effective_date"
            type="date"
            value={effectiveDate}
            onChange={(e) => setEffectiveDate(e.target.value)}
            className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
          />
          {fieldErrors.effective_date && (
            <span className="text-xs text-red-600">{fieldErrors.effective_date[0]}</span>
          )}
        </div>

        <div className="flex justify-end gap-2.5 mt-[22px]">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 text-sm font-semibold text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button type="submit" className={confirmButtonClass[isDeactivate ? 'deactivate' : 'reactivate']}>
            {isDeactivate ? 'Deactivate' : 'Reactivate'}
          </button>
        </div>
      </form>
    </div>
  )
}

export default StatusChangeModal
