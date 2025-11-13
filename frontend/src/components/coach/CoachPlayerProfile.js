import React, { useState } from 'react';
import { ArrowLeft, Calendar, MessageSquare, Plus, TrendingUp, AlertTriangle } from 'lucide-react';
import { RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CoachPlayerProfile = ({ player, onBack }) => {
  const [activeTab, setActiveTab] = useState('overview');

  // Radar chart data for skills
  const radarData = [
    { skill: 'Speed', value: 85, fullMark: 100 },
    { skill: 'Agility', value: 78, fullMark: 100 },
    { skill: 'Strength', value: 72, fullMark: 100 },
    { skill: 'Stamina', value: 88, fullMark: 100 },
    { skill: 'Technical', value: 90, fullMark: 100 },
    { skill: 'Tactical', value: 75, fullMark: 100 }
  ];

  // Assessment history
  const assessmentHistory = [
    { date: '2024-03-01', overall: 92, physical: 88, technical: 95, tactical: 90 },
    { date: '2024-02-15', overall: 88, physical: 85, technical: 92, tactical: 86 },
    { date: '2024-02-01', overall: 85, physical: 82, technical: 88, tactical: 84 },
    { date: '2024-01-15', overall: 82, physical: 80, technical: 85, tactical: 80 }
  ];

  // AI Training Plan
  const aiPlan = {
    focus: 'Tactical Awareness & Left Foot Development',
    weeklyProgram: [
      { day: 'Monday', focus: 'Speed & Agility', duration: '60 min', intensity: 'High' },
      { day: 'Tuesday', focus: 'Left Foot Technique', duration: '90 min', intensity: 'Medium' },
      { day: 'Wednesday', focus: 'Recovery', duration: '45 min', intensity: 'Low' },
      { day: 'Thursday', focus: 'Tactical Positioning', duration: '75 min', intensity: 'High' },
      { day: 'Friday', focus: 'Match Simulation', duration: '90 min', intensity: 'High' },
      { day: 'Saturday', focus: 'Game Day', duration: '90 min', intensity: 'Match' },
      { day: 'Sunday', focus: 'Active Recovery', duration: '30 min', intensity: 'Low' }
    ]
  };

  const strengths = [
    'Exceptional ball control under pressure',
    'High-speed dribbling ability',
    'Strong work rate and stamina',
    'Quick decision making'
  ];

  const weaknesses = [
    'Left foot finishing accuracy (62%)',
    'Tactical positioning in defensive transitions',
    'Aerial duels win rate (58%)'
  ];

  const recoveryStatus = {
    score: 85,
    status: 'Good',
    lastWorkload: 'High',
    recommendation: 'Continue with normal training load'
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-white/70 hover:text-white transition"
        >
          <ArrowLeft className="w-5 h-5" />
          Back to Players
        </button>
      </div>

      {/* Player Summary Card */}
      <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <div className="flex items-start gap-6">
          <div className="w-32 h-32 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-3xl flex items-center justify-center text-4xl font-bold shadow-2xl shadow-[#4DFF91]/30">
            {player.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div className="flex-1">
            <h1 className="text-4xl font-bold mb-2">{player.name}</h1>
            <div className="flex flex-wrap gap-4 text-white/80 mb-4">
              <span>{player.position}</span>
              <span>•</span>
              <span>{player.age} years</span>
              <span>•</span>
              <span>{player.height}</span>
              <span>•</span>
              <span>{player.weight}</span>
            </div>
            <div className="flex gap-3">
              <span className={`px-4 py-2 rounded-xl border text-sm font-medium ${
                player.level === 'Elite' ? 'bg-[#4DFF91]/20 text-[#4DFF91] border-[#4DFF91]/30' :
                player.level === 'Advanced' ? 'bg-[#007BFF]/20 text-[#007BFF] border-[#007BFF]/30' :
                'bg-[#FFD93D]/20 text-[#FFD93D] border-[#FFD93D]/30'
              }`}>
                {player.level}
              </span>
              <span className="px-4 py-2 rounded-xl border bg-white/5 text-white border-white/10 text-sm font-medium">
                Overall: {player.assessmentScore}
              </span>
            </div>
          </div>
          <div className="flex flex-col gap-3">
            <button className="px-6 py-3 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-semibold text-[#0C1A2A] hover:shadow-2xl hover:shadow-[#4DFF91]/30 transition flex items-center gap-2">
              <Plus className="w-4 h-4" />
              Assign Drill
            </button>
            <button className="px-6 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl font-semibold text-white hover:bg-white/20 transition flex items-center gap-2">
              <Calendar className="w-4 h-4" />
              New Assessment
            </button>
            <button className="px-6 py-3 bg-white/10 backdrop-blur-xl border border-white/20 rounded-xl font-semibold text-white hover:bg-white/20 transition flex items-center gap-2">
              <MessageSquare className="w-4 h-4" />
              Chat
            </button>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b border-white/10">
        {['overview', 'assessments', 'training', 'recovery'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 font-medium transition border-b-2 ${
              activeTab === tab
                ? 'border-[#4DFF91] text-[#4DFF91]'
                : 'border-transparent text-white/60 hover:text-white'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Tab Content */}
      {activeTab === 'overview' && (
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Skills Radar */}
          <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
            <h3 className="text-xl font-bold mb-6">Skills Overview</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={radarData}>
                <PolarGrid stroke="rgba(255,255,255,0.1)" />
                <PolarAngleAxis dataKey="skill" stroke="rgba(255,255,255,0.6)" />
                <PolarRadiusAxis stroke="rgba(255,255,255,0.3)" />
                <Radar name="Performance" dataKey="value" stroke="#4DFF91" fill="#4DFF91" fillOpacity={0.3} />
              </RadarChart>
            </ResponsiveContainer>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="space-y-6">
            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <TrendingUp className="w-5 h-5 text-[#4DFF91]" />
                <h3 className="text-xl font-bold">Strengths</h3>
              </div>
              <ul className="space-y-3">
                {strengths.map((strength, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-white/80">
                    <span className="text-[#4DFF91] mt-1">•</span>
                    <span>{strength}</span>
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
              <div className="flex items-center gap-2 mb-4">
                <AlertTriangle className="w-5 h-5 text-[#FFD93D]" />
                <h3 className="text-xl font-bold">Areas for Improvement</h3>
              </div>
              <ul className="space-y-3">
                {weaknesses.map((weakness, idx) => (
                  <li key={idx} className="flex items-start gap-2 text-white/80">
                    <span className="text-[#FFD93D] mt-1">•</span>
                    <span>{weakness}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>
        </div>
      )}

      {activeTab === 'assessments' && (
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <h3 className="text-xl font-bold mb-6">Assessment History</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={assessmentHistory}>
              <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.1)" />
              <XAxis dataKey="date" stroke="rgba(255,255,255,0.6)" />
              <YAxis stroke="rgba(255,255,255,0.6)" />
              <Tooltip contentStyle={{ backgroundColor: '#0C1A2A', border: '1px solid rgba(77, 255, 145, 0.3)', borderRadius: '12px' }} />
              <Legend />
              <Line type="monotone" dataKey="overall" stroke="#4DFF91" strokeWidth={2} />
              <Line type="monotone" dataKey="physical" stroke="#007BFF" strokeWidth={2} />
              <Line type="monotone" dataKey="technical" stroke="#FFD93D" strokeWidth={2} />
              <Line type="monotone" dataKey="tactical" stroke="#FF6B6B" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      )}

      {activeTab === 'training' && (
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <div className="flex items-center justify-between mb-6">
            <h3 className="text-xl font-bold">AI-Generated Training Plan</h3>
            <span className="text-sm text-[#4DFF91]">Auto-updated</span>
          </div>
          <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 rounded-xl p-4 mb-6">
            <p className="text-sm text-white/80">
              <strong className="text-white">Focus:</strong> {aiPlan.focus}
            </p>
          </div>
          <div className="space-y-3">
            {aiPlan.weeklyProgram.map((session, idx) => (
              <div key={idx} className="bg-white/5 border border-white/10 rounded-xl p-4 flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-lg flex items-center justify-center text-sm font-bold">
                    {session.day.slice(0, 3)}
                  </div>
                  <div>
                    <h4 className="font-semibold">{session.focus}</h4>
                    <p className="text-sm text-white/60">{session.duration}</p>
                  </div>
                </div>
                <span className={`px-3 py-1 rounded-full text-xs font-medium ${
                  session.intensity === 'High' ? 'bg-[#FF6B6B]/20 text-[#FF6B6B]' :
                  session.intensity === 'Medium' ? 'bg-[#FFD93D]/20 text-[#FFD93D]' :
                  session.intensity === 'Match' ? 'bg-[#4DFF91]/20 text-[#4DFF91]' :
                  'bg-white/10 text-white/60'
                }`}>
                  {session.intensity}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {activeTab === 'recovery' && (
        <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-6">
          <h3 className="text-xl font-bold mb-6">Recovery Status</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="bg-gradient-to-r from-[#4DFF91]/10 to-[#007BFF]/10 rounded-xl p-6">
              <div className="text-center mb-4">
                <div className="text-6xl font-bold text-[#4DFF91] mb-2">{recoveryStatus.score}</div>
                <div className="text-sm text-white/60">Recovery Score</div>
              </div>
              <div className="w-full bg-white/10 rounded-full h-3">
                <div 
                  className="bg-gradient-to-r from-[#4DFF91] to-[#007BFF] h-3 rounded-full"
                  style={{ width: `${recoveryStatus.score}%` }}
                ></div>
              </div>
            </div>
            <div className="space-y-4">
              <div className="bg-white/5 rounded-xl p-4">
                <div className="text-sm text-white/60 mb-1">Status</div>
                <div className="text-lg font-bold text-[#4DFF91]">{recoveryStatus.status}</div>
              </div>
              <div className="bg-white/5 rounded-xl p-4">
                <div className="text-sm text-white/60 mb-1">Last Workload</div>
                <div className="text-lg font-bold">{recoveryStatus.lastWorkload}</div>
              </div>
              <div className="bg-white/5 rounded-xl p-4">
                <div className="text-sm text-white/60 mb-1">Recommendation</div>
                <div className="text-sm">{recoveryStatus.recommendation}</div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CoachPlayerProfile;