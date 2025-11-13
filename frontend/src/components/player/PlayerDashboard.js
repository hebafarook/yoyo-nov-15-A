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
import PlayerAssessmentForm from './PlayerAssessmentForm';
import { Home, Activity, Calendar, FileText, TrendingUp, Heart, Trophy, BarChart3, Inbox, ClipboardCheck, LogOut } from 'lucide-react';

const PlayerDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('home');
  const [isFirstTime, setIsFirstTime] = useState(false);
  const [checkingFirstTime, setCheckingFirstTime] = useState(true);

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      logout();
    }
  };

  // Check if this is first-time player (no assessments)
  useEffect(() => {
    const checkFirstTimePlayer = async () => {
      try {
        const token = localStorage.getItem('token');
        const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
        const response = await fetch(`${BACKEND_URL}/api/auth/benchmarks`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        const benchmarks = await response.json();
        
        if (!benchmarks || benchmarks.length === 0) {
          // First-time player - no assessments yet
          setIsFirstTime(true);
          setActiveTab('take-assessment');
        }
        setCheckingFirstTime(false);
      } catch (error) {
        console.error('Error checking first-time status:', error);
        setCheckingFirstTime(false);
      }
    };

    if (user?.id) {
      checkFirstTimePlayer();
    }
  }, [user]);

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

  const handleAssessmentComplete = (assessment) => {
    console.log('Assessment completed:', assessment);
    // Navigate to My Report tab to see the generated report
    setActiveTab('report');
  };

  const renderContent = () => {
    switch (activeTab) {
      case 'home': return <PlayerHome onStartSession={() => setActiveTab('training')} onTakeAssessment={() => setActiveTab('take-assessment')} />;
      case 'training': return <PlayerTodaySession />;
      case 'plan': return <PlayerTrainingPlan />;
      case 'take-assessment': return <PlayerAssessmentForm onAssessmentComplete={handleAssessmentComplete} />;
      case 'assessments': return <PlayerAssessmentHistory />;
      case 'progress': return <PlayerProgress />;
      case 'recovery': return <PlayerRecovery />;
      case 'report': return <PlayerReportCard />;
      case 'achievements': return <AchievementsDisplay />;
      case 'inbox': return <InboxDashboard />;
      default: return <PlayerHome onStartSession={() => setActiveTab('training')} onTakeAssessment={() => setActiveTab('take-assessment')} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Elegant Sidebar - 2 Color Design */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col shadow-lg">
        {/* User Profile Section */}
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center space-x-3 mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-full flex items-center justify-center text-white font-bold text-lg">
              {(user?.username || 'P').substring(0, 1).toUpperCase()}
            </div>
            <div className="flex-1">
              <h2 className="text-sm font-bold text-gray-900 truncate">
                {user?.full_name || user?.username || 'Player'}
              </h2>
              <p className="text-xs text-gray-500">{user?.position || 'Forward'}</p>
            </div>
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="text-gray-600">
              <span className="block text-gray-400">Age</span>
              <span className="font-semibold text-gray-900">{user?.age || 17}</span>
            </div>
            <div className="text-gray-600">
              <span className="block text-gray-400">Height</span>
              <span className="font-semibold text-gray-900">{user?.height || '175cm'}</span>
            </div>
            <div className="text-gray-600">
              <span className="block text-gray-400">Weight</span>
              <span className="font-semibold text-gray-900">{user?.weight || '68kg'}</span>
            </div>
            <div className="text-gray-600">
              <span className="block text-gray-400">Foot</span>
              <span className="font-semibold text-gray-900">{user?.dominant_foot || 'Right'}</span>
            </div>
          </div>
        </div>

        {/* Navigation Menu */}
        <nav className="flex-1 overflow-y-auto py-4">
          <div className="px-3 space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    activeTab === item.id
                      ? 'bg-blue-600 text-white shadow-md'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span className="truncate">{item.label}</span>
                </button>
              );
            })}
          </div>
        </nav>

        {/* Logout Button */}
        <div className="p-4 border-t border-gray-200">
          <button
            onClick={handleLogout}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-gray-100 text-gray-700 rounded-lg hover:bg-gray-200 transition font-medium text-sm"
          >
            <LogOut className="w-4 h-4" />
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content Area */}
      <div className="flex-1 overflow-auto">
        {/* Top Header Bar */}
        <div className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10 shadow-sm">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {navItems.find(item => item.id === activeTab)?.label || 'Dashboard'}
              </h1>
              <p className="text-sm text-gray-500 mt-1">
                Welcome back, {user?.full_name || user?.username || 'Player'}
              </p>
            </div>
            <div className="text-right">
              <p className="text-xs text-gray-500">Member since</p>
              <p className="text-sm font-semibold text-gray-900">
                {user?.created_at ? new Date(user.created_at).toLocaleDateString('en-US', { month: 'short', year: 'numeric' }) : 'Jan 2024'}
              </p>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="p-6">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default PlayerDashboard;