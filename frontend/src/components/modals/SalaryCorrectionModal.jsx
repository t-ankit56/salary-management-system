import { useState } from 'react'
import { correctSalaryPeriod } from '../../api/salary'

const initialForm = {
  base: '',
  allowance: '',
  yearly_bonus: '',
  reason: '',
}

/** Corrects a specific past salary period's amounts in place, with a required reason. */
function SalaryCorrectionModal({ employeeId, period, onClose, onSuccess }) {
  const [form, setForm] = useState(initialForm)
  const [bannerError, setBannerError] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})

  function updateField(key, value) {
    setForm((f) => ({ ...f, [key]: value }))
  }

  async function handleSubmit(e) {
    e.preventDefault()
    setBannerError('')
    setFieldErrors({})

    const { status, data } = await correctSalaryPeriod(employeeId, {
      salary_period: period.id,
      ...form,
    })

    if (status === 201) {
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
        className="w-full max-w-[440px] bg-white rounded-[10px] shadow-xl px-7 pt-7 pb-6"
      >
        <h2 className="text-lg font-bold text-slate-800 m-0 mb-1">Correct Salary</h2>
        <p className="text-[13px] text-slate-500 m-0 mb-[18px]">
          Correcting record for period {period.effective_from} – {period.effective_to ?? 'present'}.
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

        <div className="flex flex-col gap-3.5">
          <div className="flex gap-3">
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="correction_base" className="text-[13px] font-semibold text-slate-600">
                Base
              </label>
              <input
                id="correction_base"
                type="number"
                placeholder="0.00"
                value={form.base}
                onChange={(e) => updateField('base', e.target.value)}
                className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
              />
              {fieldErrors.base && (
                <span className="text-xs text-red-600">{fieldErrors.base[0]}</span>
              )}
            </div>
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="correction_allowance" className="text-[13px] font-semibold text-slate-600">
                Allowance
              </label>
              <input
                id="correction_allowance"
                type="number"
                placeholder="0.00"
                value={form.allowance}
                onChange={(e) => updateField('allowance', e.target.value)}
                className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
              />
              {fieldErrors.allowance && (
                <span className="text-xs text-red-600">{fieldErrors.allowance[0]}</span>
              )}
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="correction_yearly_bonus" className="text-[13px] font-semibold text-slate-600">
              Yearly Bonus
            </label>
            <input
              id="correction_yearly_bonus"
              type="number"
              placeholder="0.00"
              value={form.yearly_bonus}
              onChange={(e) => updateField('yearly_bonus', e.target.value)}
              className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
            />
            {fieldErrors.yearly_bonus && (
              <span className="text-xs text-red-600">{fieldErrors.yearly_bonus[0]}</span>
            )}
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="reason" className="text-[13px] font-semibold text-slate-600">
              Reason <span className="text-red-600">*</span>
            </label>
            <textarea
              id="reason"
              rows={3}
              placeholder="Explain the reason for this correction"
              value={form.reason}
              onChange={(e) => updateField('reason', e.target.value)}
              className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 resize-y focus:outline-none focus:border-blue-700"
            />
            {fieldErrors.reason && (
              <span className="text-xs text-red-600">{fieldErrors.reason[0]}</span>
            )}
          </div>
        </div>

        <div className="flex justify-end gap-2.5 mt-[22px]">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 text-sm font-semibold text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button
            type="submit"
            className="px-[18px] py-2.5 text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors"
          >
            Save
          </button>
        </div>
      </form>
    </div>
  )
}

export default SalaryCorrectionModal
