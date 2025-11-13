import React, { useState, useEffect } from 'react';
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
import PlayerTrainingPrograms from './PlayerTrainingPrograms';
import { Home, Activity, Calendar, FileText, TrendingUp, Heart, Trophy, BarChart3, Inbox, ClipboardCheck, LogOut } from 'lucide-react';

const PlayerDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('home');
  const [isFirstTime, setIsFirstTime] = useState(false);
  const [checkingFirstTime, setCheckingFirstTime] = useState(true);

  const handleLogout = () => {
    console.log('Logout button clicked');
    try {
      if (window.confirm('Are you sure you want to logout?')) {
        console.log('User confirmed logout');
        logout();
      } else {
        console.log('User cancelled logout');
      }
    } catch (error) {
      console.error('Error during logout:', error);
      alert('Error logging out. Please try again.');
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
    { id: 'training', label: 'Today Session', icon: Activity },
    { id: 'training-program', label: 'Training Program', icon: Calendar },
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
    setIsFirstTime(false);
    
    // Show success message and guide to next steps
    setTimeout(() => {
      alert(`🎉 CONGRATULATIONS! Your baseline assessment is complete!

✅ Your assessment has been saved as your BASELINE BENCHMARK
✅ AI is analyzing your data and generating personalized programs
✅ Your Professional Report is ready to view

NEXT STEPS:
1. View your Professional Report (opens in new tab)
2. Generate your Training Program from the report
3. Start tracking your progress!

You can now access all features in your Player Portal!`);
      
      // Navigate to My Report tab to see the generated comprehensive report
      setActiveTab('report');
      
      // Refresh the page to update sidebar state
      window.location.reload();
    }, 1000);
  };

  const renderContent = () => {
    // Show loading while checking first-time status
    if (checkingFirstTime) {
      return (
        <div className="flex items-center justify-center h-full">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading your dashboard...</p>
          </div>
        </div>
      );
    }

    // Show first-time welcome banner
    const content = (() => {
      switch (activeTab) {
        case 'home': return <PlayerHome onStartSession={() => setActiveTab('training')} onTakeAssessment={() => setActiveTab('take-assessment')} />;
        case 'training': return <PlayerTodaySession />;
        case 'training-program': return <PlayerTrainingPrograms onNavigateToAssessment={() => setActiveTab('take-assessment')} />;
        case 'take-assessment': return <PlayerAssessmentForm onAssessmentComplete={handleAssessmentComplete} isFirstTime={isFirstTime} />;
        case 'assessments': return <PlayerAssessmentHistory />;
        case 'progress': return <PlayerProgress />;
        case 'recovery': return <PlayerRecovery />;
        case 'report': return <PlayerReportCard />;
        case 'achievements': return <AchievementsDisplay />;
        case 'inbox': return <InboxDashboard />;
        default: return <PlayerHome onStartSession={() => setActiveTab('training')} onTakeAssessment={() => setActiveTab('take-assessment')} />;
      }
    })();

    return (
      <>
        {isFirstTime && activeTab === 'take-assessment' && (
          <div className="mb-6 bg-gradient-to-r from-blue-600 to-blue-800 rounded-xl p-6 text-white shadow-lg">
            <h2 className="text-2xl font-bold mb-2">🎉 Welcome to Your Soccer Development Journey!</h2>
            <p className="text-white/90 mb-4">
              Let's start by completing your first assessment. This will help us create a personalized training program and comprehensive roadmap for your development.
            </p>
            <div className="bg-white/10 rounded-lg p-4 backdrop-blur-sm">
              <h3 className="font-bold mb-2">What happens next:</h3>
              <ul className="space-y-2 text-sm">
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400 font-bold">1.</span>
                  <span>Complete your assessment with all your current metrics</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400 font-bold">2.</span>
                  <span>AI will analyze your data and create your personalized training program</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400 font-bold">3.</span>
                  <span>You'll receive a comprehensive report with coach recommendations and AI standards</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-yellow-400 font-bold">4.</span>
                  <span>Your development roadmap will be ready - printable and saveable!</span>
                </li>
              </ul>
            </div>
          </div>
        )}
        {content}
      </>
    );
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
            type="button"
            onClick={(e) => {
              e.preventDefault();
              e.stopPropagation();
              handleLogout();
            }}
            className="w-full flex items-center justify-center space-x-2 px-4 py-2.5 bg-red-50 text-red-600 rounded-lg hover:bg-red-100 transition font-medium text-sm border border-red-200"
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