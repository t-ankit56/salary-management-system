import { fireEvent, render, screen, waitFor, within } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import EmployeeDetailPage from './EmployeeDetailPage'

function renderPage(id = '3') {
  return render(
    <MemoryRouter initialEntries={[`/employees/${id}`]}>
      <Routes>
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
