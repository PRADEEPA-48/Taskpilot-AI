import Header from './Header'
import VoiceAssistant from './VoiceAssistant'
import ChatInterface from './ChatInterface'
import SchedulePanel from './SchedulePanel'

export default function Dashboard({ user, onLogout }) {
  return (
    <div className="min-h-screen relative z-10 flex flex-col">
      <Header user={user} onLogout={onLogout} />

      <main className="flex-1 flex flex-col lg:flex-row gap-4 p-4 max-w-7xl mx-auto w-full">
        {/* Left: Voice + Chat */}
        <div className="flex-1 flex flex-col gap-4 min-w-0">
          <VoiceAssistant />
          <ChatInterface />
        </div>

        {/* Right: Schedule Panel */}
        <div className="lg:w-80 xl:w-96">
          <SchedulePanel />
        </div>
      </main>
    </div>
  )
}
