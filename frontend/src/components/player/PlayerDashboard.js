import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import PlayerHome from './PlayerHome';
import PlayerTodaySession from './PlayerTodaySession';
import PlayerTrainingPlan from './PlayerTrainingPlan';
import PlayerAssessmentHistory from './PlayerAssessmentHistory';
import PlayerProgress from './PlayerProgress';
import PlayerRecovery from './PlayerRecovery';
import PlayerMessages from './PlayerMessages';
import PlayerProfile from './PlayerProfile';
import AchievementsDisplay from '../AchievementsDisplay';
import SavedReports from '../SavedReports';
import InboxDashboard from '../InboxDashboard';
import { Home, Activity, Calendar, FileText, TrendingUp, Heart, Trophy, BarChart3, Inbox } from 'lucide-react';

const PlayerDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('home');

  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'training', label: 'Training', icon: Activity },
    { id: 'plan', label: 'Plan', icon: Calendar },
    { id: 'assessments', label: 'Assessments', icon: FileText },
    { id: 'progress', label: 'Progress', icon: TrendingUp },
    { id: 'recovery', label: 'Recovery', icon: Heart },
    { id: 'achievements', label: 'Achievements', icon: Trophy },
    { id: 'reports', label: 'Reports', icon: BarChart3 },
    { id: 'inbox', label: 'Inbox', icon: Inbox }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'home': return <PlayerHome onStartSession={() => setActiveTab('training')} />;
      case 'training': return <PlayerTodaySession />;
      case 'plan': return <PlayerTrainingPlan />;
      case 'assessments': return <PlayerAssessmentHistory />;
      case 'progress': return <PlayerProgress />;
      case 'recovery': return <PlayerRecovery />;
      case 'achievements': return <AchievementsDisplay />;
      case 'reports': return <SavedReports />;
      case 'inbox': return <InboxDashboard />;
      default: return <PlayerHome onStartSession={() => setActiveTab('training')} />;
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 via-blue-50 to-indigo-50">
      {/* Top Navigation - Old Style */}
      <div className="bg-white border-b border-gray-200 shadow-sm sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between py-4">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-blue-600 to-indigo-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
                {(user?.username || 'P').substring(0, 1).toUpperCase()}
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">
                  {user?.full_name || user?.username || 'Player Dashboard'}
                </h1>
                <p className="text-sm text-gray-500">Welcome back!</p>
              </div>
            </div>
          </div>

          {/* Tabs Navigation - Old Style */}
          <div className="flex space-x-1 overflow-x-auto pb-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-medium text-sm whitespace-nowrap transition-all ${
                    activeTab === item.id
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-gray-600 hover:bg-gray-100 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-4 h-4" />
                  <span>{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        {renderContent()}
      </div>
    </div>
  );
};

export default PlayerDashboard;