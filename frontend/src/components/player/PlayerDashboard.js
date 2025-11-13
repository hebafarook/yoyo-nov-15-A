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
import { Home, Activity, Calendar, FileText, TrendingUp, Heart, MessageSquare, User } from 'lucide-react';

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
    { id: 'messages', label: 'Chat', icon: MessageSquare },
    { id: 'profile', label: 'Profile', icon: User }
  ];

  const renderContent = () => {
    switch (activeTab) {
      case 'home': return <PlayerHome onStartSession={() => setActiveTab('training')} />;
      case 'training': return <PlayerTodaySession />;
      case 'plan': return <PlayerTrainingPlan />;
      case 'assessments': return <PlayerAssessmentHistory />;
      case 'progress': return <PlayerProgress />;
      case 'recovery': return <PlayerRecovery />;
      case 'messages': return <PlayerMessages />;
      case 'profile': return <PlayerProfile />;
      default: return <PlayerHome onStartSession={() => setActiveTab('training')} />;
    }
  };

  return (
    <div className="flex flex-col h-screen bg-gray-50">
      {/* Main Content */}
      <div className="flex-1 overflow-auto pb-20">
        {renderContent()}
      </div>

      {/* Bottom Navigation */}
      <div className="fixed bottom-0 left-0 right-0 bg-white border-t border-gray-200 shadow-lg z-50">
        <div className="max-w-7xl mx-auto px-4">
          <div className="flex justify-around items-center py-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`flex flex-col items-center gap-1 px-3 py-2 rounded-lg transition ${
                    activeTab === item.id
                      ? 'text-blue-600 bg-blue-50'
                      : 'text-gray-600 hover:text-gray-900'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-xs font-medium">{item.label}</span>
                </button>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};

export default PlayerDashboard;