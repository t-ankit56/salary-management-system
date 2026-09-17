import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { afterEach, beforeEach, expect, it, vi } from 'vitest'
import ReportsPage from './ReportsPage'

function jsonResponse(status, body) {
  return {
    status,
    text: () => Promise.resolve(body === undefined ? '' : JSON.stringify(body)),
  }
}

const REPORT_NAMES = [
  'total_payroll_cost',
  'headcount_by_department',
  'headcount_by_country',
  'average_salary_by_department',
  'average_salary_by_country',
  'average_bonus_by_department',
]

const PAYLOADS = {
  total_payroll_cost: '73000.00',
  headcount_by_department: { Engineering: 1 },
  headcount_by_country: { India: 1 },
  average_salary_by_department: { Engineering: '73000.00' },
  average_salary_by_country: { India: '73000.00' },
  average_bonus_by_department: { Engineering: '3000.00' },
}

function setupFetch({ failAll = false } = {}) {
  const fetchMock = vi.fn((url) => {
    if (failAll) {
      return Promise.resolve(
        jsonResponse(400, {
          detail: 'No salary data available before 2022-01-15',
          earliest_available_date: '2022-01-15',
        }),
      )
    }
    const name = REPORT_NAMES.find((n) => url.includes(`/api/reports/${n}/`))
    return Promise.resolve(
      jsonResponse(200, { as_of: '2026-09-16', [name]: PAYLOADS[name], excluded_count: 0 }),
    )
  })
  global.fetch = fetchMock
  return fetchMock
}

beforeEach(() => {
  vi.restoreAllMocks()
})

afterEach(() => {
  vi.useRealTimers()
})

it('defaults the as-of date to today on mount and fetches reports for it', async () => {
  vi.useFakeTimers({ toFake: ['Date'] })
  vi.setSystemTime(new Date('2026-09-16T10:00:00'))
  const fetchMock = setupFetch()

  render(<ReportsPage />)

  expect(screen.getByLabelText('As Of')).toHaveValue('2026-09-16')

  await waitFor(() =>
    expect(
      fetchMock.mock.calls.some(([url]) => url.includes('total_payroll_cost/?as_of=2026-09-16')),
    ).toBe(true),
  )
})

it('changing the as-of date re-requests all six report endpoints with that date', async () => {
  const fetchMock = setupFetch()
  render(<ReportsPage />)

  fireEvent.change(screen.getByLabelText('As Of'), { target: { value: '2026-09-16' } })

  await waitFor(() => {
    REPORT_NAMES.forEach((name) => {
      expect(
        fetchMock.mock.calls.some(([url]) => url.includes(`/api/reports/${name}/?as_of=2026-09-16`)),
      ).toBe(true)
    })
  })
})

it('every card renders its excluded_count, including when it is 0', async () => {
  setupFetch()
  render(<ReportsPage />)

  fireEvent.change(screen.getByLabelText('As Of'), { target: { value: '2026-09-16' } })

  await waitFor(() => expect(screen.getAllByText('Excluded: 0')).toHaveLength(6))
})

it('a too-early-date 400 shows earliest_available_date in the error message and does not render stale data', async () => {
  setupFetch()
  render(<ReportsPage />)
  fireEvent.change(screen.getByLabelText('As Of'), { target: { value: '2026-09-16' } })
  await waitFor(() => expect(screen.getAllByText('Excluded: 0')).toHaveLength(6))

  setupFetch({ failAll: true })
  fireEvent.change(screen.getByLabelText('As Of'), { target: { value: '2020-01-01' } })

  await waitFor(() => expect(screen.getByRole('alert')).toHaveTextContent('2022-01-15'))
  expect(screen.queryByText('Excluded: 0')).not.toBeInTheDocument()
})

it('renders a report money value from the string as given, not run through arithmetic first', async () => {
  setupFetch()
  render(<ReportsPage />)

  fireEvent.change(screen.getByLabelText('As Of'), { target: { value: '2026-09-16' } })

  await waitFor(() => expect(screen.getAllByText('$73000.00').length).toBeGreaterThan(0))
})
