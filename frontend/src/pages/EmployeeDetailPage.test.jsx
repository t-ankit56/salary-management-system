import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import EmployeeDetailPage from './EmployeeDetailPage'

function renderPage(id = '3') {
  return render(
    <MemoryRouter initialEntries={[`/employees/${id}`]}>
      <Routes>
        <Route path="/employees" element={<div>Employee list stub</div>} />
        <Route path="/employees/:id" element={<EmployeeDetailPage />} />
      </Routes>
    </MemoryRouter>,
  )
}

function jsonResponse(status, body) {
  return {
    status,
    text: () => Promise.resolve(body === undefined ? '' : JSON.stringify(body)),
  }
}

const EMPLOYEE = {
  id: 3,
  employee_code: 'E100',
  first_name: 'Jane',
  last_name: 'Doe',
  email: 'jane.doe@example.com',
  department: 3,
  department_name: 'Engineering',
  role: 3,
  role_name: 'Manager',
  country: 3,
  country_name: 'India',
  status: 'active',
  hire_date: '2022-01-15',
  created_at: '2026-09-16T17:21:36.466778Z',
  updated_at: '2026-09-16T17:21:36.466798Z',
}

const HISTORY = [
  {
    id: 3,
    base: '65000.00',
    allowance: '5000.00',
    yearly_bonus: '3000.00',
    currency: 'USD',
    effective_from: '2023-01-01',
    effective_to: null,
    correction_count: 0,
  },
  {
    id: 2,
    base: '60000.00',
    allowance: '5000.00',
    yearly_bonus: '3000.00',
    currency: 'USD',
    effective_from: '2022-01-15',
    effective_to: '2023-01-01',
    correction_count: 1,
  },
]

const CORRECTIONS = [
  {
    id: 1,
    salary_period: 2,
    previous_base: '60000.00',
    previous_allowance: '5000.00',
    previous_yearly_bonus: '3000.00',
    new_base: '61000.00',
    new_allowance: '5000.00',
    new_yearly_bonus: '3000.00',
    reason: 'Data entry error',
    created_by: 3,
    created_at: '2026-09-16T17:22:11.039274Z',
  },
]

function setupFetch() {
  const fetchMock = vi.fn((url) => {
    if (url.includes('/salary-periods/2/corrections/')) {
      return Promise.resolve(jsonResponse(200, CORRECTIONS))
    }
    if (url.includes('/salary-periods/')) {
      return Promise.resolve(jsonResponse(200, HISTORY))
    }
    return Promise.resolve(jsonResponse(200, EMPLOYEE))
  })
  global.fetch = fetchMock
  return fetchMock
}

beforeEach(() => {
  vi.restoreAllMocks()
})

it('requests the employee and salary history on mount and renders both', async () => {
  const fetchMock = setupFetch()
  renderPage()

  await waitFor(() => expect(screen.getByText('Jane Doe')).toBeInTheDocument())

  expect(fetchMock.mock.calls.some(([url]) => url.includes('/api/employees/3/'))).toBe(true)
  expect(
    fetchMock.mock.calls.some(([url]) => url.includes('/api/employees/3/salary-periods/')),
  ).toBe(true)

  expect(screen.getByText(/Engineering/)).toBeInTheDocument()
  expect(screen.getByText(/Manager/)).toBeInTheDocument()
  expect(screen.getByText(/India/)).toBeInTheDocument()
  expect(screen.getByRole('cell', { name: '65000.00' })).toBeInTheDocument()
  expect(screen.getByRole('cell', { name: '60000.00' })).toBeInTheDocument()
})

it('renders history rows in the order returned, newest first, with correction counts', async () => {
  setupFetch()
  renderPage()

  await waitFor(() => expect(screen.getByText('Jane Doe')).toBeInTheDocument())

  const rows = screen.getAllByRole('row').slice(1) // drop header row
  expect(within(rows[0]).getByText('2023-01-01')).toBeInTheDocument()
  expect(within(rows[1]).getByText('2022-01-15')).toBeInTheDocument()
  expect(within(rows[1]).getByText('1')).toBeInTheDocument()
})

it('clicking a row with a nonzero correction count fetches and displays its corrections log', async () => {
  const fetchMock = setupFetch()
  renderPage()

  await waitFor(() => expect(screen.getByText('Jane Doe')).toBeInTheDocument())

  fireEvent.click(screen.getByRole('button', { name: '1' }))

  await waitFor(() => expect(screen.getByText('Data entry error')).toBeInTheDocument())
  expect(
    fetchMock.mock.calls.some(([url]) => url.includes('/salary-periods/2/corrections/')),
  ).toBe(true)
})

