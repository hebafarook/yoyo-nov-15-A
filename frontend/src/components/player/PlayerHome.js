import React from 'react';
import { Play, CheckCircle, Circle, Bell, TrendingUp, Calendar, Award, Flame } from 'lucide-react';

const PlayerHome = ({ onStartSession }) => {
  // Mock player data
  const player = {
    name: 'Alex Johnson',
    level: 'Gold',
    avatar: 'AJ',
    streak: 7,
    todayFocus: 'First Touch + Acceleration',
    sessionTime: '45-60 min'
  };

  const dailyChecklist = [
    { id: 1, task: 'Warm-up', completed: true },
    { id: 2, task: 'Main Drill Block 1', completed: true },
    { id: 3, task: 'Main Drill Block 2', completed: false },
    { id: 4, task: 'Recovery / Stretching', completed: false },
    { id: 5, task: 'Nutrition Check', completed: false }
  ];

  const upcomingSessions = [
    { id: 1, date: 'Today', time: '16:00', type: 'Technical', title: 'Ball Control Session' },
    { id: 2, date: 'Tomorrow', time: '17:00', type: 'Conditioning', title: 'Speed & Agility' },
    { id: 3, date: 'Thu', time: '16:00', type: 'Match Prep', title: 'Team Tactical' }
  ];

  const quickStats = [
    { label: 'Last Assessment', value: '92', color: 'text-green-600' },
    { label: '7-Day Completion', value: '86%', color: 'text-blue-600' },
    { label: 'Coach Rating', value: '4.8', color: 'text-yellow-600' }
  ];

  const notifications = [
    { id: 1, text: 'Coach updated your plan', icon: Calendar, time: '2h ago' },
    { id: 2, text: 'New challenge unlocked', icon: Award, time: '5h ago' }
  ];

  const completedCount = dailyChecklist.filter(item => item.completed).length;
  const progressPercent = Math.round((completedCount / dailyChecklist.length) * 100);

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Top Bar */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div className="w-16 h-16 bg-white rounded-full flex items-center justify-center text-2xl font-bold text-blue-600">
              {player.avatar}
            </div>
            <div>
              <h2 className="text-2xl font-bold">{player.name}</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="px-3 py-1 bg-white/20 rounded-full text-xs font-medium">
                  {player.level} Level
                </span>
                <div className="flex items-center gap-1">
                  <Flame className="w-4 h-4" />
                  <span className="text-sm font-bold">{player.streak} day streak</span>
                </div>
              </div>
            </div>
          </div>
          <button className="p-2 bg-white/20 rounded-lg hover:bg-white/30 transition">
            <Bell className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Today's Focus Card */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-start justify-between mb-4">
          <div>
            <h3 className="text-2xl font-bold text-gray-800 mb-2">Today's Focus</h3>
            <p className="text-lg text-gray-600">{player.todayFocus}</p>
            <p className="text-sm text-gray-500 mt-1">⏱️ {player.sessionTime}</p>
          </div>
          <button
            onClick={onStartSession}
            className="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold hover:bg-blue-700 transition flex items-center gap-2 shadow-lg"
          >
            <Play className="w-5 h-5" />
            Start Session
          </button>
        </div>
      </div>

      {/* Daily Checklist */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-gray-800">Daily Checklist</h3>
          <span className="text-sm font-medium text-gray-600">{completedCount}/{dailyChecklist.length} completed</span>
        </div>
        <div className="mb-4">
          <div className="w-full bg-gray-200 rounded-full h-3">
            <div 
              className="bg-blue-600 h-3 rounded-full transition-all"
              style={{ width: `${progressPercent}%` }}
            ></div>
          </div>
        </div>
        <div className="space-y-3">
          {dailyChecklist.map((item) => (
            <div key={item.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg hover:bg-gray-100 transition">
              {item.completed ? (
                <CheckCircle className="w-6 h-6 text-green-600" />
              ) : (
                <Circle className="w-6 h-6 text-gray-400" />
              )}
              <span className={`text-sm font-medium ${
                item.completed ? 'text-gray-500 line-through' : 'text-gray-800'
              }`}>
                {item.task}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Upcoming Sessions */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Upcoming Sessions</h3>
        <div className="space-y-3">
          {upcomingSessions.map((session) => (
            <div key={session.id} className="flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
              <div className="flex items-center gap-3">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Calendar className="w-6 h-6 text-blue-600" />
                </div>
                <div>
                  <h4 className="font-semibold text-gray-800">{session.title}</h4>
                  <p className="text-sm text-gray-600">{session.date} at {session.time}</p>
                </div>
              </div>
              <span className="px-3 py-1 bg-blue-100 text-blue-600 rounded-full text-xs font-medium">
                {session.type}
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-3 gap-4">
        {quickStats.map((stat, idx) => (
          <div key={idx} className="bg-white rounded-2xl p-4 shadow-lg border border-gray-200 text-center">
            <div className={`text-3xl font-bold ${stat.color} mb-1`}>{stat.value}</div>
            <div className="text-xs text-gray-600">{stat.label}</div>
          </div>
        ))}
      </div>

      {/* Notifications */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Recent Updates</h3>
        <div className="space-y-3">
          {notifications.map((notif) => {
            const Icon = notif.icon;
            return (
              <div key={notif.id} className="flex items-center gap-3 p-3 bg-gray-50 rounded-lg">
                <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                  <Icon className="w-5 h-5 text-blue-600" />
                </div>
                <div className="flex-1">
                  <p className="text-sm font-medium text-gray-800">{notif.text}</p>
                  <p className="text-xs text-gray-500">{notif.time}</p>
                </div>
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
};

export default PlayerHome;