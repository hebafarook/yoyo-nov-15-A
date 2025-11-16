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
  const [activeTab, setActiveTab] = useState('take-assessment'); // Start with assessment for first-time check
  const [isFirstTime, setIsFirstTime] = useState(false);
  const [checkingFirstTime, setCheckingFirstTime] = useState(true);

  // Helper function to format height and weight based on user preferences
  const formatMeasurement = (value, type) => {
    if (!value) {
      // Default fallback values based on user's unit preference
      if (type === 'height') {
        return user?.height_unit === 'imperial' ? '5\'9"' : '175cm';
      } else if (type === 'weight') {
        return user?.weight_unit === 'imperial' ? '150lbs' : '68kg';
      }
    }
    return value;
  };

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
        
        console.log('🔍 Checking if player has previous assessments...');
        
        const response = await fetch(`${BACKEND_URL}/api/auth/benchmarks`, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        
        if (!response.ok) {
          throw new Error(`Failed to fetch benchmarks: ${response.status}`);
        }
        
        const benchmarks = await response.json();
        console.log('📊 Benchmarks received:', benchmarks);
        
        if (!benchmarks || benchmarks.length === 0) {
          // First-time player - no assessments yet - FORCE ASSESSMENT
          console.log('🎯 FIRST-TIME PLAYER - NO ASSESSMENTS FOUND');
          console.log('🔒 Forcing assessment screen - all other tabs locked');
          setIsFirstTime(true);
          setActiveTab('take-assessment');
        } else {
          // Existing player with assessments - allow home access
          console.log('✅ EXISTING PLAYER - Found', benchmarks.length, 'assessments');
          console.log('🏠 Allowing access to home screen');
          setIsFirstTime(false);
          setActiveTab('home');
        }
        setCheckingFirstTime(false);
      } catch (error) {
        console.error('❌ Error checking first-time status:', error);
        // On error, default to assessment screen to be safe
        console.log('⚠️ Error occurred - defaulting to assessment screen');
        setIsFirstTime(true);
        setActiveTab('take-assessment');
        setCheckingFirstTime(false);
      }
    };

    if (user?.id) {
      console.log('👤 User logged in:', user.username, '- Starting first-time check');
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
1. View your Professional Report
2. Generate your Training Program
3. Start tracking your progress!

All Player Portal features are now unlocked!

Redirecting to Home...`);
      
      // Navigate to home after first assessment
      setActiveTab('home');
      
      // Refresh the page to update sidebar state and clear first-time flag
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

    console.log('🎨 Rendering content for tab:', activeTab, '| First-time:', isFirstTime);

    // FORCE assessment for first-time players - override any other tab selection
    if (isFirstTime && activeTab !== 'take-assessment') {
      console.log('⚠️ WARNING: First-time player but wrong tab active. Forcing assessment...');
      setActiveTab('take-assessment');
    }

    // Show first-time welcome banner
    const content = (() => {
      // For first-time players, ONLY show assessment
      if (isFirstTime) {
        console.log('🎯 First-time player - ONLY showing assessment form');
        return <PlayerAssessmentForm onAssessmentComplete={handleAssessmentComplete} isFirstTime={isFirstTime} />;
      }

      // For existing players, show requested tab
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
          <div className="mb-6 bg-gradient-to-r from-green-600 via-blue-600 to-purple-600 rounded-xl p-6 text-white shadow-2xl border-4 border-yellow-400">
            <div className="text-center mb-4">
              <h2 className="text-3xl font-bold mb-2">🎯 BASELINE ASSESSMENT REQUIRED</h2>
              <div className="inline-block bg-yellow-400 text-gray-900 px-6 py-2 rounded-full font-bold text-sm mb-3">
                STEP 1 OF YOUR JOURNEY
              </div>
            </div>
            <p className="text-white/95 mb-4 text-center text-lg">
              Complete your first assessment to establish your BASELINE BENCHMARK and unlock all Player Portal features!
            </p>
            <div className="bg-white/15 rounded-lg p-5 backdrop-blur-sm border-2 border-white/30">
              <h3 className="font-bold mb-3 text-lg flex items-center gap-2">
                <span className="text-yellow-400">🚀</span> Your Development Pipeline:
              </h3>
              <ul className="space-y-3 text-sm">
                <li className="flex items-start gap-3 bg-white/10 p-3 rounded-lg">
                  <span className="text-yellow-400 font-bold text-lg min-w-[24px]">1.</span>
                  <div>
                    <strong>Complete Assessment</strong>
                    <p className="text-white/80 text-xs mt-1">Fill all physical, technical, tactical, and mental metrics</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 bg-white/10 p-3 rounded-lg">
                  <span className="text-yellow-400 font-bold text-lg min-w-[24px]">2.</span>
                  <div>
                    <strong>Saved as Baseline Benchmark</strong>
                    <p className="text-white/80 text-xs mt-1">Your starting point for tracking all future progress</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 bg-white/10 p-3 rounded-lg">
                  <span className="text-yellow-400 font-bold text-lg min-w-[24px]">3.</span>
                  <div>
                    <strong>AI Generates Training Programs</strong>
                    <p className="text-white/80 text-xs mt-1">Both Coach-Guided & AI-Powered programs tailored to your needs</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 bg-white/10 p-3 rounded-lg">
                  <span className="text-yellow-400 font-bold text-lg min-w-[24px]">4.</span>
                  <div>
                    <strong>View Professional Report</strong>
                    <p className="text-white/80 text-xs mt-1">Comprehensive roadmap opens automatically - print, save, and share!</p>
                  </div>
                </li>
                <li className="flex items-start gap-3 bg-green-500/30 p-3 rounded-lg border-2 border-green-400">
                  <span className="text-green-300 font-bold text-lg min-w-[24px]">5.</span>
                  <div>
                    <strong>🔓 All Features Unlocked!</strong>
                    <p className="text-white/90 text-xs mt-1">Access Home, Training, Progress, History, and all Player Portal features</p>
                  </div>
                </li>
              </ul>
              
              <div className="mt-4 bg-yellow-400/20 border-2 border-yellow-400 rounded-lg p-3">
                <p className="text-yellow-100 text-xs font-semibold text-center">
                  ⏱️ Assessment takes 10-15 minutes • All fields required for accurate analysis
                </p>
              </div>
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
              <span className="font-semibold text-gray-900">{formatMeasurement(user?.height, 'height')}</span>
            </div>
            <div className="text-gray-600">
              <span className="block text-gray-400">Weight</span>
              <span className="font-semibold text-gray-900">{formatMeasurement(user?.weight, 'weight')}</span>
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
              const isDisabled = (isFirstTime || checkingFirstTime) && item.id !== 'take-assessment';
              
              return (
                <button
                  key={item.id}
                  onClick={() => {
                    if (!isDisabled) {
                      console.log('📱 Navigation: Switching to tab:', item.id);
                      setActiveTab(item.id);
                    } else {
                      console.log('🔒 Navigation blocked: First assessment required');
                    }
                  }}
                  disabled={isDisabled}
                  className={`w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all ${
                    activeTab === item.id
                      ? 'bg-blue-600 text-white shadow-md'
                      : isDisabled
                      ? 'text-gray-400 cursor-not-allowed opacity-50'
                      : 'text-gray-700 hover:bg-gray-100'
                  }`}
                  title={isDisabled ? 'Complete your first assessment to unlock this feature' : ''}
                >
                  <Icon className="w-5 h-5 flex-shrink-0" />
                  <span className="truncate">{item.label}</span>
                  {isDisabled && <span className="ml-auto text-xs">🔒</span>}
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