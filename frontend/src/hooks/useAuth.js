import { useCallback, useEffect, useState } from 'react'
import { apiFetch } from '../api/client'

/**
 * Session state: current user (checked on mount via /api/auth/me/), login, logout.
 * Also listens for the central `auth:unauthorized` event so any 403 anywhere in the app
 * logs the user out.
 */
export function useAuth() {
  const [user, setUser] = useState(null)

  useEffect(() => {
    apiFetch('/api/auth/me/').then(({ status, data }) => {
      if (status === 200) {
        setUser(data)
      }
    })
  }, [])

  useEffect(() => {
    function handleUnauthorized() {
      setUser(null)
    }
    window.addEventListener('auth:unauthorized', handleUnauthorized)
    return () => window.removeEventListener('auth:unauthorized', handleUnauthorized)
  }, [])

  const login = useCallback(async (email, password) => {
    const { status, data } = await apiFetch('/api/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    })
    if (status === 200) {
      setUser(data)
      return { ok: true }
    }
    return { ok: false }
  }, [])

  const logout = useCallback(async () => {
    await apiFetch('/api/auth/logout/', { method: 'POST' })
    setUser(null)
  }, [])

  return { user, login, logout }
}
