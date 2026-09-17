import { NavLink } from 'react-router-dom'
import acmeLogo from '../assets/acme-logo.webp'

function linkClass({ isActive }) {
  return `px-3 py-2 text-sm font-semibold rounded-md transition-colors ${
    isActive ? 'bg-blue-700 text-white' : 'text-slate-600 hover:bg-slate-100'
  }`
}

/** Top nav bar shown on every authenticated page: page links plus Log Out. */
function NavBar({ onLogout }) {
  return (
    <nav className="bg-white border-b border-slate-200 px-8 py-3 flex items-center gap-2">
      <img src={acmeLogo} alt="ACME Corporation" className="h-8 w-auto mr-4" />
      <NavLink to="/employees" className={linkClass}>
        Employees
      </NavLink>
      <NavLink to="/reports" className={linkClass}>
        Reports
      </NavLink>
      <NavLink to="/roster-upload" className={linkClass}>
        Upload Roster
      </NavLink>
      <button
        type="button"
        onClick={onLogout}
        className="ml-auto px-3 py-2 text-sm font-semibold text-slate-600 hover:text-slate-800"
      >
        Log Out
      </button>
    </nav>
  )
}

export default NavBar
