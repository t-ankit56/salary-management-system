import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { beforeEach, expect, it, vi } from 'vitest'
import SalaryCorrectionModal from './SalaryCorrectionModal'

const PERIOD = {
  id: 2,
  base: '60000.00',
  allowance: '5000.00',
  yearly_bonus: '3000.00',
  currency: 'USD',
  effective_from: '2022-01-15',
  effective_to: '2023-01-01',
  correction_count: 1,
}

function jsonResponse(status, body) {
  return {
    status,
    text: () => Promise.resolve(body === undefined ? '' : JSON.stringify(body)),
  }
}

function fillForm() {
  fireEvent.change(screen.getByLabelText('Base'), { target: { value: '61000' } })
  fireEvent.change(screen.getByLabelText('Allowance'), { target: { value: '5000' } })
  fireEvent.change(screen.getByLabelText('Yearly Bonus'), { target: { value: '3000' } })
  fireEvent.change(screen.getByLabelText(/Reason/), { target: { value: 'Data entry error' } })
}

beforeEach(() => {
  vi.restoreAllMocks()
})

it('submits salary_period as the id of the period the modal was opened from, plus the edited amounts and reason', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse(201, {
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
    }),
  )
  global.fetch = fetchMock
  const onSuccess = vi.fn()
  render(
    <SalaryCorrectionModal
      employeeId={3}
      period={PERIOD}
      onClose={() => {}}
      onSuccess={onSuccess}
    />,
  )

  fillForm()
  fireEvent.click(screen.getByRole('button', { name: 'Save' }))

  await waitFor(() => expect(fetchMock).toHaveBeenCalled())
  const [url, options] = fetchMock.mock.calls[0]
  expect(url).toContain('/api/employees/3/salary-corrections/')
  const body = JSON.parse(options.body)
  expect(body).toEqual({
    salary_period: 2,
    base: '61000',
    allowance: '5000',
    yearly_bonus: '3000',
    reason: 'Data entry error',
  })

  await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1))
})

it('a blank reason shows the field error under the reason input and does not fail silently', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse(400, { reason: ['This field may not be blank.'] }),
  )
  global.fetch = fetchMock
  const onSuccess = vi.fn()
  render(
    <SalaryCorrectionModal
      employeeId={3}
      period={PERIOD}
      onClose={() => {}}
      onSuccess={onSuccess}
    />,
  )

  fireEvent.change(screen.getByLabelText('Base'), { target: { value: '61000' } })
  fireEvent.click(screen.getByRole('button', { name: 'Save' }))

  await waitFor(() =>
    expect(screen.getByText('This field may not be blank.')).toBeInTheDocument(),
  )
  expect(onSuccess).not.toHaveBeenCalled()
})

it('on success, calls onSuccess so the parent can close the modal and refresh the history', async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse(201, {}))
  global.fetch = fetchMock
  const onSuccess = vi.fn()
  render(
    <SalaryCorrectionModal
      employeeId={3}
      period={PERIOD}
      onClose={() => {}}
      onSuccess={onSuccess}
    />,
  )

  fillForm()
  fireEvent.click(screen.getByRole('button', { name: 'Save' }))

  await waitFor(() => expect(onSuccess).toHaveBeenCalledTimes(1))
})
