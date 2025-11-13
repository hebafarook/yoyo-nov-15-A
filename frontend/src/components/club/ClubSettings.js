import React from 'react';
import { Settings, Shield, Users, Bell, CreditCard } from 'lucide-react';

const ClubSettings = ({ clubId, clubData, onUpdate }) => {
  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-3xl font-bold text-white">Club Settings</h2>
        <p className="text-gray-400">Manage club configuration and permissions</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-green-400/20 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Settings className="w-6 h-6 text-green-400" />
            <h3 className="text-xl font-bold text-white">General Settings</h3>
          </div>
          <div className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-2">Club Name</label>
              <input
                type="text"
                defaultValue={clubData?.name}
                className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:border-green-400 focus:outline-none"
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">Club Code</label>
              <input
                type="text"
                defaultValue={clubData?.club_code}
                className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:border-green-400 focus:outline-none"
                disabled
              />
            </div>
            <div>
              <label className="block text-sm text-gray-400 mb-2">City</label>
              <input
                type="text"
                defaultValue={clubData?.city}
                className="w-full px-4 py-2 bg-gray-700/50 border border-gray-600 rounded-lg text-white focus:border-green-400 focus:outline-none"
              />
            </div>
          </div>
        </div>

        <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-purple-400/20 shadow-2xl">
          <div className="flex items-center gap-3 mb-4">
            <Shield className="w-6 h-6 text-purple-400" />
            <h3 className="text-xl font-bold text-white">Permissions</h3>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Club Admin</span>
              <span className="text-green-400 font-medium">Full Access</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Technical Director</span>
              <span className="text-blue-400 font-medium">Team Management</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-300">Coaches</span>
              <span className="text-yellow-400 font-medium">Team View</span>
            </div>
          </div>
        </div>
      </div>

      <div className="bg-gray-800/60 backdrop-blur-xl rounded-2xl p-6 border border-blue-400/20 shadow-2xl">
        <div className="flex items-center gap-3 mb-4">
          <CreditCard className="w-6 h-6 text-blue-400" />
          <h3 className="text-xl font-bold text-white">Subscription</h3>
        </div>
        <div className="flex items-center justify-between">
          <div>
            <p className="text-white font-medium">Current Plan</p>
            <p className="text-gray-400 text-sm">{clubData?.subscription_tier}</p>
          </div>
          <button className="px-4 py-2 bg-blue-500/20 text-blue-400 rounded-lg hover:bg-blue-500/30 transition">
            Upgrade
          </button>
        </div>
      </div>
    </div>
  );
};

export default ClubSettings;