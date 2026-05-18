import { useState, lazy, Suspense } from 'react'
import { jwtDecode } from 'jwt-decode'

// Lazy-load GoogleLogin to avoid errors when GoogleOAuthProvider is not present
const GoogleLogin = lazy(() =>
  import('@react-oauth/google').then(mod => ({ default: mod.GoogleLogin }))
)

export default function Login({ onLogin, clientIdAvailable }) {
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState('')

  const handleGoogleSuccess = (credentialResponse) => {
    setIsLoading(true)
    setError('')

    try {
      const decoded = jwtDecode(credentialResponse.credential)
      const userData = {
        name: decoded.name || decoded.given_name || 'User',
        email: decoded.email || '',
        avatar: decoded.picture || null,
        sub: decoded.sub
      }
      onLogin(userData)
    } catch (err) {
      console.error('Token decode error:', err)
      setError('Login failed. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }

  const handleGoogleError = () => {
    setError('Google sign-in failed. Please try again.')
    setIsLoading(false)
  }

  const handleDemoLogin = () => {
    setIsLoading(true)
    setError('')
    setTimeout(() => {
      onLogin({
        name: 'Demo User',
        email: 'demo@taskpilot.ai',
        avatar: null,
        sub: 'demo'
      })
      setIsLoading(false)
    }, 800)
  }

  return (
    <div className="min-h-screen flex items-center justify-center p-4 relative z-10">
      <div className="w-full max-w-md">
        {/* Logo/Brand */}
        <div className="text-center mb-10 animate-fade-in">
          <div className="inline-flex items-center justify-center w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500 to-purple-600 mb-6 shadow-lg shadow-indigo-500/30">
            <svg className="w-10 h-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09zM18.259 8.715L18 9.75l-.259-1.035a3.375 3.375 0 00-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 002.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 002.455 2.456L21.75 6l-1.036.259a3.375 3.375 0 00-2.455 2.456zM16.894 20.567L16.5 21.75l-.394-1.183a2.25 2.25 0 00-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 001.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 001.423 1.423l1.183.394-1.183.394a2.25 2.25 0 00-1.423 1.423z" />
            </svg>
          </div>
          <h1 className="text-4xl font-bold gradient-text mb-3">TaskPilot AI</h1>
          <p className="text-gray-400 text-lg font-light tracking-wide">Think → Plan → Execute</p>
        </div>

        {/* Login Card */}
        <div className="glass-strong rounded-3xl p-8 animate-slide-up">
          <div className="text-center mb-8">
            <h2 className="text-xl font-semibold text-white mb-2">Welcome</h2>
            <p className="text-gray-400 text-sm">Sign in to manage your tasks with AI</p>
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 rounded-lg bg-red-500/10 border border-red-500/20 text-red-400 text-sm text-center">
              {error}
            </div>
          )}

          {/* Google Sign-In Button (only if client ID is configured) */}
          {clientIdAvailable ? (
            <div className="flex justify-center mb-6">
              {isLoading ? (
                <div className="flex items-center gap-3 px-6 py-3.5 rounded-xl bg-white text-gray-800">
                  <svg className="animate-spin h-5 w-5 text-indigo-600" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                  </svg>
                  <span className="font-medium">Signing in...</span>
                </div>
              ) : (
                <Suspense fallback={
                  <div className="flex items-center gap-3 px-6 py-3.5 rounded-xl bg-white/10 text-gray-400">
                    <svg className="animate-spin h-5 w-5" fill="none" viewBox="0 0 24 24">
                      <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" />
                      <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
                    </svg>
                    <span>Loading...</span>
                  </div>
                }>
                  <GoogleLogin
                    onSuccess={handleGoogleSuccess}
                    onError={handleGoogleError}
                    theme="filled_black"
                    size="large"
                    shape="rectangular"
                    text="continue_with"
                    width="320"
                  />
                </Suspense>
              )}
            </div>
          ) : (
            /* Show setup instructions if client ID not configured */
            <div className="mb-6 p-4 rounded-xl bg-indigo-500/10 border border-indigo-500/20">
              <p className="text-xs text-indigo-300 mb-2 font-medium">Google OAuth Setup Required</p>
              <p className="text-xs text-gray-400 leading-relaxed">
                Add your <code className="text-indigo-300 bg-indigo-500/10 px-1 py-0.5 rounded">VITE_GOOGLE_CLIENT_ID</code> to the <code className="text-indigo-300 bg-indigo-500/10 px-1 py-0.5 rounded">.env</code> file to enable Google Sign-In. Use the demo below to try the app.
              </p>
            </div>
          )}

          {/* Divider */}
          <div className="flex items-center gap-4 mb-6">
            <div className="flex-1 h-px bg-white/10" />
            <span className="text-gray-500 text-xs">OR</span>
            <div className="flex-1 h-px bg-white/10" />
          </div>

          {/* Demo Access */}
          <button
            onClick={handleDemoLogin}
            disabled={isLoading}
            className="w-full flex items-center justify-center gap-2 px-6 py-3.5 rounded-xl border border-white/10 text-gray-300 font-medium hover:bg-white/5 hover:border-white/20 transition-all duration-300 disabled:opacity-50"
          >
            <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M15.75 15.75V18m-7.5-6.75h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25V13.5zm0 2.25h.008v.008H8.25v-.008zm0 2.25h.008v.008H8.25V18zm2.498-6.75h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007V13.5zm0 2.25h.007v.008h-.007v-.008zm0 2.25h.007v.008h-.007V18zm2.504-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V13.5zm0 2.25h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V18zm2.498-6.75h.008v.008h-.008v-.008zm0 2.25h.008v.008h-.008V13.5zM8.25 6h7.5v2.25h-7.5V6zM12 2.25c-1.892 0-3.758.11-5.593.322C5.307 2.7 4.5 3.65 4.5 4.757V19.5a2.25 2.25 0 002.25 2.25h10.5a2.25 2.25 0 002.25-2.25V4.757c0-1.108-.806-2.057-1.907-2.185A48.507 48.507 0 0012 2.25z" />
            </svg>
            <span>Continue with Demo</span>
          </button>
        </div>

        {/* Footer */}
        <p className="text-center text-gray-600 text-xs mt-8">
          Powered by AI · Your smart productivity companion
        </p>
      </div>
    </div>
  )
}
