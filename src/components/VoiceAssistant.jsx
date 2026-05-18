import { useState, useEffect, useRef, useCallback } from 'react'

// Global speech recognition state shared with ChatInterface
let sharedRecognition = null
let sharedIsListening = false
let sharedOnResult = null
let sharedOnEnd = null
let sharedOnInterim = null

export function getSharedRecognition() {
  return { recognition: sharedRecognition, isListening: sharedIsListening }
}

export function setSharedOnResult(callback) {
  sharedOnResult = callback
}

export function setSharedOnInterim(callback) {
  sharedOnInterim = callback
}

export function setSharedOnEnd(callback) {
  sharedOnEnd = callback
}

export default function VoiceAssistant() {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [micPermission, setMicPermission] = useState('prompt') // 'prompt' | 'granted' | 'denied'
  const [permissionError, setPermissionError] = useState('')
  const recognitionRef = useRef(null)
  const manualStopRef = useRef(false)
  const isListeningRef = useRef(false)
  const fullTranscriptRef = useRef('')
  const restartTimeoutRef = useRef(null)

  // Check microphone permission on mount
  useEffect(() => {
    checkMicPermission()
  }, [])

  const checkMicPermission = async () => {
    try {
      // Try the Permissions API first
      const result = await navigator.permissions.query({ name: 'microphone' })
      setMicPermission(result.state)

      result.onchange = () => {
        setMicPermission(result.state)
        if (result.state === 'granted') {
          setPermissionError('')
        }
      }
    } catch {
      // Permissions API not supported - will check on first use
      setMicPermission('prompt')
    }
  }

  // Request microphone permission explicitly using getUserMedia
  const requestMicPermission = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true })
      // Permission granted - stop the stream immediately, we just needed permission
      stream.getTracks().forEach(track => track.stop())
      setMicPermission('granted')
      setPermissionError('')
      return true
    } catch (err) {
      console.error('Microphone permission denied:', err)
      setMicPermission('denied')
      if (err.name === 'NotAllowedError') {
        setPermissionError('Microphone access denied. Please allow microphone in your browser settings and reload.')
      } else if (err.name === 'NotFoundError') {
        setPermissionError('No microphone found. Please connect a microphone and try again.')
      } else {
        setPermissionError('Could not access microphone: ' + err.message)
      }
      return false
    }
  }

  const stopListening = useCallback(() => {
    manualStopRef.current = true
    isListeningRef.current = false
    sharedIsListening = false
    setIsListening(false)

    // Clear any pending restart
    if (restartTimeoutRef.current) {
      clearTimeout(restartTimeoutRef.current)
      restartTimeoutRef.current = null
    }

    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (e) {
        // ignore if already stopped
      }
      recognitionRef.current = null
      sharedRecognition = null
    }

    // Notify ChatInterface that listening ended with final transcript
    if (sharedOnEnd && fullTranscriptRef.current.trim()) {
      sharedOnEnd(fullTranscriptRef.current.trim())
    }
    fullTranscriptRef.current = ''
  }, [])

  const startListening = useCallback(async () => {
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    if (!SpeechRecognition) {
      setPermissionError('Speech Recognition is not supported in this browser. Please use Google Chrome.')
      return
    }

    // Request microphone permission first if not already granted
    if (micPermission !== 'granted') {
      const granted = await requestMicPermission()
      if (!granted) return
    }

    // Reset state
    manualStopRef.current = false
    isListeningRef.current = true
    sharedIsListening = true
    fullTranscriptRef.current = ''
    setTranscript('')
    setPermissionError('')
    setIsListening(true)

    const createRecognition = () => {
      const recognition = new SpeechRecognition()
      recognition.continuous = true
      recognition.interimResults = true
      recognition.lang = 'en-US'
      recognition.maxAlternatives = 1

      recognition.onstart = () => {
        if (isListeningRef.current) {
          setIsListening(true)
          sharedIsListening = true
        }
      }

      recognition.onresult = (event) => {
        let interimTranscript = ''
        let finalTranscript = ''

        for (let i = event.resultIndex; i < event.results.length; i++) {
          const result = event.results[i]
          if (result.isFinal) {
            finalTranscript += result[0].transcript
          } else {
            interimTranscript += result[0].transcript
          }
        }

        // Accumulate final results
        if (finalTranscript) {
          fullTranscriptRef.current += finalTranscript
          // Notify ChatInterface of final text
          if (sharedOnResult) {
            sharedOnResult(fullTranscriptRef.current, true)
          }
        }

        // Show current combined text (final so far + current interim)
        const displayText = fullTranscriptRef.current + interimTranscript
        setTranscript(displayText)

        // Notify ChatInterface of interim text for live preview
        if (sharedOnInterim) {
          sharedOnInterim(displayText)
        }
      }

      recognition.onerror = (event) => {
        console.warn('Speech recognition error:', event.error)

        if (event.error === 'not-allowed' || event.error === 'service-not-allowed') {
          // Permission was denied during recognition
          manualStopRef.current = true
          isListeningRef.current = false
          sharedIsListening = false
          setIsListening(false)
          setMicPermission('denied')
          setPermissionError('Microphone access was denied. Please allow it in browser settings.')
          return
        }

        // For 'no-speech', 'network', 'aborted' errors:
        // Don't change manualStopRef - the onend handler will restart
        // Just log and let the restart logic handle it
      }

      recognition.onend = () => {
        // KEY FIX: If the user hasn't manually stopped, restart recognition automatically
        // This prevents the mic from stopping after silence
        if (!manualStopRef.current && isListeningRef.current) {
          // Add a small delay before restart to avoid rapid restart loops
          restartTimeoutRef.current = setTimeout(() => {
            if (!manualStopRef.current && isListeningRef.current) {
              try {
                const newRecognition = createRecognition()
                recognitionRef.current = newRecognition
                sharedRecognition = newRecognition
                newRecognition.start()
              } catch (e) {
                console.error('Failed to restart recognition:', e)
                setIsListening(false)
                isListeningRef.current = false
                sharedIsListening = false
              }
            }
          }, 100)
        } else {
          setIsListening(false)
          sharedIsListening = false
        }
      }

      return recognition
    }

    // Stop existing recognition if any
    if (recognitionRef.current) {
      try {
        recognitionRef.current.stop()
      } catch (e) {
        // ignore
      }
    }

    const recognition = createRecognition()
    recognitionRef.current = recognition
    sharedRecognition = recognition

    try {
      recognition.start()
    } catch (e) {
      console.error('Failed to start recognition:', e)
      setIsListening(false)
      isListeningRef.current = false
      sharedIsListening = false
      setPermissionError('Could not start speech recognition. Please check your browser settings.')
    }
  }, [micPermission])

  const toggleListening = () => {
    if (isListening) {
      stopListening()
    } else {
      startListening()
    }
  }

  // Listen for toggleVoice custom event from ChatInterface mic button
  useEffect(() => {
    const handleToggleVoice = () => {
      if (isListeningRef.current) {
        stopListening()
      } else {
        startListening()
      }
    }
    window.addEventListener('toggleVoice', handleToggleVoice)
    return () => window.removeEventListener('toggleVoice', handleToggleVoice)
  }, [startListening, stopListening])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      manualStopRef.current = true
      isListeningRef.current = false
      if (restartTimeoutRef.current) {
        clearTimeout(restartTimeoutRef.current)
      }
      if (recognitionRef.current) {
        try {
          recognitionRef.current.stop()
        } catch (e) {
          // ignore
        }
      }
    }
  }, [])

  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex flex-col items-center">
        {/* Status */}
        <div className="flex items-center gap-2 mb-4">
          {isListening ? (
            <>
              <span className="relative flex h-3 w-3">
                <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75" />
                <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500" />
              </span>
              <span className="text-sm text-red-400 font-medium">🎤 Listening...</span>
            </>
          ) : (
            <>
              <span className="relative flex h-3 w-3">
                <span className="relative inline-flex rounded-full h-3 w-3 bg-gray-500" />
              </span>
              <span className="text-sm text-gray-500 font-medium">🎤 Stopped</span>
            </>
          )}
        </div>

        {/* Mic Button */}
        <div className="relative flex items-center justify-center mb-4">
          {/* Ripple rings when listening */}
          {isListening && (
            <>
              <div className="mic-ring" />
              <div className="mic-ring" />
              <div className="mic-ring" />
            </>
          )}

          <button
            onClick={toggleListening}
            className={`relative z-10 w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${
              isListening
                ? 'bg-gradient-to-br from-red-500 to-rose-600 shadow-lg shadow-red-500/30 scale-110'
                : micPermission === 'denied'
                ? 'bg-gradient-to-br from-gray-500 to-gray-600 shadow-lg shadow-gray-500/20 hover:scale-105'
                : 'bg-gradient-to-br from-indigo-500 to-purple-600 shadow-lg shadow-indigo-500/30 hover:scale-105'
            }`}
          >
            {isListening ? (
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M5.25 7.5A5.25 5.25 0 0110.5 2.25h3a5.25 5.25 0 015.25 5.25v6a5.25 5.25 0 01-5.25 5.25h-3a5.25 5.25 0 01-5.25-5.25v-6zM12 18.75v3m-3.75 0h7.5" />
              </svg>
            ) : (
              <svg className="w-8 h-8 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
              </svg>
            )}
          </button>
        </div>

        {/* Toggle text */}
        <p className="text-sm text-gray-400">
          {isListening
            ? 'Tap to stop listening'
            : micPermission === 'denied'
            ? 'Microphone access needed'
            : 'Tap to start listening'
          }
        </p>

        {/* Permission error */}
        {permissionError && (
          <div className="mt-3 px-4 py-2 rounded-lg bg-red-500/10 border border-red-500/20 text-xs text-red-400 max-w-full text-center">
            {permissionError}
          </div>
        )}

        {/* Live transcript preview */}
        {transcript && isListening && (
          <div className="mt-3 px-4 py-2 rounded-lg bg-white/5 text-sm text-gray-300 max-w-full text-center italic">
            "{transcript}"
          </div>
        )}
      </div>
    </div>
  )
}
