import React, { useState } from 'react';
import { User, Bell, Zap, Download, Shield } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const CoachSettings = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState({
    newAssessment: true,
    playerMessage: true,
    injuryAlert: true,
    weeklyReport: true,
    trainingReminder: false
  });

  const [aiSettings, setAiSettings] = useState({
    autoGenerate: true,
    difficulty: 'Medium',
    progressionRate: 'Moderate'
  });

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-3xl font-bold">Settings</h2>
        <p className="text-white/60 mt-1">Manage your coach portal preferences</p>
      </div>

      {/* Profile Section */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <User className="w-6 h-6 text-[#4DFF91]" />
          <h3 className="text-xl font-bold">Coach Profile</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label className="block text-sm font-medium mb-2">Full Name</label>
            <input
              type="text"
              defaultValue={user?.full_name || 'Coach Name'}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Email</label>
            <input
              type="email"
              defaultValue={user?.email || 'coach@example.com'}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Academy Name</label>
            <input
              type="text"
              defaultValue="YoYo Elite Academy"
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-2">Certification Level</label>
            <select className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50">
              <option>UEFA A License</option>
              <option>UEFA B License</option>
              <option>UEFA Pro License</option>
            </select>
          </div>
        </div>
        <button className="mt-6 px-6 py-3 bg-gradient-to-r from-[#4DFF91] to-[#007BFF] rounded-xl font-semibold text-[#0C1A2A] hover:shadow-2xl hover:shadow-[#4DFF91]/30 transition">
          Save Profile
        </button>
      </div>

      {/* Notification Preferences */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <Bell className="w-6 h-6 text-[#4DFF91]" />
          <h3 className="text-xl font-bold">Notification Preferences</h3>
        </div>
        <div className="space-y-4">
          {[
            { key: 'newAssessment', label: 'New Assessment Uploaded' },
            { key: 'playerMessage', label: 'Player Messages' },
            { key: 'injuryAlert', label: 'Injury Risk Alerts' },
            { key: 'weeklyReport', label: 'Weekly Team Reports' },
            { key: 'trainingReminder', label: 'Training Session Reminders' }
          ].map(({ key, label }) => (
            <div key={key} className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
              <span className="text-sm">{label}</span>
              <button
                onClick={() => setNotifications({ ...notifications, [key]: !notifications[key] })}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
                  notifications[key] ? 'bg-gradient-to-r from-[#4DFF91] to-[#007BFF]' : 'bg-white/20'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    notifications[key] ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          ))}
        </div>
      </div>

      {/* AI Model Settings */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <Zap className="w-6 h-6 text-[#4DFF91]" />
          <h3 className="text-xl font-bold">AI Model Settings</h3>
        </div>
        <div className="space-y-6">
          <div className="flex items-center justify-between p-4 bg-white/5 rounded-xl">
            <div>
              <div className="text-sm font-medium mb-1">Auto-Generate Training Plans</div>
              <div className="text-xs text-white/60">Automatically create plans after assessments</div>
            </div>
            <button
              onClick={() => setAiSettings({ ...aiSettings, autoGenerate: !aiSettings.autoGenerate })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
                aiSettings.autoGenerate ? 'bg-gradient-to-r from-[#4DFF91] to-[#007BFF]' : 'bg-white/20'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                  aiSettings.autoGenerate ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Default Difficulty Level</label>
            <select
              value={aiSettings.difficulty}
              onChange={(e) => setAiSettings({ ...aiSettings, difficulty: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
            >
              <option>Beginner</option>
              <option>Intermediate</option>
              <option>Advanced</option>
              <option>Elite</option>
            </select>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">Progression Rate</label>
            <select
              value={aiSettings.progressionRate}
              onChange={(e) => setAiSettings({ ...aiSettings, progressionRate: e.target.value })}
              className="w-full bg-white/5 border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50"
            >
              <option>Conservative</option>
              <option>Moderate</option>
              <option>Aggressive</option>
            </select>
          </div>
        </div>
      </div>

      {/* Data Export */}
      <div className="bg-white/5 backdrop-blur-xl border border-white/10 rounded-2xl p-8">
        <div className="flex items-center gap-3 mb-6">
          <Download className="w-6 h-6 text-[#4DFF91]" />
          <h3 className="text-xl font-bold">Export Data</h3>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <button className="p-4 bg-white/5 border border-white/10 rounded-xl text-left hover:bg-white/10 transition">
            <div className="font-medium mb-1">Player Data</div>
            <div className="text-xs text-white/60">Export all player assessments and progress</div>
          </button>
          <button className="p-4 bg-white/5 border border-white/10 rounded-xl text-left hover:bg-white/10 transition">
            <div className="font-medium mb-1">Training Plans</div>
            <div className="text-xs text-white/60">Download all generated training programs</div>
          </button>
          <button className="p-4 bg-white/5 border border-white/10 rounded-xl text-left hover:bg-white/10 transition">
            <div className="font-medium mb-1">Team Reports</div>
            <div className="text-xs text-white/60">Export weekly and monthly team analytics</div>
          </button>
          <button className="p-4 bg-white/5 border border-white/10 rounded-xl text-left hover:bg-white/10 transition">
            <div className="font-medium mb-1">Full Backup</div>
            <div className="text-xs text-white/60">Complete data backup in JSON format</div>
          </button>
        </div>
      </div>
    </div>
  );
};

export default CoachSettings;