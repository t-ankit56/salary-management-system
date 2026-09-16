function SalaryChangeModal({ onClose }) {
  return (
    <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-6 z-50">
      <div className="w-full max-w-[440px] bg-white rounded-[10px] shadow-xl px-7 pt-7 pb-6">
        <h2 className="text-lg font-bold text-slate-800 m-0 mb-1">Change Salary</h2>
        <p className="text-[13px] text-slate-500 m-0 mb-[18px]">
          Create a new salary record effective from a future date.
        </p>

        <div className="flex flex-col gap-3.5">
          <div className="flex gap-3">
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="base" className="text-[13px] font-semibold text-slate-600">
                Base
              </label>
              <input
                id="base"
                type="number"
                placeholder="0.00"
                className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
              />
            </div>
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="allowance" className="text-[13px] font-semibold text-slate-600">
                Allowance
              </label>
              <input
                id="allowance"
                type="number"
                placeholder="0.00"
                className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
              />
            </div>
          </div>

          <div className="flex gap-3">
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="yearly_bonus" className="text-[13px] font-semibold text-slate-600">
                Yearly Bonus
              </label>
              <input
                id="yearly_bonus"
                type="number"
                placeholder="0.00"
                className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
              />
            </div>
            <div className="flex-1 flex flex-col gap-1.5">
              <label htmlFor="currency" className="text-[13px] font-semibold text-slate-600">
                Currency
              </label>
              <select
                id="currency"
                className="w-full px-2.5 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 bg-white focus:outline-none focus:border-blue-700"
              >
                <option value="">Select currency</option>
                <option value="USD">USD</option>
                <option value="EUR">EUR</option>
                <option value="GBP">GBP</option>
                <option value="INR">INR</option>
              </select>
            </div>
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="effective_from" className="text-[13px] font-semibold text-slate-600">
              Effective From
            </label>
            <input
              id="effective_from"
              type="date"
              className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
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

export default SalaryChangeModal
