import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import EmployeeFormPage from './EmployeeFormPage'

function renderCreatePage() {
  return render(
    <MemoryRouter initialEntries={['/employees/new']}>
      <Routes>
        <Route path="/employees/new" element={<EmployeeFormPage />} />
        <Route path="/employees/:id" element={<div>Employee detail stub</div>} />
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

function fillForm() {
  fireEvent.change(screen.getByLabelText('Employee Code'), { target: { value: 'E100' } })
  fireEvent.change(screen.getByLabelText('First Name'), { target: { value: 'Jane' } })
  fireEvent.change(screen.getByLabelText('Last Name'), { target: { value: 'Doe' } })
  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'jane.doe@example.com' } })
  fireEvent.change(screen.getByLabelText('Department'), { target: { value: '3' } })
  fireEvent.change(screen.getByLabelText('Role'), { target: { value: '3' } })
  fireEvent.change(screen.getByLabelText('Country'), { target: { value: '3' } })
  fireEvent.change(screen.getByLabelText('Hire Date'), { target: { value: '2022-01-15' } })
  fireEvent.change(screen.getByLabelText('Opening Base'), { target: { value: '60000' } })
  fireEvent.change(screen.getByLabelText('Allowance'), { target: { value: '5000' } })
  fireEvent.change(screen.getByLabelText('Yearly Bonus'), { target: { value: '3000' } })
  fireEvent.change(screen.getByLabelText('Currency'), { target: { value: 'USD' } })
  fireEvent.change(screen.getByLabelText('Salary Effective From'), { target: { value: '2022-01-15' } })
}

function setupFetch(createResponse) {
  const fetchMock = vi.fn((url, options = {}) => {
    if (options.method === 'POST' && url.includes('/api/employees/')) {
      return Promise.resolve(createResponse)
    }
    if (url.includes('/api/departments/')) {
      return Promise.resolve(jsonResponse(200, [{ id: 3, name: 'Engineering', is_active: true }]))
    }
    if (url.includes('/api/roles/')) {
      return Promise.resolve(jsonResponse(200, [{ id: 3, name: 'Manager', is_active: true }]))
    }
    if (url.includes('/api/countries/')) {
      return Promise.resolve(jsonResponse(200, [{ id: 3, name: 'India', is_active: true }]))
    }
    return Promise.resolve(jsonResponse(200, null))
  })
  global.fetch = fetchMock
  return fetchMock
}

beforeEach(() => {
  vi.restoreAllMocks()
})

it('submits every field, with money fields as strings, to POST /api/employees/', async () => {
  const fetchMock = setupFetch(
    jsonResponse(201, {
      id: 9,
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
    }),
  )
  renderCreatePage()

  await waitFor(() => expect(screen.getByLabelText('Department').children.length).toBeGreaterThan(1))
  fillForm()
  fireEvent.click(screen.getByRole('button', { name: 'Create Employee' }))

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(
        ([url, options]) => options.method === 'POST' && url.includes('/api/employees/'),
      ),
    ).toBe(true),
  )
  const call = fetchMock.mock.calls.find(
    ([url, options]) => options.method === 'POST' && url.includes('/api/employees/'),
  )
  const body = JSON.parse(call[1].body)
  expect(body).toEqual({
    employee_code: 'E100',
    first_name: 'Jane',
    last_name: 'Doe',
    email: 'jane.doe@example.com',
    department: 3,
    role: 3,
    country: 3,
    hire_date: '2022-01-15',
    base: '60000',
    allowance: '5000',
    yearly_bonus: '3000',
    currency: 'USD',
    salary_effective_from: '2022-01-15',
  })
  expect(typeof body.base).toBe('string')
})

it('on 201, navigates to /employees/:new-id', async () => {
  setupFetch(
    jsonResponse(201, {
      id: 9,
      employee_code: 'E100',
      first_name: 'Jane',
      last_name: 'Doe',
    }),
  )
  renderCreatePage()

  await waitFor(() => expect(screen.getByLabelText('Department').children.length).toBeGreaterThan(1))
  fillForm()
  fireEvent.click(screen.getByRole('button', { name: 'Create Employee' }))

  await waitFor(() => expect(screen.getByText('Employee detail stub')).toBeInTheDocument())
})

it('a field-shaped 400 (missing fields, or a duplicate code/email) highlights each field and keeps the form as entered', async () => {
  setupFetch(
    jsonResponse(400, {
      email: ['This field is required.'],
      base: ['This field is required.'],
    }),
  )
  renderCreatePage()

  await waitFor(() => expect(screen.getByLabelText('Department').children.length).toBeGreaterThan(1))
  fireEvent.change(screen.getByLabelText('Employee Code'), { target: { value: 'E100' } })
  fireEvent.click(screen.getByRole('button', { name: 'Create Employee' }))

  await waitFor(() => expect(screen.getAllByText('This field is required.')).toHaveLength(2))
  expect(screen.getByLabelText('Employee Code')).toHaveValue('E100')
  expect(screen.queryByText('Employee detail stub')).not.toBeInTheDocument()
})
