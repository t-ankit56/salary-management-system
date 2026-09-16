const confirmButtonClass = {
  deactivate:
    'px-[18px] py-2.5 text-sm font-semibold text-white bg-red-600 rounded-md hover:bg-red-700 transition-colors',
  reactivate:
    'px-[18px] py-2.5 text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors',
}

function StatusChangeModal({ mode, onClose }) {
  const isDeactivate = mode === 'deactivate'

  return (
    <div className="fixed inset-0 bg-slate-900/50 flex items-center justify-center p-6 z-50">
      <div className="w-full max-w-[400px] bg-white rounded-[10px] shadow-xl px-7 pt-7 pb-6">
        <h2 className="text-lg font-bold text-slate-800 m-0 mb-1">
          {isDeactivate ? 'Deactivate Employee' : 'Reactivate Employee'}
        </h2>
        <p className="text-[13px] text-slate-500 m-0 mb-[18px]">
          {isDeactivate
            ? 'This employee will lose access as of the effective date.'
            : 'This employee will regain access as of the effective date.'}
        </p>

        <div className="flex flex-col gap-1.5">
          <label htmlFor="effective_date" className="text-[13px] font-semibold text-slate-600">
            Effective Date
          </label>
          <input
            id="effective_date"
            type="date"
            className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md text-slate-800 focus:outline-none focus:border-blue-700"
          />
        </div>

        <div className="flex justify-end gap-2.5 mt-[22px]">
          <button
            type="button"
            onClick={onClose}
            className="px-4 py-2.5 text-sm font-semibold text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
          >
            Cancel
          </button>
          <button type="button" className={confirmButtonClass[isDeactivate ? 'deactivate' : 'reactivate']}>
            {isDeactivate ? 'Deactivate' : 'Reactivate'}
          </button>
        </div>
      </div>
    </div>
  )
}

export default StatusChangeModal
