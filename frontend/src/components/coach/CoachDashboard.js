import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import CoachIntro from './CoachIntro';
import CoachMainDashboard from './CoachMainDashboard';
import CoachPlayerList from './CoachPlayerList';
import CoachPlayerProfile from './CoachPlayerProfile';
import CoachAssessmentManagement from './CoachAssessmentManagement';
import CoachAssessmentReport from './CoachAssessmentReport';
import CoachDrillLibrary from './CoachDrillLibrary';
import CoachAITrainingGenerator from './CoachAITrainingGenerator';
import CoachTeamManagement from './CoachTeamManagement';
import CoachRecovery from './CoachRecovery';
import CoachMessages from './CoachMessages';
import CoachSettings from './CoachSettings';
import { 
  Home, Users, FileText, Activity, Book, Zap, Shield, MessageSquare, 
  Settings, Bell, Search, Menu, X, Heart, LogOut 
} from 'lucide-react';

const CoachDashboard = () => {
  const { user, logout } = useAuth();
  const [activeScreen, setActiveScreen] = useState('main');

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };
  const [selectedPlayer, setSelectedPlayer] = useState(null);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [showIntro, setShowIntro] = useState(false);

  const navItems = [
    { id: 'main', label: 'Dashboard', icon: Home },
    { id: 'players', label: 'Players', icon: Users },
    { id: 'assessments', label: 'Assessments', icon: FileText },
    { id: 'drills', label: 'Drill Library', icon: Book },
    { id: 'ai-planner', label: 'AI Planner', icon: Zap },
    { id: 'teams', label: 'Teams', icon: Shield },
    { id: 'recovery', label: 'Recovery', icon: Heart },
    { id: 'messages', label: 'Messages', icon: MessageSquare },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const renderScreen = () => {
    if (activeScreen === 'player-profile' && selectedPlayer) {
      return <CoachPlayerProfile player={selectedPlayer} onBack={() => setActiveScreen('players')} />;
    }
    if (activeScreen === 'assessment-report' && selectedAssessment) {
      return <CoachAssessmentReport assessment={selectedAssessment} onBack={() => setActiveScreen('assessments')} />;
    }

    switch (activeScreen) {
      case 'main': return <CoachMainDashboard onNavigate={setActiveScreen} />;
      case 'players': return <CoachPlayerList onSelectPlayer={(player) => { setSelectedPlayer(player); setActiveScreen('player-profile'); }} />;
      case 'assessments': return <CoachAssessmentManagement onSelectAssessment={(assessment) => { setSelectedAssessment(assessment); setActiveScreen('assessment-report'); }} />;
      case 'drills': return <CoachDrillLibrary />;
      case 'ai-planner': return <CoachAITrainingGenerator />;
      case 'teams': return <CoachTeamManagement />;
      case 'recovery': return <CoachRecovery />;
      case 'messages': return <CoachMessages />;
      case 'settings': return <CoachSettings />;
      default: return <CoachMainDashboard onNavigate={setActiveScreen} />;
    }
  };

  if (showIntro) {
    return <CoachIntro onComplete={() => setShowIntro(false)} />;
  }

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${
        sidebarOpen ? 'w-64' : 'w-0'
      } bg-white border-r border-gray-200 transition-all duration-300 overflow-hidden shadow-sm`}>
        <div className="p-6">
          <div className="mb-8">
            <h1 className="text-2xl font-bold text-gray-800">
              YoYo Elite AI
            </h1>
            <p className="text-sm text-gray-600 mt-1">Coach Portal</p>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveScreen(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                    activeScreen === item.id || (activeScreen === 'player-profile' && item.id === 'players') || (activeScreen === 'assessment-report' && item.id === 'assessments')
                      ? 'bg-blue-50 text-blue-600 shadow-sm'
                      : 'text-gray-700 hover:bg-gray-50'
                  }`}
                >
                  <Icon className="w-5 h-5" />
                  <span className="text-sm font-medium">{item.label}</span>
                </button>
              );
            })}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Top Bar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 shadow-sm">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-100 rounded-lg transition"
              >
                {sidebarOpen ? <X className="w-5 h-5 text-gray-600" /> : <Menu className="w-5 h-5 text-gray-600" />}
              </button>

              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search players, drills, assessments..."
                  className="bg-gray-50 border border-gray-300 rounded-lg pl-10 pr-4 py-2 text-sm text-gray-900 placeholder-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 w-80"
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button className="relative p-2 hover:bg-gray-100 rounded-lg transition">
                <Bell className="w-5 h-5 text-gray-600" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-blue-600 rounded-full"></span>
              </button>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium text-gray-800">{user?.full_name || 'Coach'}</p>
                  <p className="text-xs text-gray-600">Head Coach</p>
                </div>
                <div className="w-10 h-10 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold">
                  {user?.full_name?.[0] || 'C'}
                </div>
              </div>

              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition"
                title="Logout"
              >
                <LogOut className="w-4 h-4" />
                <span className="text-sm font-medium">Logout</span>
              </button>
            </div>
          </div>
        </div>

        {/* Screen Content */}
        <div className="flex-1 overflow-auto p-6 bg-gray-50">
          {renderScreen()}
        </div>
      </div>
    </div>
  );
};

export default CoachDashboard;