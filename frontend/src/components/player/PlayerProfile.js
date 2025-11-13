import React from 'react';
import { User, Award, Settings, LogOut } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const PlayerProfile = () => {
  const { user, logout } = useAuth();

  const playerProfile = {
    name: user?.full_name || 'Alex Johnson',
    age: 16,
    position: 'Forward',
    preferredFoot: 'Right',
    level: 'Gold',
    badges: ['🔥', '⚡', '🏆', '⚽'],
    club: 'YoYo Elite Academy',
    team: 'U16 Premier',
    coach: 'Coach Mike',
    email: user?.email || 'alex.johnson@example.com'
  };

  return (
    <div className="max-w-4xl mx-auto p-6 space-y-6">
      {/* Profile Header */}
      <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-8 text-white shadow-lg border-2 border-yellow-400">
        <div className="flex items-center gap-6 mb-6">
          <div className="w-24 h-24 bg-yellow-400 rounded-full flex items-center justify-center text-4xl font-bold text-indigo-900">
            {playerProfile.name.split(' ').map(n => n[0]).join('')}
          </div>
          <div>
            <h2 className="text-3xl font-bold mb-2">{playerProfile.name}</h2>
            <div className="flex items-center gap-2">
              <span className="px-4 py-1 bg-white/20 rounded-full text-sm font-medium">
                {playerProfile.level} Level
              </span>
            </div>
          </div>
        </div>
        
        {/* Badges */}
        <div className="flex gap-3">
          {playerProfile.badges.map((badge, idx) => (
            <div key={idx} className="w-12 h-12 bg-white/20 rounded-lg flex items-center justify-center text-2xl">
              {badge}
            </div>
          ))}
        </div>
      </div>

      {/* Player Info */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Player Info</h3>
        <div className="grid grid-cols-2 gap-4">
          <div>
            <p className="text-sm text-gray-600 mb-1">Age</p>
            <p className="font-semibold text-gray-800">{playerProfile.age} years</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Position</p>
            <p className="font-semibold text-gray-800">{playerProfile.position}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Preferred Foot</p>
            <p className="font-semibold text-gray-800">{playerProfile.preferredFoot}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Level</p>
            <p className="font-semibold text-gray-800">{playerProfile.level}</p>
          </div>
        </div>
      </div>

      {/* Club & Team */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Club & Team</h3>
        <div className="space-y-3">
          <div>
            <p className="text-sm text-gray-600 mb-1">Club</p>
            <p className="font-semibold text-gray-800">{playerProfile.club}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Team</p>
            <p className="font-semibold text-gray-800">{playerProfile.team}</p>
          </div>
          <div>
            <p className="text-sm text-gray-600 mb-1">Coach</p>
            <p className="font-semibold text-gray-800">{playerProfile.coach}</p>
          </div>
        </div>
      </div>

      {/* App Settings */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">App Settings</h3>
        <div className="space-y-3">
          <button className="w-full flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
            <span className="font-medium text-gray-800">Notifications</span>
            <span className="text-sm text-blue-600">On</span>
          </button>
          <button className="w-full flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
            <span className="font-medium text-gray-800">Language</span>
            <span className="text-sm text-blue-600">English</span>
          </button>
          <button className="w-full flex items-center justify-between p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition">
            <span className="font-medium text-gray-800">Units</span>
            <span className="text-sm text-blue-600">Metric</span>
          </button>
        </div>
      </div>

      {/* Account */}
      <div className="bg-white rounded-2xl p-6 shadow-lg border border-gray-200">
        <h3 className="text-xl font-bold text-gray-800 mb-4">Account</h3>
        <div className="space-y-3">
          <div className="p-4 bg-gray-50 rounded-xl">
            <p className="text-sm text-gray-600 mb-1">Email</p>
            <p className="font-medium text-gray-800">{playerProfile.email}</p>
          </div>
          <button className="w-full py-3 bg-gray-100 text-gray-700 rounded-xl font-medium hover:bg-gray-200 transition">
            Change Password
          </button>
          <button
            onClick={logout}
            className="w-full py-3 bg-red-50 text-red-600 rounded-xl font-medium hover:bg-red-100 transition flex items-center justify-center gap-2"
          >
            <LogOut className="w-5 h-5" />
            Log Out
          </button>
        </div>
      </div>
    </div>
  );
};

export default PlayerProfile;