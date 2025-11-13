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

const HomePage = ({ onNavigate, onOpenAuth }) => {
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

  if (!isAuthenticated) {
    return (
      <div className="max-w-7xl mx-auto p-6">
        <Card>
          <CardContent className="p-12 text-center">
            <div className="mb-8">
              <h2 className="text-3xl font-bold mb-4">Welcome to Yo-Yo Elite Soccer AI Coach</h2>
              <p className="text-gray-600 mb-6 text-lg">
                Professional Training & Assessment Platform for Players, Coaches, and Parents
              </p>
            </div>

            {/* Feature Highlights */}
            <div className="grid md:grid-cols-3 gap-6 mb-10">
              <div className="p-6 bg-blue-50 rounded-lg">
                <Trophy className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="font-bold text-lg mb-2">For Players</h3>
                <p className="text-gray-600 text-sm">Track performance and get personalized training programs</p>
              </div>
              <div className="p-6 bg-green-50 rounded-lg">
                <Users className="w-12 h-12 text-green-600 mx-auto mb-4" />
                <h3 className="font-bold text-lg mb-2">For Coaches</h3>
                <p className="text-gray-600 text-sm">Manage teams and analyze player performance</p>
              </div>
              <div className="p-6 bg-purple-50 rounded-lg">
                <Activity className="w-12 h-12 text-purple-600 mx-auto mb-4" />
                <h3 className="font-bold text-lg mb-2">For Parents</h3>
                <p className="text-gray-600 text-sm">Monitor your child's development and progress</p>
              </div>
            </div>

            <div className="flex gap-4 justify-center">
              <Button onClick={() => onNavigate('assessment')} size="lg" className="px-8">
                Get Started
                <ArrowRight className="w-5 h-5 ml-2" />
              </Button>
            </div>

            <p className="text-gray-500 text-sm mt-6">
              Click "Login" or "Register" above to choose your portal and get started
            </p>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Welcome Header - Role-based colors */}
      <div className={`bg-gradient-to-r ${
        user?.role === 'coach' ? 'from-green-600 to-green-700' :
        user?.role === 'parent' ? 'from-purple-600 to-purple-700' :
        'from-blue-600 to-blue-700'
      } text-white rounded-lg p-8`}>
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold mb-2">
              Welcome back, {user?.full_name || user?.username || 'User'}! 👋
            </h1>
            <p className="text-white text-opacity-90 text-lg">
              {user?.role === 'coach' ? '🎯 Professional Coaching Dashboard' : 
               user?.role === 'parent' ? '👨‍👩‍👧 Parent Monitoring Dashboard' : 
               '⚽ Player Development Dashboard'}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-white text-opacity-80">Today's Date</div>
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
