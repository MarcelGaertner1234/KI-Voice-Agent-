import { createContext, useState, useEffect, ReactNode } from 'react'
import { User } from '@/types/user'
import { authService } from '@/services/auth'
import { storageService } from '@/services/storage'

interface AuthContextType {
  user: User | null
  isLoading: boolean
  login: (email: string, password: string) => Promise<void>
  register: (email: string, password: string, name: string) => Promise<void>
  logout: () => void
  updateUser: (user: User) => void
}

export const AuthContext = createContext<AuthContextType | undefined>(undefined)

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    // Check for saved token and validate
    const checkAuth = async () => {
      const token = storageService.getAccessToken()
      if (token) {
        try {
          const userData = await authService.getCurrentUser()
          setUser(userData)
        } catch (error) {
          console.error('Auth check failed:', error)
          storageService.clearTokens()
        }
      }
      setIsLoading(false)
    }

    checkAuth()
  }, [])

  const login = async (email: string, password: string) => {
    const response = await authService.login(email, password)
    storageService.setTokens(response.access_token, response.refresh_token)
    const userData = await authService.getCurrentUser()
    setUser(userData)
  }

  const register = async (email: string, password: string, name: string) => {
    const response = await authService.register(email, password, name)
    setUser(response)
  }

  const logout = () => {
    authService.logout()
    storageService.clearTokens()
    setUser(null)
  }

  const updateUser = (updatedUser: User) => {
    setUser(updatedUser)
  }

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        login,
        register,
        logout,
        updateUser,
      }}
    >
      {children}
    </AuthContext.Provider>
  )
}