import { beforeEach, expect, it, vi } from 'vitest'
import { apiFetch } from './client'

function jsonResponse(status, body) {
  return {
    status,
    text: () => Promise.resolve(body === undefined ? '' : JSON.stringify(body)),
  }
}

beforeEach(() => {
  vi.restoreAllMocks()
  document.cookie = 'csrftoken=test-token'
})

it('sends a JSON body with a JSON content-type', async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, {}))
  global.fetch = fetchMock

  await apiFetch('/api/employees/', { method: 'POST', body: JSON.stringify({ a: 1 }) })

  const [, options] = fetchMock.mock.calls[0]
  expect(options.headers['Content-Type']).toBe('application/json')
})

it('sends a FormData body without forcing a JSON content-type, so the browser sets the multipart boundary', async () => {
  const fetchMock = vi.fn().mockResolvedValue(jsonResponse(200, {}))
  global.fetch = fetchMock

  const formData = new FormData()
  formData.append('file', new File(['x'], 'roster.xlsx'))
  await apiFetch('/api/imports/roster/', { method: 'POST', body: formData })

  const [, options] = fetchMock.mock.calls[0]
  expect(options.headers['Content-Type']).toBeUndefined()
  expect(options.body).toBe(formData)
})
