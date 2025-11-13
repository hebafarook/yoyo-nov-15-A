import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import ParentOverview from './ParentOverview';
import { LogOut } from 'lucide-react';
import ParentTrainingPlan from './ParentTrainingPlan';
import ParentAssessments from './ParentAssessments';
import ParentPerformance from './ParentPerformance';
import ParentVideos from './ParentVideos';
import ParentHealth from './ParentHealth';
import ParentMessaging from './ParentMessaging';
import ParentEvents from './ParentEvents';
import ParentAchievements from './ParentAchievements';
import ParentBilling from './ParentBilling';
import ParentSettings from './ParentSettings';
import { 
  Home, Activity, FileText, TrendingUp, Video, Heart, 
  MessageSquare, Calendar, Award, CreditCard, Settings, 
  ChevronDown, User, Menu, X 
} from 'lucide-react';

const ParentDashboard = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('overview');
  const [selectedChild, setSelectedChild] = useState(null);
  const [children, setChildren] = useState([]);
  const [sidebarOpen, setSidebarOpen] = useState(true);

  useEffect(() => {
    // Load parent's children from API
    loadChildren();
  }, []);

  const loadChildren = async () => {
    // Mock data for now - will connect to API
    const mockChildren = [
      {
        id: '1',
        first_name: 'Alex',
        last_name: user?.full_name?.split(' ')[1] || 'Smith',
        age_group: 'U14',
        primary_position: 'Forward',
        profile_photo_url: null,
        current_ai_rating: 78
      }
    ];
    setChildren(mockChildren);
    if (mockChildren.length > 0) {
      setSelectedChild(mockChildren[0]);
    }
  };

  const navItems = [
    { id: 'overview', label: 'Overview', icon: Home },
    { id: 'training', label: 'Training Plan', icon: Activity },
    { id: 'assessments', label: 'Assessments', icon: FileText },
    { id: 'performance', label: 'Performance', icon: TrendingUp },
    { id: 'videos', label: 'Videos', icon: Video },
    { id: 'health', label: 'Health & Nutrition', icon: Heart },
    { id: 'messaging', label: 'Messaging', icon: MessageSquare },
    { id: 'events', label: 'Events', icon: Calendar },
    { id: 'achievements', label: 'Achievements', icon: Award },
    { id: 'billing', label: 'Billing', icon: CreditCard },
    { id: 'settings', label: 'Settings', icon: Settings }
  ];

  const renderContent = () => {
    if (!selectedChild) {
      return (
        <div className="flex items-center justify-center h-full">
          <p className="text-gray-500">No child selected</p>
        </div>
      );
    }

    switch (activeTab) {
      case 'overview': return <ParentOverview child={selectedChild} />;
      case 'training': return <ParentTrainingPlan child={selectedChild} />;
      case 'assessments': return <ParentAssessments child={selectedChild} />;
      case 'performance': return <ParentPerformance child={selectedChild} />;
      case 'videos': return <ParentVideos child={selectedChild} />;
      case 'health': return <ParentHealth child={selectedChild} />;
      case 'messaging': return <ParentMessaging child={selectedChild} />;
      case 'events': return <ParentEvents child={selectedChild} />;
      case 'achievements': return <ParentAchievements child={selectedChild} />;
      case 'billing': return <ParentBilling />;
      case 'settings': return <ParentSettings />;
      default: return <ParentOverview child={selectedChild} />;
    }
  };

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className={`${
        sidebarOpen ? 'w-64' : 'w-0'
      } bg-white border-r border-gray-200 transition-all duration-300 overflow-hidden`}>
        <div className="p-4">
          <h2 className="text-lg font-bold text-gray-800 mb-6">Parent Portal</h2>
          <nav className="space-y-1">
            {navItems.map((item) => {
              const Icon = item.icon;
              return (
                <button
                  key={item.id}
                  onClick={() => setActiveTab(item.id)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition ${
                    activeTab === item.id
                      ? 'bg-blue-50 text-blue-600'
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
        <div className="bg-white border-b border-gray-200 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </button>
              
              <div className="flex items-center gap-2">
                <h1 className="text-xl font-bold text-gray-800">YoYo Elite Soccer AI</h1>
                <span className="text-sm text-gray-500">– Parent Portal</span>
              </div>
            </div>

            <div className="flex items-center gap-4">
              {/* Child Selector */}
              {children.length > 0 && (
                <div className="relative">
                  <select
                    value={selectedChild?.id || ''}
                    onChange={(e) => {
                      const child = children.find(c => c.id === e.target.value);
                      setSelectedChild(child);
                    }}
                    className="appearance-none bg-gray-50 border border-gray-300 rounded-lg px-4 py-2 pr-8 text-sm font-medium text-gray-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    {children.map(child => (
                      <option key={child.id} value={child.id}>
                        {child.first_name} {child.last_name} ({child.age_group})
                      </option>
                    ))}
                  </select>
                  <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-500 pointer-events-none" />
                </div>
              )}

              {/* Parent Info */}
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center">
                  <User className="w-5 h-5 text-white" />
                </div>
                <span className="text-sm font-medium text-gray-700">
                  {user?.full_name || 'Parent'}
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Page Content */}
        <div className="flex-1 overflow-auto p-6">
          {renderContent()}
        </div>
      </div>
    </div>
  );
};

export default ParentDashboard;