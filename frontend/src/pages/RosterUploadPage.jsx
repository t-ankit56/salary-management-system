import { useState } from 'react'
import { Link } from 'react-router-dom'
import { uploadRoster } from '../api/imports'

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

/** Bulk-upload an Excel roster; all-or-nothing, with a Row/Error table on failure. */
function RosterUploadPage() {
  const [file, setFile] = useState(null)
  const [uploading, setUploading] = useState(false)
  const [result, setResult] = useState(null)
  const [errors, setErrors] = useState(null)

  async function handleUpload() {
    setUploading(true)
    setErrors(null)
    setResult(null)

    const { status, data } = await uploadRoster(file)

    setUploading(false)
    if (status === 201) {
      setResult(data)
    } else {
      setErrors(data?.errors ?? [])
    }
  }

  return (
    <div className="min-h-screen bg-slate-50 p-8">
      <div className="max-w-[700px] mx-auto">
        <h1 className="text-[22px] font-bold text-slate-800 m-0 mb-1.5">Upload Roster</h1>
        <p className="text-sm text-slate-500 m-0 mb-5">
          Upload an Excel file with one row per employee. Existing employees (matched by
          employee code) are updated; new ones are created. If any row fails validation,
          nothing is saved.
        </p>

        {result && (
          <div className="flex items-center justify-between flex-wrap gap-3 px-5 py-4 mb-4 bg-green-50 border border-green-200 rounded-lg">
            <div className="flex items-center gap-3">
              <span className="flex-shrink-0 w-[22px] h-[22px] rounded-full bg-green-600 text-white text-[13px] font-bold flex items-center justify-center">
                ✓
              </span>
              <span className="text-sm font-semibold text-green-800">
                {result.created} employees created, {result.updated} updated.
              </span>
            </div>
            <Link
              to="/employees"
              className="px-[18px] py-2.5 text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors"
            >
              View Employees
            </Link>
          </div>
        )}

        {errors && errors.length > 0 && (
          <>
            <div
              role="alert"
              className="flex items-center gap-2 px-3 py-2.5 mb-4 bg-red-50 border border-red-200 rounded-md text-red-700 text-[13px] leading-snug"
            >
              <span className="flex-shrink-0 w-4 h-4 rounded-full bg-red-500 text-white text-[11px] font-bold flex items-center justify-center">
                !
              </span>
              <span>Upload failed — fix the errors below and try again.</span>
            </div>

            <div className="bg-white border border-slate-200 rounded-lg overflow-hidden mb-4">
              <table className="w-full border-collapse text-sm">
                <thead>
                  <tr className="bg-slate-100">
                    <th className="text-left px-4 py-2.5 text-[11px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200 w-20">
                      Row
                    </th>
                    <th className="text-left px-4 py-2.5 text-[11px] font-bold text-slate-500 uppercase tracking-wide border-b border-slate-200">
                      Error
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {errors.map((err, index) => (
                    <tr key={index} className="border-b border-slate-100">
                      <td className="px-4 py-2 text-slate-600 font-mono">{err.row}</td>
                      <td className="px-4 py-2 text-slate-800">{err.error}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </>
        )}

        <div className="bg-white border border-slate-200 rounded-lg p-7">
          <div className="border-2 border-dashed border-slate-300 rounded-lg py-10 px-6 flex flex-col items-center gap-3 text-center">
            <UploadIcon />
            <div className="text-sm text-slate-600">
              <span className="font-semibold">Drag and drop</span> your file here, or
            </div>
            <label
              htmlFor="roster-file"
              className="px-4 py-2 text-[13px] font-semibold text-slate-600 bg-white border border-slate-300 rounded-md hover:bg-slate-50 transition-colors cursor-pointer"
            >
              Browse Files
            </label>
            <input
              id="roster-file"
              aria-label="Roster file"
              type="file"
              accept=".xlsx"
              className="hidden"
              onChange={(e) => setFile(e.target.files[0] ?? null)}
            />
            {file ? (
              <div className="text-xs text-slate-600 font-semibold">{file.name}</div>
            ) : (
              <div className="text-xs text-slate-400">.xlsx files only</div>
            )}
          </div>

          <div className="mt-5 flex justify-end">
            <button
              type="button"
              disabled={!file || uploading}
              onClick={handleUpload}
              className="px-5 py-2.5 text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors disabled:bg-slate-300 disabled:cursor-not-allowed disabled:hover:bg-slate-300"
            >
              {uploading ? 'Uploading…' : 'Upload'}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}

export default RosterUploadPage
