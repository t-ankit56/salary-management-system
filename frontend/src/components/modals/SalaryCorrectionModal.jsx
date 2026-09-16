function SalaryCorrectionModal({ period, onClose }) {
  return (
    <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-6 z-50">
      <div className="w-full max-w-[440px] bg-white rounded-[10px] shadow-xl px-7 pt-7 pb-6">
        <h2 className="text-lg font-bold text-slate-800 m-0 mb-1">Correct Salary</h2>
        <p className="text-[13px] text-slate-500 m-0 mb-[18px]">
          Correcting record for period {period.effective_from} – {period.effective_to ?? 'present'}.
        </p>

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
                className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
              />
            </div>
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="correction_allowance" className="text-[13px] font-semibold text-slate-600">
                Allowance
              </label>
              <input
                id="correction_allowance"
                type="number"
                placeholder="0.00"
                className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
              />
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
              className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="reason" className="text-[13px] font-semibold text-slate-600">
              Reason <span className="text-red-600">*</span>
            </label>
            <textarea
              id="reason"
              required
              rows={3}
              placeholder="Explain the reason for this correction"
              className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 resize-y focus:outline-none focus:border-blue-700"
            />
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
            type="button"
            className="px-[18px] py-2.5 text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors"
          >
            Save
          </button>
        </div>
      </div>
    </div>
  )
}

export default SalaryCorrectionModal
