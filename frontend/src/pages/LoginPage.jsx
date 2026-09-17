import { useState } from 'react'
import acmeLogo from '../assets/acme-logo.webp'

/** Email/password login screen; the only page rendered when there's no session. */
function LoginPage({ onLogin }) {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    const result = await onLogin(email, password)
    if (!result.ok) {
      setError('Invalid email or password')
    }
  }

  return (
    <div className="min-h-screen w-full flex items-center justify-center bg-slate-50 p-6">
      <div className="w-full max-w-[400px] bg-white border border-slate-200 rounded-lg shadow-sm px-9 py-10">
        <div className="text-center mb-7">
          <img src={acmeLogo} alt="ACME Corporation" className="h-16 w-auto mx-auto mb-4" />
          <div className="text-xl font-bold text-slate-800 tracking-tight">
            Payroll &amp; Compensation Portal
          </div>
          <div className="text-[13px] text-slate-500 mt-1">Internal HR Access</div>
        </div>

        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label htmlFor="email" className="text-[13px] font-semibold text-slate-600">
              Email
            </label>
            <input
              id="email"
              name="email"
              type="email"
              autoComplete="username"
              required
              placeholder="you@company.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md bg-white text-slate-800 focus:outline-none focus:border-blue-700 focus:ring-4 focus:ring-blue-700/15"
            />
          </div>

          <div className="flex flex-col gap-1.5">
            <label htmlFor="password" className="text-[13px] font-semibold text-slate-600">
              Password
            </label>
            <input
              id="password"
              name="password"
              type="password"
              autoComplete="current-password"
              required
              placeholder="••••••••"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2.5 text-sm border border-slate-300 rounded-md bg-white text-slate-800 focus:outline-none focus:border-blue-700 focus:ring-4 focus:ring-blue-700/15"
            />
          </div>

          <button
            type="submit"
            className="mt-2 w-full py-[11px] text-sm font-semibold text-white bg-blue-700 rounded-md hover:bg-blue-800 transition-colors"
          >
            Log In
          </button>

          <div className="min-h-10">
            {error && (
              <div
                role="alert"
                className="flex items-start gap-2 px-3 py-2.5 bg-red-50 border border-red-200 rounded-md text-red-700 text-[13px] leading-snug"
              >
                <span className="flex-shrink-0 w-4 h-4 rounded-full bg-red-500 text-white text-[11px] font-bold flex items-center justify-center mt-px">
                  !
                </span>
                <span>{error}</span>
              </div>
            )}
          </div>
        </form>
      </div>
    </div>
  )
}

export default LoginPage
