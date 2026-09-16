import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import App from './App'
import { apiFetch } from './api/client'

function jsonResponse(status, body) {
  return {
    status,
    text: () => Promise.resolve(body === undefined ? '' : JSON.stringify(body)),
  }
}

function mockFetch(overrides) {
  return vi.fn((url) => {
    for (const [matcher, response] of overrides) {
      if (url.includes(matcher)) return Promise.resolve(response)
    }
    if (url.includes('/api/employees/')) {
      return Promise.resolve(jsonResponse(200, { count: 0, next: null, previous: null, results: [] }))
    }
    return Promise.resolve(jsonResponse(200, []))
  })
}

function renderApp() {
  return render(
    <MemoryRouter>
      <App />
    </MemoryRouter>,
  )
}

beforeEach(() => {
  vi.restoreAllMocks()
})

it('submits credentials and shows the authenticated app on success', async () => {
  global.fetch = mockFetch([
    ['/api/auth/me/', jsonResponse(403, { detail: 'Authentication credentials were not provided.' })],
    ['/api/auth/login/', jsonResponse(200, { email: 'hr@acme.com' })],
  ])

  renderApp()

  await waitFor(() => expect(screen.getByLabelText('Email')).toBeInTheDocument())

  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'hr@acme.com' } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'correct' } })
  fireEvent.click(screen.getByRole('button', { name: 'Log In' }))

  await waitFor(() => expect(screen.getByRole('heading', { name: 'Employees' })).toBeInTheDocument())

  const loginCall = global.fetch.mock.calls.find(([url]) => url.includes('/api/auth/login/'))
  expect(loginCall).toBeTruthy()
  expect(JSON.parse(loginCall[1].body)).toEqual({ email: 'hr@acme.com', password: 'correct' })
})

it('shows an error on a 401 response and does not navigate anywhere', async () => {
  global.fetch = mockFetch([
    ['/api/auth/me/', jsonResponse(403, { detail: 'Authentication credentials were not provided.' })],
    ['/api/auth/login/', jsonResponse(401)],
  ])

  renderApp()

  await waitFor(() => expect(screen.getByLabelText('Email')).toBeInTheDocument())

  fireEvent.change(screen.getByLabelText('Email'), { target: { value: 'hr@acme.com' } })
  fireEvent.change(screen.getByLabelText('Password'), { target: { value: 'wrong' } })
  fireEvent.click(screen.getByRole('button', { name: 'Log In' }))

  await waitFor(() => expect(screen.getByText('Invalid email or password')).toBeInTheDocument())
  expect(screen.queryByRole('heading', { name: 'Employees' })).not.toBeInTheDocument()
})

it('dispatches the unauthorized event and renders LoginPage on a 403 from any fetch call', async () => {
  global.fetch = mockFetch([
    ['/api/employees/999/', jsonResponse(403, { detail: 'Authentication credentials were not provided.' })],
    ['/api/auth/me/', jsonResponse(200, { email: 'hr@acme.com' })],
  ])

  renderApp()

  await waitFor(() => expect(screen.getByRole('heading', { name: 'Employees' })).toBeInTheDocument())

  await apiFetch('/api/employees/999/')

  await waitFor(() => expect(screen.getByLabelText('Email')).toBeInTheDocument())
})

it('does not show an error banner when the mount-time session check returns 403', async () => {
  global.fetch = mockFetch([
    ['/api/auth/me/', jsonResponse(403, { detail: 'Authentication credentials were not provided.' })],
  ])

  renderApp()

  await waitFor(() => expect(screen.getByLabelText('Email')).toBeInTheDocument())
  expect(screen.queryByRole('alert')).not.toBeInTheDocument()
})
