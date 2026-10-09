import { createContext, useContext, useState, useEffect, useCallback } from 'react'
import api from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  const fetchUser = useCallback(async () => {
    const accessToken = localStorage.getItem('access_token')
    if (!accessToken) {
      setUser(null)
      setLoading(false)
      return
    }

    try {
      const response = await api.get('/api/auth/me')
      setUser(response.data)
    } catch (error) {
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token')
      if (refreshToken) {
        try {
          const refreshResponse = await api.post('/api/auth/refresh', { refresh_token: refreshToken })
          localStorage.setItem('access_token', refreshResponse.data.access_token)
          localStorage.setItem('refresh_token', refreshResponse.data.refresh_token)
          const response = await api.get('/api/auth/me')
          setUser(response.data)
        } catch (refreshError) {
          logout()
        }
      } else {
        logout()
      }
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    fetchUser()
  }, [fetchUser])

  const login = async (email, password) => {
    const response = await api.post('/api/auth/login', { email, password })
    const { access_token, refresh_token } = response.data
    localStorage.setItem('access_token', access_token)
    localStorage.setItem('refresh_token', refresh_token)
    api.defaults.headers.common['Authorization'] = `Bearer ${access_token}`
    await fetchUser()
    return response.data
  }

  const register = async (email, password, full_name) => {
    const response = await api.post('/api/auth/register', { email, password, full_name })
    return response.data
  }

  const logout = () => {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    delete api.defaults.headers.common['Authorization']
    setUser(null)
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    fetchUser,
  }

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider')
  }
  return context
}