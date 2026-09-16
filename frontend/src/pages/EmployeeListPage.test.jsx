import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import EmployeeListPage from './EmployeeListPage'

function renderPage() {
  return render(
    <MemoryRouter>
      <EmployeeListPage />
    </MemoryRouter>,
  )
}

function jsonResponse(status, body) {
  return {
    status,
    text: () => Promise.resolve(body === undefined ? '' : JSON.stringify(body)),
  }
}

function employeeRow(overrides = {}) {
  return {
    id: 3,
    employee_code: 'E100',
    first_name: 'Jane',
    last_name: 'Doe',
    email: 'jane.doe@example.com',
    department: 3,
    department_name: 'Engineering',
    role: 5,
    role_name: 'Manager',
    country: 7,
    country_name: 'India',
    status: 'active',
    hire_date: '2022-01-15',
    created_at: '2026-09-16T17:21:36.466778Z',
    updated_at: '2026-09-16T17:21:36.466798Z',
    ...overrides,
  }
}

function setupFetch({ count = 1, next = null, results } = {}) {
  const fetchMock = vi.fn()
  fetchMock.mockResolvedValueOnce(jsonResponse(200, [{ id: 3, name: 'Engineering', is_active: true }]))
  fetchMock.mockResolvedValueOnce(jsonResponse(200, [{ id: 5, name: 'Manager', is_active: true }]))
  fetchMock.mockResolvedValueOnce(jsonResponse(200, [{ id: 7, name: 'India', is_active: true }]))
  fetchMock.mockResolvedValue(
    jsonResponse(200, {
      count,
      next,
      previous: null,
      results: results ?? [employeeRow()],
    }),
  )
  global.fetch = fetchMock
  return fetchMock
}

beforeEach(() => {
  vi.restoreAllMocks()
})

it('selecting a department filter re-requests employees with the other filters preserved', async () => {
  const fetchMock = setupFetch()
  renderPage()

  await waitFor(() => expect(fetchMock.mock.calls.length).toBeGreaterThanOrEqual(4))

  fireEvent.change(screen.getByLabelText('Status'), { target: { value: 'active' } })
  await waitFor(() => expect(fetchMock.mock.calls.at(-1)[0]).toContain('status=active'))

  fireEvent.change(screen.getByLabelText('Department'), { target: { value: '3' } })
  await waitFor(() => {
    const url = fetchMock.mock.calls.at(-1)[0]
    expect(url).toContain('department=3')
    expect(url).toContain('status=active')
  })
})

it('typing in search re-requests with the search term', async () => {
  const fetchMock = setupFetch()
  renderPage()

  await waitFor(() => expect(fetchMock.mock.calls.length).toBeGreaterThanOrEqual(4))

  fireEvent.change(screen.getByPlaceholderText('Search by name or employee code'), {
    target: { value: 'Jane' },
  })

  await waitFor(() => expect(fetchMock.mock.calls.at(-1)[0]).toContain('search=Jane'))
})

it('renders department_name/role_name/country_name/status from the response, not raw ids', async () => {
  setupFetch()
  renderPage()

  await waitFor(() => expect(screen.getByText('Jane Doe')).toBeInTheDocument())
  expect(screen.getByText('Engineering')).toBeInTheDocument()
  expect(screen.getByText('Manager')).toBeInTheDocument()
  expect(screen.getByText('India')).toBeInTheDocument()
  expect(screen.getByText('Active')).toBeInTheDocument()
})

it('changing page re-requests with the page param and does not follow the next URL from the response', async () => {
  const fetchMock = setupFetch({
    count: 30,
    next: 'http://example-host:9999/api/employees/?page=2',
    results: [employeeRow()],
  })
  renderPage()

  await waitFor(() => expect(screen.getByRole('button', { name: '2' })).toBeInTheDocument())

  fireEvent.click(screen.getByRole('button', { name: '2' }))

  await waitFor(() => {
    const url = fetchMock.mock.calls.at(-1)[0]
    expect(url).toContain('page=2')
    expect(url).not.toContain('example-host')
  })
})
