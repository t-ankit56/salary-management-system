function UploadIcon() {
  return (
    <svg
      width="32"
      height="32"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="1.6"
      strokeLinecap="round"
      strokeLinejoin="round"
      className="text-slate-400"
    >
      <path d="M12 16V4" />
      <path d="M7 9l5-5 5 5" />
      <path d="M4 16v3a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2v-3" />
    </svg>
  )
}

function RosterUploadPage() {
  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-[700px] mx-auto">
        <h1 className="text-[22px] font-bold text-slate-800 m-0 mb-1.5">Upload Roster</h1>
        <p className="text-sm text-slate-500 m-0 mb-5">
          Upload an Excel file with one row per employee. Existing employees (matched by
          employee code) are updated; new ones are created. If any row fails validation,
          nothing is saved.
        </p>

        <div className="bg-white border border-slate-200 rounded-lg p-7">
          <div className="border-2 border-dashed border-slate-300 rounded-lg py-10 px-6 flex flex-col items-center gap-3 text-center">
            <UploadIcon />
            <div className="text-sm text-slate-600">
              <span className="font-semibold">Drag and drop</span> your file here, or
            </div>
            <button
              type="button"
              className="px-4 py-2 text-[13px] font-semibold text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors"
            >
              Browse Files
            </button>
            <div className="text-xs text-slate-400">.xlsx files only</div>
          </div>

          <div className="mt-5 flex justify-end">
            <button
              type="button"
              disabled
              className="px-5 py-2.5 text-sm font-semibold text-white bg-slate-300 rounded-md cursor-not-allowed"
            >
              Upload
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RosterUploadPage
