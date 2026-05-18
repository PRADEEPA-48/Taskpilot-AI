import { useState, useEffect } from 'react'
import { GoogleOAuthProvider } from '@react-oauth/google'
import Login from './components/Login'
import Dashboard from './components/Dashboard'

// Read Google Client ID from environment variable
// Set VITE_GOOGLE_CLIENT_ID in your .env file
const GOOGLE_CLIENT_ID = import.meta.env.VITE_GOOGLE_CLIENT_ID || ''

function AppContent() {
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [user, setUser] = useState(null)

  // Restore session from localStorage on mount
  useEffect(() => {
    const savedUser = localStorage.getItem('taskpilot_user')
    if (savedUser) {
      try {
        const parsed = JSON.parse(savedUser)
        setUser(parsed)
        setIsLoggedIn(true)
      } catch {
        localStorage.removeItem('taskpilot_user')
      }
    }
  }, [])

  const handleLogin = (userData) => {
    setUser(userData)
    setIsLoggedIn(true)
    localStorage.setItem('taskpilot_user', JSON.stringify(userData))
  }

  const handleLogout = () => {
    setUser(null)
    setIsLoggedIn(false)
    localStorage.removeItem('taskpilot_user')
  }

  return (
    <div className="min-h-screen relative">
      {/* Background orbs */}
      <div className="orb orb-1" />
      <div className="orb orb-2" />
      <div className="orb orb-3" />

      {isLoggedIn ? (
        <Dashboard user={user} onLogout={handleLogout} />
      ) : (
        <Login onLogin={handleLogin} clientIdAvailable={!!GOOGLE_CLIENT_ID} />
      )}
    </div>
  )
}

function App() {
  const clientId = GOOGLE_CLIENT_ID

  // If no client ID configured, render without GoogleOAuthProvider
  // Login will show demo-only mode
  if (!clientId) {
    return <AppContent />
  }

  return (
    <GoogleOAuthProvider clientId={clientId}>
      <AppContent />
    </GoogleOAuthProvider>
  )
}

export default App
