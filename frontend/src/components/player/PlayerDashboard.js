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
import PlayerReportCard from './PlayerReportCard';
import { Home, Activity, Calendar, FileText, TrendingUp, Heart, Trophy, BarChart3, Inbox, ClipboardCheck } from 'lucide-react';

const PlayerDashboard = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('home');

  const navItems = [
    { id: 'home', label: 'Home', icon: Home },
    { id: 'training', label: 'Training', icon: Activity },
    { id: 'plan', label: 'Plan', icon: Calendar },
    { id: 'take-assessment', label: 'Take Assessment', icon: ClipboardCheck },
    { id: 'assessments', label: 'History', icon: FileText },
    { id: 'progress', label: 'Progress', icon: TrendingUp },
    { id: 'recovery', label: 'Recovery', icon: Heart },
    { id: 'report', label: 'My Report', icon: BarChart3 },
    { id: 'achievements', label: 'Achievements', icon: Trophy },
    { id: 'inbox', label: 'Inbox', icon: Inbox }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'home': return <PlayerHome onStartSession={() => setActiveTab('training')} onTakeAssessment={() => setActiveTab('take-assessment')} />;
      case 'training': return <PlayerTodaySession />;
      case 'plan': return <PlayerTrainingPlan />;
      case 'take-assessment': return <TakeAssessmentView />;
      case 'assessments': return <PlayerAssessmentHistory />;
      case 'progress': return <PlayerProgress />;
      case 'recovery': return <PlayerRecovery />;
      case 'report': return <PlayerReportCard />;
      case 'achievements': return <AchievementsDisplay />;
      case 'inbox': return <InboxDashboard />;
      default: return <PlayerHome onStartSession={() => setActiveTab('training')} onTakeAssessment={() => setActiveTab('take-assessment')} />;
    }
  };

  // Take Assessment View Component
  const TakeAssessmentView = () => {
    return (
      <div className="max-w-6xl mx-auto">
        <div className="bg-gradient-to-r from-indigo-600 via-purple-600 to-pink-600 rounded-2xl p-6 text-white shadow-lg border-2 border-yellow-400 mb-6">
          <h2 className="text-3xl font-bold mb-2">📝 Take Assessment</h2>
          <p className="text-white/90">Complete your performance assessment</p>
        </div>
        <div className="bg-white rounded-2xl p-8 shadow-lg border border-gray-200">
          <p className="text-gray-600 mb-4">The assessment form will be displayed here. This will redirect to the main assessment interface.</p>
          <button 
            onClick={() => {
              // Redirect to main assessment tab
              window.location.href = '/#assessment';
              window.location.reload();
            }}
            className="px-6 py-3 bg-gradient-to-r from-purple-600 to-indigo-600 text-white rounded-xl font-semibold hover:from-purple-700 hover:to-indigo-700 transition"
          >
            Go to Assessment Form
          </button>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      {/* Top Navigation - Royal Colors */}
      <div className="bg-gradient-to-r from-indigo-900 via-purple-900 to-pink-900 border-b-4 border-yellow-400 shadow-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* User Header with Player Info */}
          <div className="flex items-center justify-between py-3 border-b border-white/20">
            <div className="flex items-center space-x-4">
              <div className="w-14 h-14 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-full flex items-center justify-center text-indigo-900 font-bold text-2xl shadow-lg border-2 border-white">
                {(user?.username || 'P').substring(0, 1).toUpperCase()}
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">
                  {user?.full_name || user?.username || 'Player Dashboard'}
                </h1>
                <div className="flex items-center space-x-4 text-xs text-purple-200">
                  <span>⚡ Position: {user?.position || 'Forward'}</span>
                  <span>📅 Age: {user?.age || 17}</span>
                  <span>📏 Height: {user?.height || '175cm'}</span>
                  <span>⚖️ Weight: {user?.weight || '68kg'}</span>
                </div>
              </div>
            </div>
            <div className="text-right">
              <p className="text-xs text-purple-200">Joined</p>
              <p className="text-sm font-semibold text-yellow-400">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString() : 'Jan 2024'}
              </p>
            </div>
          </div>

          {/* Tabs Navigation - Royal Style */}
          <div className="flex space-x-1 overflow-x-auto py-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex items-center space-x-2 px-4 py-2 rounded-lg font-semibold text-sm whitespace-nowrap transition-all ${
                    activeTab === item.id
                      ? 'bg-yellow-400 text-indigo-900 shadow-lg transform scale-105'
                      : 'text-purple-100 hover:bg-white/10 hover:text-white'
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