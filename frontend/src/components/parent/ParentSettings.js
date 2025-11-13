import React, { useState } from 'react';
import { User, Mail, Phone, Lock, Bell } from 'lucide-react';
import { useAuth } from '../../contexts/AuthContext';

const ParentSettings = () => {
  const { user } = useAuth();
  const [notifications, setNotifications] = useState({
    missedTraining: true,
    newAssessment: true,
    injuryFlagged: true,
    newCoachMessage: true,
    billingAlerts: true
  });

  const [privacy, setPrivacy] = useState({
    anonymizedData: false,
    shareHighlights: true
  });

  const handleSaveProfile = (e) => {
    e.preventDefault();
    alert('Profile updated successfully!');
  };

  const handleSaveNotifications = () => {
    alert('Notification preferences saved!');
  };

  const handleSavePrivacy = () => {
    alert('Privacy settings saved!');
  };

  return (
    <div className="space-y-6">
      {/* Parent Profile */}
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-2xl font-bold text-gray-800 mb-6">Parent Profile</h2>
        <form onSubmit={handleSaveProfile} className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <User className="w-4 h-4" />
                First Name
              </label>
              <input
                type="text"
                defaultValue={user?.full_name?.split(' ')[0] || ''}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
            <div>
              <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
                <User className="w-4 h-4" />
                Last Name
              </label>
              <input
                type="text"
                defaultValue={user?.full_name?.split(' ')[1] || ''}
                className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Mail className="w-4 h-4" />
              Email
            </label>
            <input
              type="email"
              defaultValue={user?.email || ''}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Phone className="w-4 h-4" />
              Phone
            </label>
            <input
              type="tel"
              placeholder="+1 (555) 123-4567"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
          </div>

          <div>
            <label className="flex items-center gap-2 text-sm font-medium text-gray-700 mb-2">
              <Lock className="w-4 h-4" />
              Change Password
            </label>
            <button
              type="button"
              className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200 transition"
            >
              Change Password
            </button>
          </div>

          <button
            type="submit"
            className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
          >
            Save Profile
          </button>
        </form>
      </div>

      {/* Notification Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4 flex items-center gap-2">
          <Bell className="w-5 h-5" />
          Notification Preferences
        </h3>
        <div className="space-y-4">
          {[
            { key: 'missedTraining', label: 'Missed training alerts' },
            { key: 'newAssessment', label: 'New assessment uploaded' },
            { key: 'injuryFlagged', label: 'Injury flagged in logs' },
            { key: 'newCoachMessage', label: 'New coach message' },
            { key: 'billingAlerts', label: 'Billing / payment alerts' }
          ].map(({ key, label }) => (
            <div key={key} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
              <span className="text-sm text-gray-700">{label}</span>
              <button
                onClick={() => setNotifications({ ...notifications, [key]: !notifications[key] })}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
                  notifications[key] ? 'bg-blue-600' : 'bg-gray-300'
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
        <button
          onClick={handleSaveNotifications}
          className="w-full mt-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
        >
          Save Preferences
        </button>
      </div>

      {/* Privacy Settings */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-bold text-gray-800 mb-4">Privacy & Child Profile</h3>
        <div className="space-y-4">
          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <span className="text-sm font-medium text-gray-700">Allow anonymized data usage</span>
              <p className="text-xs text-gray-600">Help improve AI training algorithms</p>
            </div>
            <button
              onClick={() => setPrivacy({ ...privacy, anonymizedData: !privacy.anonymizedData })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
                privacy.anonymizedData ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                  privacy.anonymizedData ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>

          <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
            <div>
              <span className="text-sm font-medium text-gray-700">Allow sharing highlights with coach</span>
              <p className="text-xs text-gray-600">Coach can view training videos and progress</p>
            </div>
            <button
              onClick={() => setPrivacy({ ...privacy, shareHighlights: !privacy.shareHighlights })}
              className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
                privacy.shareHighlights ? 'bg-blue-600' : 'bg-gray-300'
              }`}
            >
              <span
                className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                  privacy.shareHighlights ? 'translate-x-6' : 'translate-x-1'
                }`}
              />
            </button>
          </div>
        </div>
        <button
          onClick={handleSavePrivacy}
          className="w-full mt-4 py-2 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition"
        >
          Save Settings
        </button>
      </div>
    </div>
  );
};

export default ParentSettings;