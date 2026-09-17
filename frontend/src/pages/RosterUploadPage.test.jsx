import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter, Route, Routes } from 'react-router-dom'
import { beforeEach, expect, it, vi } from 'vitest'
import RosterUploadPage from './RosterUploadPage'

function renderPage() {
  return render(
    <MemoryRouter initialEntries={['/roster-upload']}>
      <Routes>
        <Route path="/roster-upload" element={<RosterUploadPage />} />
        <Route path="/employees" element={<div>Employee list stub</div>} />
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

function rosterFile() {
  return new File(['dummy content'], 'roster.xlsx', {
    type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  })
}

beforeEach(() => {
  vi.restoreAllMocks()
})

it('the Upload button is disabled until a file is chosen', () => {
  renderPage()

  expect(screen.getByRole('button', { name: 'Upload' })).toBeDisabled()

  fireEvent.change(screen.getByLabelText('Roster file'), { target: { files: [rosterFile()] } })

  expect(screen.getByRole('button', { name: 'Upload' })).not.toBeDisabled()
  expect(screen.getByText('roster.xlsx')).toBeInTheDocument()
})

it('submits the chosen file as multipart form data to POST /api/imports/roster/', async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse(201, { created: 12, updated: 3 }))
  global.fetch = fetchMock
  renderPage()

  fireEvent.change(screen.getByLabelText('Roster file'), { target: { files: [rosterFile()] } })
  fireEvent.click(screen.getByRole('button', { name: 'Upload' }))

  await waitFor(() => expect(fetchMock).toHaveBeenCalled())
  const [url, options] = fetchMock.mock.calls[0]
  expect(url).toContain('/api/imports/roster/')
  expect(options.method).toBe('POST')
  expect(options.body).toBeInstanceOf(FormData)
  expect(options.body.get('file')).toBeInstanceOf(File)
})

it('on 201, shows the created/updated counts and a link back to the employee list', async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse(201, { created: 12, updated: 3 }))
  global.fetch = fetchMock
  renderPage()

  fireEvent.change(screen.getByLabelText('Roster file'), { target: { files: [rosterFile()] } })
  fireEvent.click(screen.getByRole('button', { name: 'Upload' }))

  await waitFor(() =>
    expect(screen.getByText('12 employees created, 3 updated.')).toBeInTheDocument(),
  )
  fireEvent.click(screen.getByRole('link', { name: 'View Employees' }))
  expect(screen.getByText('Employee list stub')).toBeInTheDocument()
})

it('on a 400 with row errors, shows a Row/Error table instead of a generic banner', async () => {
  const fetchMock = vi.fn().mockResolvedValue(
    jsonResponse(400, {
      errors: [
        { row: 4, error: 'email is required' },
        { row: 7, error: 'duplicate employee_code in file' },
      ],
    }),
  )
  global.fetch = fetchMock
  renderPage()

  fireEvent.change(screen.getByLabelText('Roster file'), { target: { files: [rosterFile()] } })
  fireEvent.click(screen.getByRole('button', { name: 'Upload' }))

  await waitFor(() =>
    expect(
      screen.getByText('Upload failed — fix the errors below and try again.'),
    ).toBeInTheDocument(),
  )
  expect(screen.getByRole('cell', { name: '4' })).toBeInTheDocument()
  expect(screen.getByText('email is required')).toBeInTheDocument()
  expect(screen.getByRole('cell', { name: '7' })).toBeInTheDocument()
  expect(screen.getByText('duplicate employee_code in file')).toBeInTheDocument()
})
