import React, { useState } from 'react';
import { TrendingUp, Award } from 'lucide-react';
import { LineChart, Line, BarChart, Bar, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const PlayerProgress = () => {
  const [activeTab, setActiveTab] = useState('overall');

  const consistencyData = [
    { week: 'W1', completion: 80 },
    { week: 'W2', completion: 85 },
    { week: 'W3', completion: 90 },
    { week: 'W4', completion: 75 },
    { week: 'W5', completion: 95 },
    { week: 'W6', completion: 88 }
  ];

  const technicalData = [
    { assessment: 'Jan', dribbling: 85, passing: 80, shooting: 75 },
    { assessment: 'Feb', dribbling: 88, passing: 85, shooting: 80 },
    { assessment: 'Mar', dribbling: 92, passing: 88, shooting: 85 }
  ];

  const skillProfile = [
    { skill: 'Speed', current: 92, threeMonthsAgo: 85 },
    { skill: 'Agility', current: 90, threeMonthsAgo: 82 },
    { skill: 'Stamina', current: 88, threeMonthsAgo: 85 },
    { skill: 'Technical', current: 95, threeMonthsAgo: 88 },
    { skill: 'Tactical', current: 85, threeMonthsAgo: 78 },
    { skill: 'Mental', current: 90, threeMonthsAgo: 85 }
  ];

  const achievements = [
    { id: 1, title: '7-Day Streak', icon: '🔥', earned: '2024-03-15' },
    { id: 2, title: 'Speed Milestone', icon: '⚡', earned: '2024-03-10' },
    { id: 3, title: '80%+ Month', icon: '🏆', earned: '2024-02-28' },
    { id: 4, title: 'First Touch Master', icon: '⚽', earned: '2024-02-15' }
  ];

  const coachFeedback = [
    '"Your left foot has improved dramatically!" - Coach Mike',
    '"Great work on tactical awareness" - Coach Sarah',
    '"Keep up the consistency!" - Coach Mike'
  ];

  return (
    <div className="max-w-6xl mx-auto p-6 space-y-6">
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-6 text-white shadow-lg">
        <h2 className="text-3xl font-bold mb-2">My Progress</h2>
        <p className="text-white/90">See how you're improving over time</p>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 overflow-x-auto pb-2">
        {['overall', 'technical', 'physical'].map((tab) => (
          <button
            key={tab}
            onClick={() => setActiveTab(tab)}
            className={`px-6 py-3 rounded-xl font-medium whitespace-nowrap transition ${
              activeTab === tab
                ? 'bg-blue-600 text-white shadow-lg'
                : 'bg-white text-gray-700 hover:bg-gray-50 border border-gray-200'
            }`}
          >
            {tab.charAt(0).toUpperCase() + tab.slice(1)}
          </button>
        ))}
      </div>

      {/* Overall Tab */}
      {activeTab === 'overall' && (
        <div className="space-y-6">
          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Training Consistency</h3>
            <ResponsiveContainer width="100%" height={250}>
              <LineChart data={consistencyData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="week" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Line type="monotone" dataKey="completion" stroke="#3b82f6" strokeWidth={2} />
              </LineChart>
            </ResponsiveContainer>
          </div>

          <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
            <h3 className="text-xl font-bold text-gray-800 mb-4">Skill Profile Comparison</h3>
            <ResponsiveContainer width="100%" height={300}>
              <RadarChart data={skillProfile}>
                <PolarGrid stroke="#e5e7eb" />
                <PolarAngleAxis dataKey="skill" />
                <PolarRadiusAxis domain={[0, 100]} />
                <Radar name="Now" dataKey="current" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} />
                <Radar name="3 Months Ago" dataKey="threeMonthsAgo" stroke="#9ca3af" fill="#9ca3af" fillOpacity={0.2} />
                <Legend />
              </RadarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}

      {/* Technical Tab */}
      {activeTab === 'technical' && (
        <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Technical Scores Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={technicalData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="assessment" />
              <YAxis domain={[0, 100]} />
              <Tooltip />
              <Legend />
              <Bar dataKey="dribbling" fill="#3b82f6" />
              <Bar dataKey="passing" fill="#8b5cf6" />
              <Bar dataKey="shooting" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </div>
      )}

      {/* Achievements */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <div className="flex items-center gap-2 mb-4">
          <Award className="w-6 h-6 text-yellow-500" />
          <h3 className="text-xl font-bold text-gray-800">Achievements</h3>
        </div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          {achievements.map((achievement) => (
            <div key={achievement.id} className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-xl p-4 text-center border border-yellow-200">
              <div className="text-4xl mb-2">{achievement.icon}</div>
              <div className="font-bold text-gray-800 text-sm mb-1">{achievement.title}</div>
              <div className="text-xs text-gray-600">{achievement.earned}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Coach Feedback */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Coach Feedback</h3>
        <div className="space-y-3">
          {coachFeedback.map((feedback, idx) => (
            <div key={idx} className="bg-blue-50 rounded-xl p-4">
              <p className="text-gray-700 italic">{feedback}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PlayerProgress;