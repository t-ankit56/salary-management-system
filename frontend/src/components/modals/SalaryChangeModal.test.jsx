import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, expect, it, vi } from 'vitest'
import SalaryChangeModal from './SalaryChangeModal'

function jsonResponse(status, body) {
  return {
    status,
    text: () => Promise.resolve(body === undefined ? '' : JSON.stringify(body)),
  }
}

function fillForm() {
  fireEvent.change(screen.getByLabelText('Base'), { target: { value: '65000' } })
  fireEvent.change(screen.getByLabelText('Allowance'), { target: { value: '5000' } })
  fireEvent.change(screen.getByLabelText('Yearly Bonus'), { target: { value: '3000' } })
  fireEvent.change(screen.getByLabelText('Currency'), { target: { value: 'USD' } })
  fireEvent.change(screen.getByLabelText('Effective From'), { target: { value: '2023-01-01' } })
}

beforeEach(() => {
  vi.restoreAllMocks()
})

it('submits the entered values as strings to POST /api/employees/:id/salary-changes/', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse(201, {
      id: 3,
      employee: 3,
      base: '65000.00',
      allowance: '5000.00',
      yearly_bonus: '3000.00',
      currency: 'USD',
      effective_from: '2023-01-01',
      effective_to: null,
    }),
  )
  global.fetch = fetchMock
  const onSuccess = vi.fn()
  render(<SalaryChangeModal employeeId={3} onClose={() => {}} onSuccess={onSuccess} />)

  fillForm()
  fireEvent.click(screen.getByRole('button', { name: 'Save' }))

  await waitFor(() => expect(fetchMock).toHaveBeenCalled())
  const [url, options] = fetchMock.mock.calls[0]
  expect(url).toContain('/api/employees/3/salary-changes/')
  const body = JSON.parse(options.body)
  expect(body).toEqual({
    base: '65000',
    allowance: '5000',
    yearly_bonus: '3000',
    currency: 'USD',
    effective_from: '2023-01-01',
  })

  await waitFor(() => expect(onSuccess).toHaveBeenCalled())
})

it('on success, calls onSuccess so the parent can close the modal and refetch history', async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse(201, {}))
  global.fetch = fetchMock
  const onSuccess = vi.fn()
  render(<SalaryChangeModal employeeId={3} onClose={() => {}} onSuccess={onSuccess} />)

  fillForm()
  fireEvent.click(screen.getByRole('button', { name: 'Save' }))

  await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1))
})

it('shows a {detail} 400 response as a banner and keeps the modal open', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse(400, { detail: "Cannot backdate a change before the current period's start" }),
  )
  global.fetch = fetchMock
  const onSuccess = vi.fn()
  render(<SalaryChangeModal employeeId={3} onClose={() => {}} onSuccess={onSuccess} />)

  fillForm()
  fireEvent.click(screen.getByRole('button', { name: 'Save' }))

  await waitFor(() =>
    expect(screen.getByRole('alert')).toHaveTextContent(
      "Cannot backdate a change before the current period's start",
    ),
  )
  expect(onSuccess).not.toHaveBeenCalled()
})

it('highlights a field-shaped 400 response on its field, not a generic banner', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse(400, { effective_from: ['This field is required.'] }),
  )
  global.fetch = fetchMock
  render(<SalaryChangeModal employeeId={3} onClose={() => {}} onSuccess={() => {}} />)

  fireEvent.click(screen.getByRole('button', { name: 'Save' }))

  await waitFor(() => expect(screen.getByText('This field is required.')).toBeInTheDocument())
  expect(screen.queryByRole('alert')).not.toBeInTheDocument()
})
