import React from 'react';
import { Users, FileText, AlertTriangle, Calendar, TrendingUp, Activity, Zap, Target } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CoachMainDashboard = ({ onNavigate }) => {
  // Mock data
  const stats = [
    { label: 'Total Players', value: '42', change: '+3', icon: Users, color: 'from-[#4DFF91] to-[#00D9FF]' },
    { label: 'Assessments Due', value: '8', change: '+2', icon: FileText, color: 'from-[#FF6B6B] to-[#FFA07A]' },
    { label: 'Recovery Alerts', value: '3', change: '-1', icon: AlertTriangle, color: 'from-[#FFD93D] to-[#FF6B6B]' },
    { label: 'Sessions Today', value: '5', change: '+0', icon: Calendar, color: 'from-[#007BFF] to-[#4D9FFF]' }
  ];

  const playerStatusData = [
    { name: 'Marcus Silva', position: 'FW', level: 'Elite', status: 'Ready', progress: 92 },
    { name: 'Alex Johnson', position: 'MF', level: 'Advanced', status: 'Training', progress: 78 },
    { name: 'David Chen', position: 'DF', level: 'Intermediate', status: 'Recovery', progress: 65 },
    { name: 'Leo Martinez', position: 'GK', level: 'Elite', status: 'Ready', progress: 88 },
    { name: 'Jake Williams', position: 'FW', level: 'Advanced', status: 'Training', progress: 74 }
  ];

  const teamProgressData = [
    { month: 'Jan', physical: 65, technical: 70, tactical: 60 },
    { month: 'Feb', physical: 70, technical: 75, tactical: 65 },
    { month: 'Mar', physical: 75, technical: 80, tactical: 72 },
    { month: 'Apr', physical: 80, technical: 82, tactical: 78 },
    { month: 'May', physical: 85, technical: 88, tactical: 82 }
  ];

  const aiRecommendations = [
    { player: 'Marcus Silva', priority: 'High', suggestion: 'Increase sprint recovery time by 20%', category: 'Recovery' },
    { player: 'Alex Johnson', priority: 'Medium', suggestion: 'Focus on weak-foot passing drills', category: 'Technical' },
    { player: 'David Chen', priority: 'High', suggestion: 'Add tactical positioning sessions', category: 'Tactical' }
  ];

  const todaySessions = [
    { time: '09:00', title: 'U14 Speed & Agility', players: 12, status: 'Completed' },
    { time: '11:00', title: 'U16 Technical Training', players: 15, status: 'In Progress' },
    { time: '14:00', title: 'U18 Tactical Session', players: 18, status: 'Upcoming' },
    { time: '16:00', title: 'Elite Squad Fitness', players: 8, status: 'Upcoming' }
  ];

  const getStatusColor = (status) => {
    switch (status) {
      case 'Ready': return 'text-[#4DFF91]';
      case 'Training': return 'text-[#007BFF]';
      case 'Recovery': return 'text-[#FFD93D]';
      default: return 'text-white/60';
    }
  };

  const getPriorityColor = (priority) => {
    switch (priority) {
      case 'High': return 'bg-[#FF6B6B]/20 text-[#FF6B6B] border-[#FF6B6B]/30';
      case 'Medium': return 'bg-[#FFD93D]/20 text-[#FFD93D] border-[#FFD93D]/30';
      case 'Low': return 'bg-[#4DFF91]/20 text-[#4DFF91] border-[#4DFF91]/30';
      default: return 'bg-white/10 text-white border-white/20';
    }
  };

  return (
    <div className="space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
        <h2 className="text-3xl font-bold mb-2">Welcome Back, Coach</h2>
        <p className="text-white/70">Here's what's happening with your players today</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => {
          const Icon = stat.icon;
          return (
            <div key={idx} className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6 hover:scale-105 transition-transform cursor-pointer">
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 bg-gradient-to-br ${stat.color} rounded-xl flex items-center justify-center`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <span className="text-xs text-[#4DFF91] font-medium">{stat.change}</span>
              </div>
              <h3 className="text-3xl font-bold mb-1">{stat.value}</h3>
              <p className="text-sm text-white/60">{stat.label}</p>
            </div>
          );
        })}
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Player Status Grid */}
        <div className="lg:col-span-2 bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold">Player Status</h3>
            <button onClick={() => onNavigate('players')} className="text-sm text-[#4DFF91] hover:text-[#4DFF91]/80">
              View All →
            </button>
          </div>
          <div className="space-y-4">
            {playerStatusData.map((player, idx) => (
              <div key={idx} className="bg-white/5 border border-white/10 rounded-xl p-4 hover:bg-white/10 transition">
                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center gap-3">
                    <div className="w-10 h-10 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-full flex items-center justify-center text-sm font-bold">
                      {player.name.split(' ').map(n => n[0]).join('')}
                    </div>
                    <div>
                      <h4 className="font-semibold">{player.name}</h4>
                      <p className="text-xs text-white/60">{player.position} • {player.level}</p>
                    </div>
                  </div>
                  <span className={`text-sm font-medium ${getStatusColor(player.status)}`}>
                    {player.status}
                  </span>
                </div>
                <div className="w-full bg-white/10 rounded-full h-2">
                  <div 
                    className="bg-gradient-to-r from-[#4DFF91] to-[#007BFF] h-2 rounded-full transition-all"
                    style={{ width: `${player.progress}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Today's Sessions */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <h3 className="text-xl font-bold mb-6">Today's Sessions</h3>
          <div className="space-y-4">
            {todaySessions.map((session, idx) => (
              <div key={idx} className="border-l-4 border-[#4DFF91] bg-white/5 rounded-r-xl p-4">
                <div className="flex items-start justify-between mb-2">
                  <span className="text-sm font-bold text-[#4DFF91]">{session.time}</span>
                  <span className={`text-xs px-2 py-1 rounded-full ${
                    session.status === 'Completed' ? 'bg-[#4DFF91]/20 text-[#4DFF91]' :
                    session.status === 'In Progress' ? 'bg-[#007BFF]/20 text-[#007BFF]' :
                    'bg-white/10 text-white/60'
                  }`}>
                    {session.status}
                  </span>
                </div>
                <h4 className="font-semibold text-sm mb-1">{session.title}</h4>
                <p className="text-xs text-white/60">{session.players} players</p>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* AI Recommendations & Team Progress */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* AI Recommendations */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <div className="flex items-center gap-2 mb-6">
            <Zap className="w-5 h-5 text-[#4DFF91]" />
            <h3 className="text-xl font-bold">AI Recommendations</h3>
          </div>
          <div className="space-y-4">
            {aiRecommendations.map((rec, idx) => (
              <div key={idx} className="bg-white/5 border border-white/10 rounded-xl p-4">
                <div className="flex items-start justify-between mb-2">
                  <h4 className="font-semibold text-sm">{rec.player}</h4>
                  <span className={`text-xs px-2 py-1 rounded-full border ${getPriorityColor(rec.priority)}`}>
                    {rec.priority}
                  </span>
                </div>
                <p className="text-sm text-white/70 mb-2">{rec.suggestion}</p>
                <span className="text-xs text-[#4DFF91]">{rec.category}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Team Progress Chart */}
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <h3 className="text-xl font-bold mb-6">Team Progress</h3>
          <ResponsiveContainer width="100%" height={250}>
            <LineChart data={teamProgressData}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="month" stroke="rgba(255,255,255,0.6)" />
              <YAxis stroke="rgba(255,255,255,0.6)" />
              <Tooltip contentStyle={{ backgroundColor: '#0C1A2A', border: '1px solid rgba(77, 255, 145, 0.3)', borderRadius: '8px' }} />
              <Legend />
              <Line type="monotone" dataKey="physical" stroke="#4DFF91" strokeWidth={2} />
              <Line type="monotone" dataKey="technical" stroke="#007BFF" strokeWidth={2} />
              <Line type="monotone" dataKey="tactical" stroke="#FFD93D" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
};

export default CoachMainDashboard;