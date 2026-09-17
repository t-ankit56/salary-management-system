/**
 * Central fetch wrapper: adds the CSRF header on writes, credentials for the session
 * cookie, and a JSON content-type unless the body is FormData (multipart uploads set
 * their own). Dispatches `auth:unauthorized` on any 403 so `useAuth` can react centrally.
 */

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? ''

function readCookie(name) {
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`))
  return match ? decodeURIComponent(match[1]) : null
}

export async function apiFetch(path, options = {}) {
  const method = options.method ?? 'GET'
  const headers = { ...options.headers }

  if (method !== 'GET') {
    headers['X-CSRFToken'] = readCookie('csrftoken')
  }
  if (options.body && !(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json'
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    method,
    headers,
    credentials: 'include',
  })

  const text = await response.text()
  const data = text ? JSON.parse(text) : null

  if (response.status === 403) {
    window.dispatchEvent(new Event('auth:unauthorized'))
  }

  return { status: response.status, data }
}
