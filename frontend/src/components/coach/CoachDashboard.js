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
  Settings, Bell, Search, Menu, X, Heart 
} from 'lucide-react';

const CoachDashboard = () => {
  const { user, logout } = useAuth();
  const [activeScreen, setActiveScreen] = useState('main');
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
    <div className="flex h-screen bg-gradient-to-br from-[#0C1A2A] to-[#1a2332] text-white">
      {/* Sidebar */}
      <div className={`${
        sidebarOpen ? 'w-64' : 'w-0'
      } bg-[#0C1A2A]/80 backdrop-blur-xl border-r border-white/10 transition-all duration-300 overflow-hidden`}>
        <div className="p-6">
          <div className="mb-8">
            <h1 className="text-2xl font-bold bg-gradient-to-r from-[#4DFF91] to-[#007BFF] bg-clip-text text-transparent">
              YoYo Elite AI
            </h1>
            <p className="text-sm text-white/60 mt-1">Coach Portal</p>
          </div>

          <nav className="space-y-2">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveScreen(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition ${
                    activeScreen === item.id || (activeScreen === 'player-profile' && item.id === 'players') || (activeScreen === 'assessment-report' && item.id === 'assessments')
                      ? 'bg-gradient-to-r from-[#4DFF91]/20 to-[#007BFF]/20 border border-[#4DFF91]/30 text-[#4DFF91] shadow-lg shadow-[#4DFF91]/20'
                      : 'text-white/70 hover:bg-white/5 hover:text-white'
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
        <div className="bg-[#0C1A2A]/60 backdrop-blur-xl border-b border-white/10 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-white/10 rounded-lg transition"
              >
                {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>

              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-white/40" />
                <input
                  type="text"
                  placeholder="Search players, drills, assessments..."
                  className="bg-white/5 border border-white/10 rounded-xl pl-10 pr-4 py-2 text-sm text-white placeholder-white/40 focus:outline-none focus:ring-2 focus:ring-[#4DFF91]/50 w-80"
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button className="relative p-2 hover:bg-white/10 rounded-lg transition">
                <Bell className="w-5 h-5" />
                <span className="absolute top-1 right-1 w-2 h-2 bg-[#4DFF91] rounded-full"></span>
              </button>

              <div className="flex items-center gap-3">
                <div className="text-right">
                  <p className="text-sm font-medium">{user?.full_name || 'Coach'}</p>
                  <p className="text-xs text-white/60">Head Coach</p>
                </div>
                <div className="w-10 h-10 bg-gradient-to-br from-[#4DFF91] to-[#007BFF] rounded-full flex items-center justify-center text-[#0C1A2A] font-bold">
                  {user?.full_name?.[0] || 'C'}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Screen Content */}
        <div className="flex-1 overflow-auto p-6">
          {renderScreen()}
        </div>
      </div>
    </div>
  );
};

export default CoachDashboard;