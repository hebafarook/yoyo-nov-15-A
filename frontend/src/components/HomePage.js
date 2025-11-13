import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { 
  TrendingUp, Target, Award, Calendar, Clock, 
  PlayCircle, FileText, BarChart3, Users, Trophy,
  Activity, Zap, Brain, ArrowRight, Plus, CheckCircle
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const HomePage = ({ onNavigate }) => {
  const { user, isAuthenticated } = useAuth();
  const [stats, setStats] = useState({
    totalReports: 0,
    totalBenchmarks: 0,
    recentAssessments: [],
    activePlayers: 0
  });
  const [loading, setLoading] = useState(false); // Changed to false - load in background
  const [hasAssessment, setHasAssessment] = useState(false);
  const [hasProgram, setHasProgram] = useState(false);

  useEffect(() => {
    if (isAuthenticated && user) {
      loadDashboardStats();
      checkUserProgress();
    }
  }, [isAuthenticated, user]);

  const checkUserProgress = async () => {
    if (!user) return;
    
    try {
      const token = localStorage.getItem('access_token');
      
      // Check for benchmarks (assessments)
      const benchmarksRes = await axios.get(`${API}/auth/benchmarks`, {
        headers: { 'Authorization': `Bearer ${token}` }
      });
      
      const benchmarks = benchmarksRes.data || [];
      const hasBenchmarks = benchmarks.length > 0;
      setHasAssessment(hasBenchmarks);
      
      // Check for training program using player_name from most recent benchmark
      if (hasBenchmarks && benchmarks[0]?.player_name) {
        const playerName = benchmarks[0].player_name;
        try {
          const programRes = await axios.get(`${API}/periodized-programs/${playerName}`);
          setHasProgram(!!programRes.data);
        } catch (err) {
          // 404 or error means no program exists
          setHasProgram(false);
        }
      } else {
        setHasProgram(false);
      }
    } catch (error) {
      console.error('Error checking user progress:', error);
      setHasAssessment(false);
      setHasProgram(false);
    }
  };

  const handleGetStarted = () => {
    // Smart routing based on user progress
    if (!hasAssessment) {
      // No assessment yet - go to assessment
      onNavigate('assessment');
    } else if (!hasProgram) {
      // Has assessment but no program - go to training to generate
      onNavigate('training');
    } else {
      // Has both - go to training to continue
      onNavigate('training');
    }
  };

  const loadDashboardStats = async () => {
    if (!user || !user.id) {
      return;
    }
    
    try {
      // Load user's saved reports and benchmarks
      const [reportsRes, benchmarksRes] = await Promise.allSettled([
        axios.get(`${API}/auth/saved-reports`),
        axios.get(`${API}/auth/benchmarks`)
      ]);
      
      const reports = reportsRes.status === 'fulfilled' ? reportsRes.value.data : [];
      const benchmarks = benchmarksRes.status === 'fulfilled' ? benchmarksRes.value.data : [];
      
      setStats({
        totalReports: reports?.length || 0,
        totalBenchmarks: benchmarks?.length || 0,
        recentAssessments: benchmarks?.slice(0, 5) || [],
        activePlayers: [...new Set((benchmarks || []).map(b => b.player_name))].length
      });
    } catch (error) {
      console.error('Error loading dashboard stats:', error);
      // Keep default empty stats
    }
  };

  const quickActions = [
    {
      title: hasAssessment ? 'New Assessment' : 'Start Assessment',
      description: hasAssessment ? 'Evaluate player performance' : 'Complete your first assessment',
      icon: <BarChart3 className="w-6 h-6" />,
      color: 'bg-blue-500',
      action: () => onNavigate('assessment')
    },
    {
      title: hasProgram ? 'Continue Training' : 'View Training',
      description: hasProgram ? 'Resume your training program' : 'Access training programs',
      icon: <PlayCircle className="w-6 h-6" />,
      color: 'bg-green-500',
      action: handleGetStarted
    },
    {
      title: 'My Reports',
      description: 'View saved assessments',
      icon: <FileText className="w-6 h-6" />,
      color: 'bg-purple-500',
      action: () => onNavigate('reports')
    },
    {
      title: 'Progress Tracker',
      description: 'Monitor improvements',
      icon: <TrendingUp className="w-6 h-6" />,
      color: 'bg-orange-500',
      action: () => onNavigate('progress')
    }
  ];

  // Portal Selection for Non-Authenticated Users
  const [selectedPortal, setSelectedPortal] = useState('player');
  
  const portals = [
    {
      id: 'player',
      name: 'Player Portal',
      icon: <Trophy className="w-8 h-8" />,
      color: 'blue',
      bgGradient: 'from-blue-500 to-blue-600',
      borderColor: 'border-blue-500',
      hoverBg: 'hover:bg-blue-50',
      description: 'Track your performance, training, and progress',
      features: ['Personal Assessments', 'Training Programs', 'Progress Tracking']
    },
    {
      id: 'coach',
      name: 'Coach Portal',
      icon: <Users className="w-8 h-8" />,
      color: 'green',
      bgGradient: 'from-green-500 to-green-600',
      borderColor: 'border-green-500',
      hoverBg: 'hover:bg-green-50',
      description: 'Manage players, assessments, and team analytics',
      features: ['Team Management', 'Player Assessments', 'Performance Analytics']
    },
    {
      id: 'parent',
      name: 'Parent Portal',
      icon: <Activity className="w-8 h-8" />,
      color: 'purple',
      bgGradient: 'from-purple-500 to-purple-600',
      borderColor: 'border-purple-500',
      hoverBg: 'hover:bg-purple-50',
      description: 'Monitor your child\'s development and communicate',
      features: ['View Child Progress', 'Coach Communication', 'Training Reports']
    }
  ];
  
  const currentPortal = portals.find(p => p.id === selectedPortal);

  if (!isAuthenticated) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            Yo-Yo Elite Soccer AI Coach
          </h1>
          <p className="text-lg text-gray-600">
            Professional Training & Assessment Platform
          </p>
        </div>

        {/* Portal Tabs */}
        <div className="flex justify-center mb-8">
          <div className="inline-flex bg-gray-100 rounded-lg p-1">
            {portals.map((portal) => (
              <button
                key={portal.id}
                onClick={() => setSelectedPortal(portal.id)}
                className={`
                  px-6 py-3 rounded-md font-semibold transition-all flex items-center gap-2
                  ${selectedPortal === portal.id 
                    ? `bg-white shadow-md text-${portal.color}-600` 
                    : 'text-gray-600 hover:text-gray-900'
                  }
                `}
              >
                {portal.icon}
                {portal.name}
              </button>
            ))}
          </div>
        </div>

        {/* Portal Content */}
        <Card className={`border-t-4 ${currentPortal.borderColor}`}>
          <CardContent className="p-12">
            <div className="grid md:grid-cols-2 gap-12 items-center">
              {/* Left Side - Portal Info */}
              <div>
                <div className={`inline-flex p-4 rounded-full bg-gradient-to-br ${currentPortal.bgGradient} text-white mb-6`}>
                  {currentPortal.icon}
                </div>
                <h2 className="text-3xl font-bold mb-4">{currentPortal.name}</h2>
                <p className="text-gray-600 text-lg mb-6">{currentPortal.description}</p>
                
                <div className="space-y-3 mb-8">
                  <p className="font-semibold text-gray-900">Key Features:</p>
                  {currentPortal.features.map((feature, index) => (
                    <div key={index} className="flex items-center gap-2">
                      <CheckCircle className={`w-5 h-5 text-${currentPortal.color}-500`} />
                      <span className="text-gray-700">{feature}</span>
                    </div>
                  ))}
                </div>

                <div className="flex gap-4">
                  <Button 
                    onClick={() => onNavigate('assessment')} 
                    size="lg"
                    className={`bg-gradient-to-r ${currentPortal.bgGradient} hover:opacity-90`}
                  >
                    Get Started
                    <ArrowRight className="w-5 h-5 ml-2" />
                  </Button>
                </div>
              </div>

              {/* Right Side - Visual Representation */}
              <div className="hidden md:block">
                <div className={`bg-gradient-to-br ${currentPortal.bgGradient} rounded-2xl p-8 text-white`}>
                  <h3 className="text-2xl font-bold mb-4">Welcome!</h3>
                  <p className="mb-6 opacity-90">
                    {selectedPortal === 'player' && 'Take control of your soccer development with AI-powered assessments and personalized training programs.'}
                    {selectedPortal === 'coach' && 'Elevate your coaching with comprehensive player analytics, team management tools, and data-driven insights.'}
                    {selectedPortal === 'parent' && 'Stay connected with your child\'s soccer journey. Track their progress and communicate with coaches effortlessly.'}
                  </p>
                  <div className="space-y-4">
                    <div className="bg-white bg-opacity-20 rounded-lg p-4">
                      <div className="flex items-center gap-3">
                        <Target className="w-6 h-6" />
                        <div>
                          <p className="font-semibold">Advanced Analytics</p>
                          <p className="text-sm opacity-90">AI-powered performance insights</p>
                        </div>
                      </div>
                    </div>
                    <div className="bg-white bg-opacity-20 rounded-lg p-4">
                      <div className="flex items-center gap-3">
                        <Brain className="w-6 h-6" />
                        <div>
                          <p className="font-semibold">Personalized Training</p>
                          <p className="text-sm opacity-90">Customized programs for every player</p>
                        </div>
                      </div>
                    </div>
                    <div className="bg-white bg-opacity-20 rounded-lg p-4">
                      <div className="flex items-center gap-3">
                        <Trophy className="w-6 h-6" />
                        <div>
                          <p className="font-semibold">Track Progress</p>
                          <p className="text-sm opacity-90">Monitor improvements over time</p>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Welcome Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg p-8">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              Welcome back, {user?.full_name || 'Coach'}! 👋
            </h1>
            <p className="text-blue-100 text-lg">
              {user?.is_coach ? 'Professional Coaching Dashboard' : 'Player Development Dashboard'}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-blue-100">Today's Date</div>
            <div className="text-2xl font-bold">{new Date().toLocaleDateString('en-US', { 
              month: 'short', 
              day: 'numeric', 
              year: 'numeric' 
            })}</div>
          </div>
        </div>
      </div>

      {/* Quick Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="border-l-4 border-l-blue-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Saved Reports</p>
                <p className="text-3xl font-bold text-blue-600">{stats.totalReports}</p>
              </div>
              <FileText className="w-12 h-12 text-blue-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-green-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Benchmarks</p>
                <p className="text-3xl font-bold text-green-600">{stats.totalBenchmarks}</p>
              </div>
              <Target className="w-12 h-12 text-green-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-purple-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">Active Players</p>
                <p className="text-3xl font-bold text-purple-600">{stats.activePlayers}</p>
              </div>
              <Users className="w-12 h-12 text-purple-500 opacity-20" />
            </div>
          </CardContent>
        </Card>

        <Card className="border-l-4 border-l-orange-500">
          <CardContent className="p-6">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-gray-600">This Week</p>
                <p className="text-3xl font-bold text-orange-600">0</p>
                <p className="text-xs text-gray-500">Training Sessions</p>
              </div>
              <Activity className="w-12 h-12 text-orange-500 opacity-20" />
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Quick Actions
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {quickActions.map((action, index) => (
              <button
                key={index}
                onClick={action.action}
                className="p-6 border-2 border-gray-200 rounded-lg hover:border-blue-500 hover:shadow-lg transition-all group"
              >
                <div className={`${action.color} w-12 h-12 rounded-lg flex items-center justify-center text-white mb-4 group-hover:scale-110 transition-transform`}>
                  {action.icon}
                </div>
                <h3 className="font-bold text-lg mb-1">{action.title}</h3>
                <p className="text-sm text-gray-600">{action.description}</p>
                <div className="flex items-center mt-3 text-blue-600 text-sm font-semibold">
                  Get Started <ArrowRight className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform" />
                </div>
              </button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Getting Started Guide */}
      <Card className="border-2 border-blue-200 bg-blue-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Trophy className="w-5 h-5 text-blue-600" />
            Getting Started Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-start gap-4 p-4 bg-white rounded-lg">
              <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                1
              </div>
              <div className="flex-1">
                <h4 className="font-semibold mb-1">Create Player Assessment</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Start by conducting a comprehensive assessment of your player's physical, technical, tactical, and psychological abilities.
                </p>
                <Button size="sm" onClick={() => onNavigate('assessment')}>
                  <Plus className="w-4 h-4 mr-1" />
                  New Assessment
                </Button>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 bg-white rounded-lg">
              <div className="w-8 h-8 bg-green-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                2
              </div>
              <div className="flex-1">
                <h4 className="font-semibold mb-1">Generate Training Program</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Based on assessment results, select your training frequency (3, 4, or 5 days/week) and generate a personalized program.
                </p>
              </div>
            </div>

            <div className="flex items-start gap-4 p-4 bg-white rounded-lg">
              <div className="w-8 h-8 bg-purple-600 text-white rounded-full flex items-center justify-center font-bold flex-shrink-0">
                3
              </div>
              <div className="flex-1">
                <h4 className="font-semibold mb-1">Track Progress</h4>
                <p className="text-sm text-gray-600 mb-2">
                  Save reports as benchmarks, monitor improvements over time, and adjust training programs based on performance data.
                </p>
                <Button size="sm" variant="outline" onClick={() => onNavigate('reports')}>
                  View Reports
                </Button>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Features Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <Card className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center mb-4">
              <Activity className="w-6 h-6 text-red-600" />
            </div>
            <h3 className="font-bold text-lg mb-2">Performance Assessment</h3>
            <p className="text-sm text-gray-600 mb-4">
              Comprehensive evaluation across physical, technical, tactical, and psychological categories with age-specific standards.
            </p>
            <ul className="space-y-1 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Youth Handbook Standards
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                VO2 Max Calculator
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Detailed Reports
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
              <Calendar className="w-6 h-6 text-blue-600" />
            </div>
            <h3 className="font-bold text-lg mb-2">Training Programs</h3>
            <p className="text-sm text-gray-600 mb-4">
              AI-powered periodized training programs with detailed exercise instructions and progress tracking.
            </p>
            <ul className="space-y-1 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                3 Training Phases
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Flexible Frequency
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Exercise Database
              </li>
            </ul>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardContent className="p-6">
            <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
              <TrendingUp className="w-6 h-6 text-green-600" />
            </div>
            <h3 className="font-bold text-lg mb-2">Progress Tracking</h3>
            <p className="text-sm text-gray-600 mb-4">
              Save benchmarks, track improvements, and monitor player development over time with visual analytics.
            </p>
            <ul className="space-y-1 text-sm text-gray-600">
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Baseline Benchmarks
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Progress Timeline
              </li>
              <li className="flex items-center gap-2">
                <CheckCircle className="w-4 h-4 text-green-500" />
                Improvement Stats
              </li>
            </ul>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default HomePage;
