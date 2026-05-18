import { useState } from 'react'

const initialMeetings = [
  {
    id: 1,
    title: 'Hackathon Meeting',
    time: 'Tomorrow 5:00 PM',
    icon: '📅',
    type: 'meeting'
  },
  {
    id: 2,
    title: 'Sprint Review',
    time: 'Friday 10:00 AM',
    icon: '📋',
    type: 'meeting'
  },
  {
    id: 3,
    title: 'Team Standup',
    time: 'Daily 9:00 AM',
    icon: '🤝',
    type: 'meeting'
  }
]

const initialTasks = [
  {
    id: 4,
    title: 'DSA Practice',
    time: 'Today 7:00 PM',
    icon: '📚',
    type: 'task',
    priority: 'high'
  },
  {
    id: 5,
    title: 'Project Documentation',
    time: 'Today 9:00 PM',
    icon: '📝',
    type: 'task',
    priority: 'medium'
  },
  {
    id: 6,
    title: 'Code Review PR #42',
    time: 'Tomorrow 11:00 AM',
    icon: '🔍',
    type: 'task',
    priority: 'low'
  }
]

export default function SchedulePanel() {
  const [activeTab, setActiveTab] = useState('meetings')
  const [meetings] = useState(initialMeetings)
  const [tasks] = useState(initialTasks)

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'high': return 'bg-red-500/20 text-red-400 border-red-500/20'
      case 'medium': return 'bg-yellow-500/20 text-yellow-400 border-yellow-500/20'
      case 'low': return 'bg-green-500/20 text-green-400 border-green-500/20'
      default: return 'bg-gray-500/20 text-gray-400 border-gray-500/20'
    }
  }

  return (
    <div className="glass rounded-2xl h-full flex flex-col">
      {/* Header */}
      <div className="px-4 py-3 border-b border-white/10">
        <h3 className="text-sm font-semibold text-white">Upcoming Schedule</h3>
        <p className="text-xs text-gray-500">Your tasks & meetings</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-1 px-3 py-2">
        <button
          onClick={() => setActiveTab('meetings')}
          className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-all duration-200 ${
            activeTab === 'meetings'
              ? 'bg-indigo-500/20 text-indigo-300 border border-indigo-500/30'
              : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
          }`}
        >
          📅 Meetings
        </button>
        <button
          onClick={() => setActiveTab('tasks')}
          className={`flex-1 py-2 px-3 rounded-lg text-xs font-medium transition-all duration-200 ${
            activeTab === 'tasks'
              ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30'
              : 'text-gray-500 hover:text-gray-300 hover:bg-white/5'
          }`}
        >
          ✅ Tasks
        </button>
      </div>

      {/* Cards */}
      <div className="flex-1 overflow-y-auto p-3 space-y-2">
        {activeTab === 'meetings' && meetings.map((meeting, index) => (
          <div
            key={meeting.id}
            className="glass rounded-xl p-3 hover:bg-white/5 transition-all duration-200 cursor-pointer group animate-slide-up"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <div className="flex items-start gap-3">
              <span className="text-lg">{meeting.icon}</span>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-white group-hover:text-indigo-300 transition-colors truncate">
                  {meeting.title}
                </p>
                <p className="text-xs text-gray-500 mt-0.5">{meeting.time}</p>
              </div>
              <svg className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </div>
          </div>
        ))}

        {activeTab === 'tasks' && tasks.map((task, index) => (
          <div
            key={task.id}
            className="glass rounded-xl p-3 hover:bg-white/5 transition-all duration-200 cursor-pointer group animate-slide-up"
            style={{ animationDelay: `${index * 0.05}s` }}
          >
            <div className="flex items-start gap-3">
              <span className="text-lg">{task.icon}</span>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <p className="text-sm font-medium text-white group-hover:text-purple-300 transition-colors truncate">
                    {task.title}
                  </p>
                </div>
                <div className="flex items-center gap-2 mt-1">
                  <p className="text-xs text-gray-500">{task.time}</p>
                  <span className={`text-[10px] px-1.5 py-0.5 rounded-full border ${getPriorityColor(task.priority)}`}>
                    {task.priority}
                  </span>
                </div>
              </div>
              <svg className="w-4 h-4 text-gray-600 group-hover:text-gray-400 transition-colors flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M8.25 4.5l7.5 7.5-7.5 7.5" />
              </svg>
            </div>
          </div>
        ))}

        {/* Empty state message */}
        {activeTab === 'meetings' && meetings.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 text-sm">No upcoming meetings</p>
          </div>
        )}
        {activeTab === 'tasks' && tasks.length === 0 && (
          <div className="text-center py-8">
            <p className="text-gray-500 text-sm">No upcoming tasks</p>
          </div>
        )}
      </div>

      {/* Quick Stats */}
      <div className="px-3 py-3 border-t border-white/10">
        <div className="flex justify-between items-center">
          <div className="text-center">
            <p className="text-lg font-bold gradient-text">{meetings.length}</p>
            <p className="text-[10px] text-gray-600">Meetings</p>
          </div>
          <div className="w-px h-8 bg-white/10" />
          <div className="text-center">
            <p className="text-lg font-bold gradient-text">{tasks.length}</p>
            <p className="text-[10px] text-gray-600">Tasks</p>
          </div>
          <div className="w-px h-8 bg-white/10" />
          <div className="text-center">
            <p className="text-lg font-bold text-green-400">{tasks.filter(t => t.priority === 'high').length}</p>
            <p className="text-[10px] text-gray-600">Urgent</p>
          </div>
        </div>
      </div>
    </div>
  )
}
