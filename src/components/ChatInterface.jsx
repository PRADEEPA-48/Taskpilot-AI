import { useState, useEffect, useRef, useCallback } from 'react'
import { setSharedOnResult, setSharedOnInterim, setSharedOnEnd } from './VoiceAssistant'

const API_URL = 'http://localhost:5000/process'

export default function ChatInterface() {
  const [messages, setMessages] = useState([
    {
      id: 1,
      type: 'ai',
      text: "Hello! I'm TaskPilot AI. I can help you schedule tasks and meetings. Try saying something like \"Schedule a hackathon meeting tomorrow at 5 PM\" or type your request below!",
      timestamp: new Date()
    }
  ])
  const [inputText, setInputText] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isTyping, setIsTyping] = useState(false)
  const chatEndRef = useRef(null)
  const inputRef = useRef(null)
  const pendingVoiceTextRef = useRef('')
  const handleSendRef = useRef(null)

  // Auto-scroll to bottom
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages, isTyping])

  const handleSend = useCallback(async (text) => {
    const messageText = (typeof text === 'string' ? text : inputText).trim()
    if (!messageText || isLoading) return

    // Add user message
    const userMessage = {
      id: Date.now(),
      type: 'user',
      text: messageText,
      timestamp: new Date()
    }
    setMessages(prev => [...prev, userMessage])
    setInputText('')
    pendingVoiceTextRef.current = ''

    // Show typing indicator
    setIsLoading(true)
    setIsTyping(true)

    try {
      const response = await fetch(API_URL, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text: messageText })
      })

      if (!response.ok) {
        throw new Error(`Server error: ${response.status}`)
      }

      const data = await response.json()

      // Small delay for natural feel
      setTimeout(() => {
        setIsTyping(false)
        const aiMessage = {
          id: Date.now() + 1,
          type: 'ai',
          text: data.response || data.message || data.result || JSON.stringify(data),
          timestamp: new Date()
        }
        setMessages(prev => [...prev, aiMessage])
        setIsLoading(false)
      }, 600 + Math.random() * 800)

    } catch (error) {
      console.error('API Error:', error)
      setTimeout(() => {
        setIsTyping(false)
        const errorMessage = {
          id: Date.now() + 1,
          type: 'ai',
          text: "I'm currently offline. Make sure the backend server is running at " + API_URL + ". Your request: \"" + messageText + "\" has been noted. I'll process it once I'm back online.",
          timestamp: new Date()
        }
        setMessages(prev => [...prev, errorMessage])
        setIsLoading(false)
      }, 800)
    }
  }, [inputText, isLoading])

  // Keep ref updated so voice callbacks always use latest handleSend
  handleSendRef.current = handleSend

  // Register voice callbacks (only once)
  useEffect(() => {
    setSharedOnResult((text, isFinal) => {
      if (isFinal) {
        pendingVoiceTextRef.current = text
        setInputText(text)
      }
    })

    setSharedOnInterim((text) => {
      setInputText(text)
    })

    setSharedOnEnd((finalText) => {
      const textToSend = finalText || pendingVoiceTextRef.current
      if (textToSend && textToSend.trim()) {
        handleSendRef.current(textToSend.trim())
      }
      setInputText('')
      pendingVoiceTextRef.current = ''
    })
  }, [])

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const formatTime = (date) => {
    return new Date(date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="glass rounded-2xl flex flex-col h-[500px]">
      {/* Chat Header */}
      <div className="px-4 py-3 border-b border-white/10 flex items-center gap-3">
        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center">
          <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
            <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
          </svg>
        </div>
        <div>
          <h3 className="text-sm font-semibold text-white">TaskPilot Chat</h3>
          <p className="text-xs text-green-400">● Online</p>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex ${msg.type === 'user' ? 'justify-end' : 'justify-start'} message-appear`}
          >
            <div className={`max-w-[80%] ${msg.type === 'user' ? 'order-2' : 'order-1'}`}>
              {/* AI Avatar */}
              {msg.type === 'ai' && (
                <div className="flex items-start gap-2">
                  <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0 mt-1">
                    <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                      <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                    </svg>
                  </div>
                  <div>
                    <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-2.5">
                      <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                    </div>
                    <p className="text-[10px] text-gray-600 mt-1 ml-1">{formatTime(msg.timestamp)}</p>
                  </div>
                </div>
              )}

              {/* User Message */}
              {msg.type === 'user' && (
                <div>
                  <div className="bg-gradient-to-br from-indigo-500/20 to-purple-600/20 border border-indigo-500/20 rounded-2xl rounded-tr-sm px-4 py-2.5">
                    <p className="text-sm text-gray-200 leading-relaxed whitespace-pre-wrap">{msg.text}</p>
                  </div>
                  <p className="text-[10px] text-gray-600 mt-1 text-right mr-1">{formatTime(msg.timestamp)}</p>
                </div>
              )}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex justify-start message-appear">
            <div className="flex items-start gap-2">
              <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center flex-shrink-0">
                <svg className="w-3.5 h-3.5 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                  <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904L9 18.75l-.813-2.846a4.5 4.5 0 00-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 003.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 003.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 00-3.09 3.09z" />
                </svg>
              </div>
              <div className="bg-white/5 border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3">
                <div className="flex gap-1">
                  <span className="typing-dot w-2 h-2 bg-indigo-400 rounded-full" />
                  <span className="typing-dot w-2 h-2 bg-indigo-400 rounded-full" />
                  <span className="typing-dot w-2 h-2 bg-indigo-400 rounded-full" />
                </div>
              </div>
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-3 border-t border-white/10">
        <div className="flex items-center gap-2">
          <input
            ref={inputRef}
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={handleKeyPress}
            placeholder="Type your task or meeting request..."
            className="flex-1 bg-white/5 border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder-gray-500 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 transition-all duration-200"
            disabled={isLoading}
          />
          {/* Send Button */}
          <button
            onClick={() => handleSend()}
            disabled={!inputText.trim() || isLoading}
            className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-purple-600 flex items-center justify-center hover:shadow-lg hover:shadow-indigo-500/20 transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed"
          >
            <svg className="w-4 h-4 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M6 12L3.269 3.126A59.768 59.768 0 0121.485 12 59.77 59.77 0 013.27 20.876L5.999 12zm0 0h7.5" />
            </svg>
          </button>
          {/* Mic Button - dispatches event to toggle main voice assistant */}
          <button
            className="w-10 h-10 rounded-xl border border-white/10 flex items-center justify-center hover:bg-white/5 hover:border-white/20 transition-all duration-200"
            onClick={() => window.dispatchEvent(new CustomEvent('toggleVoice'))}
            title="Toggle voice input"
          >
            <svg className="w-4 h-4 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 18.75a6 6 0 006-6v-1.5m-6 7.5a6 6 0 01-6-6v-1.5m6 7.5v3.75m-3.75 0h7.5M12 15.75a3 3 0 01-3-3V4.5a3 3 0 116 0v8.25a3 3 0 01-3 3z" />
            </svg>
          </button>
        </div>
      </div>
    </div>
  )
}