it('when status is active, the button opens StatusChangeModal in deactivate mode and posts to the deactivate endpoint', async () => {
  const fetchMock = vi.fn((url, options = {}) => {
    if (options.method === 'POST' && url.includes('/deactivate/')) {
      return Promise.resolve(jsonResponse(200))
    }
    if (url.includes('/salary-periods/')) {
      return Promise.resolve(jsonResponse(200, HISTORY))
    }
    return Promise.resolve(jsonResponse(200, EMPLOYEE))
  })
  global.fetch = fetchMock
  renderPage()

  await waitFor(() => expect(screen.getByText('Jane Doe')).toBeInTheDocument())

  fireEvent.click(screen.getByRole('button', { name: 'Deactivate' }))
  expect(screen.getByText('Deactivate Employee')).toBeInTheDocument()

  fireEvent.change(screen.getByLabelText('Effective Date'), { target: { value: '2024-01-01' } })
  const confirmButtons = screen.getAllByRole('button', { name: 'Deactivate' })
  fireEvent.click(confirmButtons[confirmButtons.length - 1])

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(
        ([url, options]) => options.method === 'POST' && url.includes('/api/employees/3/deactivate/'),
      ),
    ).toBe(true),
  )
  const call = fetchMock.mock.calls.find(([url]) => url.includes('/deactivate/'))
  expect(JSON.parse(call[1].body)).toEqual({ effective_date: '2024-01-01' })
})

it('when status is inactive, the button opens StatusChangeModal in reactivate mode and posts to the reactivate endpoint', async () => {
  const inactiveEmployee = { ...EMPLOYEE, id: 5, status: 'inactive' }
  const fetchMock = vi.fn((url, options = {}) => {
    if (options.method === 'POST' && url.includes('/reactivate/')) {
      return Promise.resolve(jsonResponse(200))
    }
    if (url.includes('/salary-periods/')) {
      return Promise.resolve(jsonResponse(200, HISTORY))
    }
    return Promise.resolve(jsonResponse(200, inactiveEmployee))
  })
  global.fetch = fetchMock
  renderPage('5')

  await waitFor(() => expect(screen.getByText('Jane Doe')).toBeInTheDocument())

  fireEvent.click(screen.getByRole('button', { name: 'Reactivate' }))
  expect(screen.getByText('Reactivate Employee')).toBeInTheDocument()

  fireEvent.change(screen.getByLabelText('Effective Date'), { target: { value: '2024-06-01' } })
  const confirmButtons = screen.getAllByRole('button', { name: 'Reactivate' })
  fireEvent.click(confirmButtons[confirmButtons.length - 1])

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(
        ([url, options]) => options.method === 'POST' && url.includes('/api/employees/5/reactivate/'),
      ),
    ).toBe(true),
  )
})

it('on success, the employee is refetched and the status badge/button label update', async () => {
  let employeeGetCount = 0
  const fetchMock = vi.fn((url, options = {}) => {
    if (options.method === 'POST' && url.includes('/deactivate/')) {
      return Promise.resolve(jsonResponse(200))
    }
    if (url.includes('/salary-periods/')) {
      return Promise.resolve(jsonResponse(200, HISTORY))
    }
    employeeGetCount += 1
    const status = employeeGetCount === 1 ? 'active' : 'inactive'
    return Promise.resolve(jsonResponse(200, { ...EMPLOYEE, status }))
  })
  global.fetch = fetchMock
  renderPage()

  await waitFor(() => expect(screen.getByText('Active')).toBeInTheDocument())

  fireEvent.click(screen.getByRole('button', { name: 'Deactivate' }))
  fireEvent.change(screen.getByLabelText('Effective Date'), { target: { value: '2024-01-01' } })
  const confirmButtons = screen.getAllByRole('button', { name: 'Deactivate' })
  fireEvent.click(confirmButtons[confirmButtons.length - 1])

  await waitFor(() => expect(screen.getByText('Inactive')).toBeInTheDocument())
  expect(screen.getByRole('button', { name: 'Reactivate' })).toBeInTheDocument()
})

it('a {detail} 400 (e.g. already inactive) shows as a banner in the modal', async () => {
  const fetchMock = vi.fn((url, options = {}) => {
    if (options.method === 'POST' && url.includes('/deactivate/')) {
      return Promise.resolve(jsonResponse(400, { detail: 'Employee is already inactive' }))
    }
    if (url.includes('/salary-periods/')) {
      return Promise.resolve(jsonResponse(200, HISTORY))
    }
    return Promise.resolve(jsonResponse(200, EMPLOYEE))
  })
  global.fetch = fetchMock
  renderPage()

  await waitFor(() => expect(screen.getByText('Jane Doe')).toBeInTheDocument())

  fireEvent.click(screen.getByRole('button', { name: 'Deactivate' }))
  fireEvent.change(screen.getByLabelText('Effective Date'), { target: { value: '2024-01-01' } })
  const confirmButtons = screen.getAllByRole('button', { name: 'Deactivate' })
  fireEvent.click(confirmButtons[confirmButtons.length - 1])

  await waitFor(() =>
    expect(screen.getByRole('alert')).toHaveTextContent('Employee is already inactive'),
  )
})

it('a back link navigates to the employees list', async () => {
  setupFetch()
  renderPage()

  await waitFor(() => expect(screen.getByText('Jane Doe')).toBeInTheDocument())

  fireEvent.click(screen.getByRole('link', { name: /Back/ }))

  expect(screen.getByText('Employee list stub')).toBeInTheDocument()
})
