import { Navigate, Route, Routes } from 'react-router-dom'
import { useAuth } from './hooks/useAuth'
import LoginPage from './pages/LoginPage'
import EmployeeListPage from './pages/EmployeeListPage'
import EmployeeDetailPage from './pages/EmployeeDetailPage'
import EmployeeFormPage from './pages/EmployeeFormPage'
import ReportsPage from './pages/ReportsPage'

function App() {
  const { user, login } = useAuth()

  if (!user) {
    return <LoginPage onLogin={login} />
  }

  return (
    <Routes>
      <Route path="/" element={<Navigate to="/employees" replace />} />
      <Route path="/login" element={<Navigate to="/employees" replace />} />
      <Route path="/employees" element={<EmployeeListPage />} />
      <Route path="/employees/new" element={<EmployeeFormPage />} />
      <Route path="/employees/:id" element={<EmployeeDetailPage />} />
      <Route path="/employees/:id/edit" element={<EmployeeFormPage />} />
      <Route path="/reports" element={<ReportsPage />} />
    </Routes>
  )
}

export default App
