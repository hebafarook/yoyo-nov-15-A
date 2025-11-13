import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import axios from 'axios';
import {
  Home, Users, Shield, Activity, TrendingUp, Calendar,
  AlertTriangle, Award, FileText, Settings, Brain, Heart,
  Target, BarChart3, BookOpen, UserCheck, Menu, X
} from 'lucide-react';

// Import all club sub-components
import ClubHome from './ClubHome';
import TeamsManagement from './TeamsManagement';
import PlayersDirectory from './PlayersDirectory';
import CoachesManagement from './CoachesManagement';
import AssessmentsOverview from './AssessmentsOverview';
import SafetyCenter from './SafetyCenter';
import AIInsightsHub from './AIInsightsHub';
import MatchScheduling from './MatchScheduling';
import MedicalCenter from './MedicalCenter';
import PerformanceAnalytics from './PerformanceAnalytics';
import AcademyCurriculum from './AcademyCurriculum';
import ClubSettings from './ClubSettings';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;

const ClubPortalDashboard = () => {
  const { user } = useAuth();
  const [activeSection, setActiveSection] = useState('home');
  const [clubData, setClubData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  const navSections = [
    { id: 'home', label: 'Club Dashboard', icon: Home, color: 'blue' },
    { id: 'teams', label: 'Teams Management', icon: Users, color: 'purple' },
    { id: 'players', label: 'Players Directory', icon: UserCheck, color: 'green' },
    { id: 'coaches', label: 'Coaches & Staff', icon: Award, color: 'orange' },
    { id: 'assessments', label: 'Assessments Overview', icon: FileText, color: 'cyan' },
    { id: 'safety', label: 'Safety & Load Center', icon: Shield, color: 'red' },
    { id: 'ai-insights', label: 'AI Insights & Alerts', icon: Brain, color: 'pink' },
    { id: 'matches', label: 'Match & Events', icon: Calendar, color: 'indigo' },
    { id: 'medical', label: 'Medical & Injuries', icon: Heart, color: 'rose' },
    { id: 'analytics', label: 'Performance Analytics', icon: TrendingUp, color: 'teal' },
    { id: 'curriculum', label: 'Academy Curriculum', icon: BookOpen, color: 'amber' },
    { id: 'settings', label: 'Club Settings', icon: Settings, color: 'gray' }
  ];

  useEffect(() => {
    if (user?.id) {
      fetchClubData();
    }
  }, [user]);

  const fetchClubData = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      const headers = { Authorization: `Bearer ${token}` };

      // Get user's club (for demo, use first club or create one)
      const clubsRes = await axios.get(`${BACKEND_URL}/api/club/clubs`, { headers });
      let club = clubsRes.data[0];

      if (!club) {
        // Create demo club
        const newClubRes = await axios.post(`${BACKEND_URL}/api/club/create-club`, {
          name: "YoYo Elite Soccer Academy",
          club_code: "YOYO-001",
          city: "Manchester",
          country: "UK",
          primary_contact_email: user.email || "admin@yoyoelite.com"
        }, { headers });
        club = newClubRes.data;
      }

      setClubData(club);
      setLoading(false);
    } catch (error) {
      console.error('Error fetching club data:', error);
      setLoading(false);
    }
  };

  const renderActiveSection = () => {
    if (!clubData) return null;

    const components = {
      'home': <ClubHome clubId={clubData.id} />,
      'teams': <TeamsManagement clubId={clubData.id} />,
      'players': <PlayersDirectory clubId={clubData.id} />,
      'coaches': <CoachesManagement clubId={clubData.id} />,
      'assessments': <AssessmentsOverview clubId={clubData.id} />,
      'safety': <SafetyCenter clubId={clubData.id} />,
      'ai-insights': <AIInsightsHub clubId={clubData.id} />,
      'matches': <MatchScheduling clubId={clubData.id} />,
      'medical': <MedicalCenter clubId={clubData.id} />,
      'analytics': <PerformanceAnalytics clubId={clubData.id} />,
      'curriculum': <AcademyCurriculum clubId={clubData.id} />,
      'settings': <ClubSettings clubId={clubData.id} clubData={clubData} onUpdate={fetchClubData} />
    };

    return components[activeSection] || components['home'];
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-4 border-green-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Club Portal...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-blue-900 to-purple-900">
      {/* Top Bar */}
      <div className="bg-gray-900/80 backdrop-blur-lg border-b border-green-400/30 sticky top-0 z-50">
        <div className="flex items-center justify-between px-6 py-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="lg:hidden text-white hover:text-green-400 transition"
            >
              {sidebarOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
            </button>
            <div>
              <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                <Shield className="w-8 h-8 text-green-400" />
                {clubData?.name || 'Club Portal'}
              </h1>
              <p className="text-sm text-gray-400">Elite Performance Management System</p>
            </div>
          </div>
          <div className="flex items-center gap-4">
            <div className="text-right">
              <p className="text-sm font-medium text-white">{user?.name || user?.email}</p>
              <p className="text-xs text-green-400">Club Administrator</p>
            </div>
            <div className="w-10 h-10 bg-gradient-to-br from-green-400 to-blue-500 rounded-full flex items-center justify-center">
              <span className="text-white font-bold">{(user?.name || 'U')[0].toUpperCase()}</span>
            </div>
          </div>
        </div>
      </div>

      <div className="flex">
        {/* Sidebar */}
        <aside className={`${sidebarOpen ? 'translate-x-0' : '-translate-x-full'} lg:translate-x-0 fixed lg:sticky top-[73px] left-0 h-[calc(100vh-73px)] w-64 bg-gray-900/95 backdrop-blur-lg border-r border-green-400/20 transition-transform duration-300 z-40 overflow-y-auto`}>
          <nav className="p-4 space-y-2">
            {navSections.map((section) => {
              const Icon = section.icon;
              const isActive = activeSection === section.id;
              
              return (
                <button
                  key={section.id}
                  onClick={() => {
                    setActiveSection(section.id);
                    if (window.innerWidth < 1024) setSidebarOpen(false);
                  }}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                    isActive
                      ? 'bg-gradient-to-r from-green-400/20 to-blue-500/20 border border-green-400/50 text-white shadow-lg'
                      : 'text-gray-400 hover:text-white hover:bg-white/5'
                  }`}
                >
                  <Icon className={`w-5 h-5 ${isActive ? 'text-green-400' : ''}`} />
                  <span className="font-medium text-sm">{section.label}</span>
                </button>
              );
            })}
          </nav>
        </aside>

        {/* Main Content */}
        <main className="flex-1 p-6 lg:p-8 overflow-y-auto">
          {renderActiveSection()}
        </main>
      </div>
    </div>
  );
};

export default ClubPortalDashboard;
