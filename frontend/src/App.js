import React, { useState, useEffect, createContext, useContext } from "react";
import "./App.css";
import { BrowserRouter, Routes, Route, Link } from "react-router-dom";
import axios from "axios";
import { Button } from "./components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./components/ui/card";
import { Input } from "./components/ui/input";
import { Label } from "./components/ui/label";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "./components/ui/tabs";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "./components/ui/select";
import { Badge } from "./components/ui/badge";
import { Progress } from "./components/ui/progress";
import { useSpeechSynthesis, useSpeechRecognition } from "react-speech-kit";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, RadarChart, PolarGrid, PolarAngleAxis, PolarRadiusAxis, Radar, BarChart, Bar } from "recharts";
import { Activity, Target, TrendingUp, Mic, MicOff, Volume2, VolumeX, Square, Trophy, Users, Music, Bell, Coins, Gift, Zap, Crown, Star, Flame, Languages, Globe, BarChart3, Award, ArrowRight, BookOpen, Lightbulb, Scale, Heart, Timer, Ruler, Info, HelpCircle, RefreshCw, Calendar, CheckCircle, Brain, Eye, Dumbbell, Gamepad2, Sparkles, Clock, Shield, Headphones, Camera, MessageSquare, Settings, FileText, LogIn, UserPlus, LogOut, Inbox } from "lucide-react";
import { YOUTH_HANDBOOK_STANDARDS, ASSESSMENT_EXPLANATIONS, evaluatePerformance, getAgeCategory, calculateOverallScore } from "./AssessmentStandards";
import ProgressTracker from "./components/ProgressTracker";
import ComingSoon from "./components/ComingSoon";
import VO2MaxCalculator from "./components/VO2MaxCalculator";
import TrainingDashboard from "./components/TrainingDashboard";
import PerformanceHighlights from "./components/PerformanceHighlights";
import PhysicalPerformanceMonitor from "./components/PhysicalPerformanceMonitor";
import AssessmentReport from "./components/AssessmentReport";
import PlayerReport from "./components/PlayerReport";
import AuthModal from "./components/AuthModal";
import ForgotPasswordModal from "./components/ForgotPasswordModal";
import SavedReports from "./components/SavedReports";
import HomePage from "./components/HomePage";
import AdminDashboard from "./components/AdminDashboard";
import AchievementsDisplay from "./components/AchievementsDisplay";
import AICoachDashboard from "./components/AICoachDashboard";
import InboxDashboard from "./components/InboxDashboard";
import ParentDashboard from "./components/parent/ParentDashboard";
import CoachDashboard from "./components/coach/CoachDashboard";
import PlayerDashboard from "./components/player/PlayerDashboard";
import ProfessionalAssessmentReport from "./components/player/ProfessionalAssessmentReport";
import ClubPortalDashboard from "./components/club/ClubPortalDashboard";
import SystemAdminPortal from "./components/admin/SystemAdminPortal";
import { AuthProvider, useAuth } from "./contexts/AuthContext";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Daily Progressive Training Structure
const DAILY_PROGRESSIVE_STRUCTURE = {
  week1: {
    theme: "Foundation Building",
    daily_focus: {
      monday: { focus: "Speed Development", intensity: "Medium", duration: 60 },
      tuesday: { focus: "Ball Control Training", intensity: "High", duration: 90 },
      wednesday: { focus: "Recovery & Flexibility", intensity: "Low", duration: 45 },
      thursday: { focus: "Tactical Awareness", intensity: "Medium", duration: 75 },
      friday: { focus: "Shooting Practice", intensity: "High", duration: 60 },
      saturday: { focus: "Match Simulation", intensity: "High", duration: 90 },
      sunday: { focus: "Active Recovery", intensity: "Low", duration: 30 }
    }
  },
  week2: {
    theme: "Skill Enhancement",
    daily_focus: {
      monday: { focus: "Speed Training", intensity: "High", duration: 60 },
      tuesday: { focus: "Advanced Technical Skills", intensity: "High", duration: 90 },
      wednesday: { focus: "Tactical Development", intensity: "Medium", duration: 75 },
      thursday: { focus: "Agility Training", intensity: "High", duration: 75 },
      friday: { focus: "Finishing Drills", intensity: "High", duration: 60 },
      saturday: { focus: "Competitive Match Play", intensity: "High", duration: 90 },
      sunday: { focus: "Mental Training", intensity: "Low", duration: 45 }
    }
  },
  week3: {
    theme: "Performance Optimization",
    daily_focus: {
      monday: { focus: "Explosive Speed", intensity: "Very High", duration: 60 },
      tuesday: { focus: "Elite Technical Work", intensity: "High", duration: 90 },
      wednesday: { focus: "Advanced Tactics", intensity: "Medium", duration: 75 },
      thursday: { focus: "Competition Agility", intensity: "High", duration: 75 },
      friday: { focus: "Clinical Finishing", intensity: "Very High", duration: 60 },
      saturday: { focus: "High-Level Match Play", intensity: "Very High", duration: 90 },
      sunday: { focus: "Recovery & Analysis", intensity: "Low", duration: 45 }
    }
  },
  week4: {
    theme: "Assessment & Planning",
    daily_focus: {
      monday: { focus: "Speed Assessment", intensity: "High", duration: 60 },
      tuesday: { focus: "Technical Evaluation", intensity: "High", duration: 90 },
      wednesday: { focus: "Tactical Assessment", intensity: "Medium", duration: 75 },
      thursday: { focus: "Agility Testing", intensity: "High", duration: 75 },
      friday: { focus: "Performance Review", intensity: "High", duration: 60 },
      saturday: { focus: "Final Assessment", intensity: "Medium", duration: 60 },
      sunday: { focus: "Program Planning", intensity: "Low", duration: 30 }
    }
  }
};

// Language Context
const LanguageContext = createContext();

const useLanguage = () => {
  const context = useContext(LanguageContext);
  if (!context) {
    throw new Error('useLanguage must be used within a LanguageProvider');
  }
  return context;
};

const LanguageProvider = ({ children }) => {
  const [language, setLanguage] = useState('en');
  const [direction, setDirection] = useState('ltr');

  const translations = {
    en: {
      'app.title': 'Yo-Yo Elite Soccer Player AI Coach',
      'app.subtitle': 'Professional Training & Assessment Platform',
      'app.description': 'Advanced AI-powered coaching system for developing elite soccer players through comprehensive assessment, personalized training programs, and performance tracking.',
      'nav.home': 'Home',
      'nav.assessment': 'Assessment',
      'nav.training': 'Training Programs',
      'nav.aicoach': 'AI Coach & Analysis',
      'nav.progress': 'Progress Tracking',
      'nav.voice': 'Voice Notes',
      'nav.trophies': 'Achievements',
      'nav.group': 'Team Management',
      'nav.highlights': 'Performance Analytics',
      'nav.body': 'Physical Metrics',
      'assessment.title': 'Professional Player Assessment',
      'assessment.subtitle': 'Comprehensive evaluation based on elite standards',
      'common.excellent': 'Excellent',
      'common.good': 'Good',
      'common.average': 'Average',
      'common.poor': 'Needs Improvement'
    },
    ar: {
      'app.title': 'مدرب الذكي يو-يو للاعبين كرة القدم النخبة',
      'app.subtitle': 'منصة التدريب والتقييم المهنية',
      'app.description': 'نظام تدريب متقدم مدعوم بالذكاء الاصطناعي لتطوير لاعبي كرة القدم النخبة من خلال التقييم الشامل وبرامج التدريب الشخصية وتتبع الأداء.',
      'nav.home': 'الرئيسية',
      'nav.assessment': 'التقييم',
      'nav.training': 'برامج التدريب',
      'nav.aicoach': 'مدرب الذكاء الاصطناعي',
      'nav.progress': 'تتبع التقدم',
      'nav.voice': 'الملاحظات الصوتية',
      'nav.trophies': 'الإنجازات',
      'nav.group': 'إدارة الفريق',
      'nav.highlights': 'تحليل الأداء',
      'nav.body': 'المقاييس البدنية',
      'assessment.title': 'تقييم اللاعب المحترف',
      'assessment.subtitle': 'تقييم شامل على أساس المعايير النخبة',
      'common.excellent': 'ممتاز',
      'common.good': 'جيد',
      'common.average': 'متوسط',
      'common.poor': 'يحتاج تحسين'
    }
  };

  const t = (key) => {
    return translations[language][key] || key;
  };

  const formatText = (template, params) => {
    let result = template;
    Object.keys(params).forEach(key => {
      result = result.replace(`{${key}}`, params[key]);
    });
    return result;
  };

  const toggleLanguage = () => {
    const newLang = language === 'en' ? 'ar' : 'en';
    setLanguage(newLang);
    setDirection(newLang === 'ar' ? 'rtl' : 'ltr');
    document.documentElement.lang = newLang;
    document.documentElement.dir = newLang === 'ar' ? 'rtl' : 'ltr';
  };

  return (
    <LanguageContext.Provider value={{ 
      language, 
      direction, 
      t, 
      formatText, 
      toggleLanguage 
    }}>
      {children}
    </LanguageContext.Provider>
  );
};

// Standards Legend Component
const StandardsLegend = () => {
  const { t, direction } = useLanguage();
  
  return (
    <div className="mb-8">
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-3">
            <Crown className="w-6 h-6" style={{color: 'var(--primary-black)'}} />
            <span style={{color: 'var(--text-black)'}}>Performance Standards Guide</span>
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 professional-card">
              <Crown className="w-8 h-8 mx-auto mb-3" style={{color: 'var(--navy-primary)'}} />
              <h4 className="font-semibold text-lg mb-1" style={{color: 'var(--navy-primary)'}}>{t('common.excellent')}</h4>
              <p className="text-sm" style={{color: 'var(--text-gray)'}}>Elite/International Level</p>
            </div>
            <div className="text-center p-4 professional-card">
              <Award className="w-8 h-8 mx-auto mb-3" style={{color: 'var(--navy-secondary)'}} />
              <h4 className="font-semibold text-lg mb-1" style={{color: 'var(--navy-primary)'}}>{t('common.good')}</h4>
              <p className="text-sm" style={{color: 'var(--text-gray)'}}>High Competitive Standard</p>
            </div>
            <div className="text-center p-4 professional-card">
              <Star className="w-8 h-8 mx-auto mb-3" style={{color: 'var(--text-light)'}} />
              <h4 className="font-semibold text-lg mb-1" style={{color: 'var(--navy-primary)'}}>{t('common.average')}</h4>
              <p className="text-sm" style={{color: 'var(--text-gray)'}}>Solid Club Level</p>
            </div>
            <div className="text-center p-4 professional-card">
              <Target className="w-8 h-8 mx-auto mb-3" style={{color: 'var(--text-muted)'}} />
              <h4 className="font-semibold text-lg mb-1" style={{color: 'var(--navy-primary)'}}>{t('common.poor')}</h4>
              <p className="text-sm" style={{color: 'var(--text-gray)'}}>Development Required</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

// Assessment Field Explanation Component
const FieldExplanation = ({ fieldName, isVisible, onToggle }) => {
  const { direction } = useLanguage();
  const explanation = ASSESSMENT_EXPLANATIONS[fieldName];
  
  if (!explanation) return null;

  return (
    <div className="mt-3">
      <button
        type="button"
        onClick={onToggle}
        className="btn-secondary text-sm py-2 px-3"
      >
        <HelpCircle className="w-4 h-4" />
        {isVisible ? 'Hide Details' : 'Show Details'}
      </button>
      
      {isVisible && (
        <div className="mt-3 p-4 professional-card border border-black">
          <h5 className="font-semibold text-lg mb-2 text-black">{explanation.title}</h5>
          <p className="text-sm mb-3" dir={direction}>{explanation.description}</p>
          <div className="space-y-2 text-sm">
            <p><strong className="text-black">Importance:</strong> {explanation.importance}</p>
            <p><strong className="text-black">Tips:</strong> {explanation.tips}</p>
            <p><strong className="text-black">Scoring:</strong> {explanation.scoring}</p>
          </div>
        </div>
      )}
    </div>
  );
};

// Enhanced Assessment Component
const AssessmentForm = ({ onAssessmentCreated, setActiveTab }) => {
  const { t, direction } = useLanguage();
  const { user, isAuthenticated } = useAuth();
  const [formData, setFormData] = useState({
    player_name: "",
    age: "",
    position: "",
    height_cm: "",
    weight_kg: "",
    assessment_date: new Date().toISOString().split('T')[0],
    // Physical metrics
    sprint_30m: "",
    yo_yo_test: "",
    vo2_max: "",
    vertical_jump: "",
    body_fat: "",
    // Technical metrics
    ball_control: "",
    passing_accuracy: "",
    dribbling_success: "",
    shooting_accuracy: "",
    defensive_duels: "",
    // Tactical metrics
    game_intelligence: "",
    positioning: "",
    decision_making: "",
    // Psychological metrics
    coachability: "",
    mental_toughness: ""
  });

  const [isLoading, setIsLoading] = useState(false);
  const [explanationVisibility, setExplanationVisibility] = useState({});
  const [assessmentSuccess, setAssessmentSuccess] = useState(false);
  const [assessmentMessage, setAssessmentMessage] = useState('');

  // Auto-populate player data from user profile
  useEffect(() => {
    if (isAuthenticated && user) {
      setFormData(prev => ({
        ...prev,
        player_name: user.role === 'player' ? user.username : prev.player_name,
        age: user.age || prev.age,
        position: user.position || prev.position,
      }));
    }
  }, [isAuthenticated, user]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      if (!isAuthenticated || !user) {
        alert("Please login to save your assessment data.");
        setIsLoading(false);
        return;
      }

      // Add user_id if authenticated
      const assessmentData = {
        ...formData,
        user_id: user.id
      };
      
      console.log('Creating assessment with data:', assessmentData);
      const response = await axios.post(`${API}/assessments`, assessmentData);
      console.log('Assessment created successfully:', response.data);
      
      const createdAssessment = response.data;
      
      // Calculate overall score for the assessment
      const ageCategory = getAgeCategory(parseInt(formData.age));
      const overallScore = calculateOverallScore(formData, ageCategory);
      const performanceLevel = getPerformanceLevel(overallScore);
      
      // Automatically save as benchmark
      try {
        const benchmarkData = {
          user_id: user.id,
          player_name: formData.player_name,
          assessment_id: createdAssessment.id,
          age: parseInt(formData.age),
          position: formData.position,
          // Physical metrics
          sprint_30m: parseFloat(formData.sprint_30m),
          yo_yo_test: parseInt(formData.yo_yo_test),
          vo2_max: parseFloat(formData.vo2_max),
          vertical_jump: parseInt(formData.vertical_jump),
          body_fat: parseFloat(formData.body_fat),
          // Technical metrics
          ball_control: parseInt(formData.ball_control),
          passing_accuracy: parseFloat(formData.passing_accuracy),
          dribbling_success: parseFloat(formData.dribbling_success),
          shooting_accuracy: parseFloat(formData.shooting_accuracy),
          defensive_duels: parseFloat(formData.defensive_duels),
          // Tactical metrics
          game_intelligence: parseInt(formData.game_intelligence),
          positioning: parseInt(formData.positioning),
          decision_making: parseInt(formData.decision_making),
          // Psychological metrics
          coachability: parseInt(formData.coachability),
          mental_toughness: parseInt(formData.mental_toughness),
          // Calculated metrics
          overall_score: overallScore,
          performance_level: performanceLevel,
          benchmark_type: 'regular',
          notes: `Assessment created on ${new Date().toLocaleDateString()}`
        };
        
        console.log('Saving as benchmark:', benchmarkData);
        const token = localStorage.getItem('token');
        const benchmarkResponse = await axios.post(`${API}/auth/save-benchmark`, benchmarkData, {
          headers: { 'Authorization': `Bearer ${token}` }
        });
        console.log('Benchmark saved:', benchmarkResponse.data);
        
        // Auto-generate intelligent report using LLM engine
        try {
          console.log('Triggering AI report generation for assessment:', createdAssessment.id);
          const reportGenResponse = await axios.post(`${API}/reports/generate-report`, {
            assessment_id: createdAssessment.id,
            include_comparison: true,
            include_training_plan: true
          }, {
            headers: { 'Authorization': `Bearer ${token}` }
          });
          
          console.log('AI-powered report generated successfully:', reportGenResponse.data);
          
        } catch (reportError) {
          console.error('Error generating AI report (non-critical):', reportError);
        }
        
        if (benchmarkResponse.data.is_baseline) {
          setAssessmentMessage('🎯 BASELINE ASSESSMENT SAVED!\n\nThis is your baseline benchmark - all future progress will be compared to this assessment. Your data is securely saved and ready for training program generation.\n\n✅ Report automatically saved to My Reports');
        } else {
          setAssessmentMessage('📊 ASSESSMENT SAVED AS BENCHMARK!\n\nSaved for progress tracking. Your data is securely saved and you can view your progress in the Reports tab.\n\n✅ Report automatically saved to My Reports');
        }
        setAssessmentSuccess(true);
      } catch (benchmarkError) {
        console.error('Error saving benchmark:', benchmarkError);
        // Still notify success even if benchmark fails
        setAssessmentMessage('✅ ASSESSMENT SAVED!\n\nNote: Benchmark save had an issue, but your assessment data is safe.');
        setAssessmentSuccess(true);
      }
      
      // Notify parent component
      onAssessmentCreated(createdAssessment);
      
      // Scroll to top to show success message
      window.scrollTo({ top: 0, behavior: 'smooth' });
      
    } catch (error) {
      console.error("Error creating assessment:", error);
      
      // Show detailed error message
      let errorMessage = "Failed to save assessment. Please try again.";
      if (error.response) {
        if (error.response.status === 401) {
          errorMessage = "Session expired. Please login again.";
        } else if (error.response.data && error.response.data.detail) {
          errorMessage = `Error: ${error.response.data.detail}`;
        }
      }
      
      setAssessmentMessage(`❌ ERROR\n\n${errorMessage}`);
      setAssessmentSuccess(false);
      alert(errorMessage);
    } finally {
      setIsLoading(false);
    }
  };

  // Helper function to calculate overall score
  const calculateOverallScore = (data, ageCategory) => {
    // This is a simplified calculation - you can adjust weights
    const scores = [];
    
    // Physical (20%)
    const physicalMetrics = ['sprint_30m', 'yo_yo_test', 'vo2_max', 'vertical_jump', 'body_fat'];
    physicalMetrics.forEach(metric => {
      if (data[metric]) {
        const perf = evaluatePerformance(parseFloat(data[metric]), metric, ageCategory);
        scores.push(getPerformanceScore(perf) * 4); // Scale to 20
      }
    });
    
    // Technical (40%)
    const technicalMetrics = ['ball_control', 'passing_accuracy', 'dribbling_success', 'shooting_accuracy', 'defensive_duels'];
    technicalMetrics.forEach(metric => {
      if (data[metric]) {
        scores.push(parseFloat(data[metric]) / 100 * 40); // Scale to 40
      }
    });
    
    // Tactical (30%)
    const tacticalMetrics = ['game_intelligence', 'positioning', 'decision_making'];
    tacticalMetrics.forEach(metric => {
      if (data[metric]) {
        scores.push(parseInt(data[metric]) * 6); // Scale to 30
      }
    });
    
    // Psychological (10%)
    const psychMetrics = ['coachability', 'mental_toughness'];
    psychMetrics.forEach(metric => {
      if (data[metric]) {
        scores.push(parseInt(data[metric]) * 2); // Scale to 10
      }
    });
    
    return scores.length > 0 ? scores.reduce((a, b) => a + b, 0) / scores.length : 50;
  };

  const getPerformanceScore = (performance) => {
    const scores = { excellent: 5, good: 4, average: 3, 'below average': 2, poor: 1 };
    return scores[performance] || 3;
  };

  const getPerformanceLevel = (score) => {
    if (score >= 80) return 'Elite';
    if (score >= 70) return 'Advanced';
    if (score >= 60) return 'Intermediate';
    if (score >= 40) return 'Developing';
    return 'Beginner';
  };

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.name]: e.target.value });
  };

  const toggleExplanation = (fieldName) => {
    setExplanationVisibility(prev => ({
      ...prev,
      [fieldName]: !prev[fieldName]
    }));
  };

  const getFieldValidation = (fieldName, value, age) => {
    if (!value || !age) return 'input-field';
    
    const numValue = parseFloat(value);
    const ageCategory = getAgeCategory(parseInt(age));
    const performance = evaluatePerformance(numValue, fieldName, ageCategory);
    
    if (!performance) return 'input-field';
    
    const validationClasses = {
      excellent: 'input-field border-[--secondary-gold] bg-[--light-bg]',
      good: 'input-field border-[--success] bg-[--light-bg]',
      average: 'input-field border-[--text-muted] bg-[--light-bg]',
      poor: 'input-field border-[--error] bg-[--light-bg]'
    };
    
    return validationClasses[performance];
  };

  // VO2 Max Calculator handlers
  const handleVO2MaxCalculation = (calculatedValue) => {
    setFormData(prev => ({
      ...prev,
      vo2_max: calculatedValue.toString()
    }));
  };

  const handleSaveBenchmark = async (benchmark) => {
    try {
      const benchmarkData = {
        player_id: formData.player_name || "unknown", // Use player name as ID for now
        vo2_max: benchmark.vo2Max,
        calculation_inputs: benchmark.inputs,
        calculation_method: "ACSM",
        notes: benchmark.notes,
        fitness_level: benchmark.fitness_level
      };

      const response = await axios.post(`${API}/vo2-benchmarks`, benchmarkData);
      console.log('Benchmark saved:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error saving benchmark:', error);
      throw error;
    }
  };

  const createPeriodizedProgram = async (playerId) => {
    try {
      const programData = {
        player_id: playerId,
        program_name: `Elite Development Program - ${playerId}`,
        total_duration_weeks: 14, // Foundation (4) + Development (6) + Peak (4)
        program_objectives: [
          "Develop technical skills under pressure",
          "Improve physical conditioning and speed",
          "Enhance tactical awareness and decision making",
          "Build mental toughness and confidence",
          "Achieve optimal match performance"
        ],
        assessment_interval_weeks: 4
      };

      const response = await axios.post(`${API}/periodized-programs`, programData);
      console.log('Periodized program created:', response.data);
      return response.data;
    } catch (error) {
      console.error('Error creating periodized program:', error);
      // Don't throw error - program creation is optional
      return null;
    }
  };

  return (
    <div className="max-w-5xl mx-auto">
      <StandardsLegend />
      
      <Card className="professional-card">
        <CardHeader className="text-center">
          <CardTitle className="text-3xl font-bold mb-3">
            {t('assessment.title')}
          </CardTitle>
          <CardDescription className="text-lg" style={{color: 'var(--text-gray-dark)'}}>
            {t('assessment.subtitle')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          {/* Success Message */}
          {assessmentSuccess && (
            <div className="mb-6 p-6 bg-green-50 border-2 border-green-500 rounded-lg">
              <div className="flex items-start gap-3">
                <div className="text-green-600 text-3xl">✅</div>
                <div className="flex-1">
                  <h4 className="text-xl font-bold text-green-800 mb-2">Success!</h4>
                  <p className="text-green-700 whitespace-pre-line">{assessmentMessage}</p>
                  <div className="mt-4 flex gap-3">
                    <button
                      onClick={() => {
                        setAssessmentSuccess(false);
                        setActiveTab('training');
                      }}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                    >
                      Generate Training Program →
                    </button>
                    <button
                      onClick={() => {
                        setAssessmentSuccess(false);
                        setActiveTab('reports');
                      }}
                      className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                    >
                      View My Reports
                    </button>
                    <button
                      onClick={() => setAssessmentSuccess(false)}
                      className="px-4 py-2 bg-gray-200 text-gray-700 rounded-lg hover:bg-gray-300 transition-colors"
                    >
                      Create Another Assessment
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}
          
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Information */}
            <div className="space-y-6">
              <h3 className="text-xl font-semibold text-gray-900">Player Information</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="player_name" className="text-base font-medium mb-2 block" style={{color: 'var(--text-black)'}}>
                    Player Name {user?.role === 'player' && <span className="text-xs text-gray-500">(Auto-filled)</span>}
                  </Label>
                  <input
                    id="player_name"
                    name="player_name"
                    value={formData.player_name}
                    onChange={handleChange}
                    required
                    readOnly={user?.role === 'player'}
                    className={`input-field ${user?.role === 'player' ? 'bg-gray-100' : ''}`}
                    placeholder="Enter player name"
                  />
                </div>
                <div>
                  <Label htmlFor="age" className="text-base font-medium mb-2 block" style={{color: 'var(--text-black)'}}>
                    Age {user?.age && <span className="text-xs text-gray-500">(Auto-filled)</span>}
                  </Label>
                  <input
                    id="age"
                    name="age"
                    type="number"
                    min="12"
                    max="25"
                    value={formData.age}
                    onChange={handleChange}
                    required
                    className="input-field"
                    placeholder="Player age"
                  />
                  {formData.age && (
                    <span className="badge-good mt-2 inline-block">
                      Age Group: {getAgeCategory(parseInt(formData.age))}
                    </span>
                  )}
                </div>
                <div>
                  <Label htmlFor="position" className="text-base font-medium mb-2 block" style={{color: 'var(--text-black)'}}>
                    Position {user?.position && <span className="text-xs text-gray-500">(Auto-filled)</span>}
                  </Label>
                  <Select 
                    value={formData.position}
                    onValueChange={(value) => setFormData({...formData, position: value})}
                  >
                    <SelectTrigger className="input-field">
                      <SelectValue placeholder="Select position" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="goalkeeper">Goalkeeper</SelectItem>
                      <SelectItem value="defender">Defender</SelectItem>
                      <SelectItem value="midfielder">Midfielder</SelectItem>
                      <SelectItem value="forward">Forward</SelectItem>
                      <SelectItem value="striker">Striker</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="height_cm" className="text-base font-medium mb-2 block" style={{color: 'var(--text-black)'}}>
                    Height (cm) *
                  </Label>
                  <input
                    id="height_cm"
                    name="height_cm"
                    type="number"
                    min="140"
                    max="220"
                    value={formData.height_cm}
                    onChange={handleChange}
                    required
                    className="input-field"
                    placeholder="e.g., 175"
                  />
                </div>
                <div>
                  <Label htmlFor="weight_kg" className="text-base font-medium mb-2 block" style={{color: 'var(--text-black)'}}>
                    Weight (kg) *
                  </Label>
                  <input
                    id="weight_kg"
                    name="weight_kg"
                    type="number"
                    min="40"
                    max="120"
                    step="0.1"
                    value={formData.weight_kg}
                    onChange={handleChange}
                    required
                    className="input-field"
                    placeholder="e.g., 70"
                  />
                  {formData.height_cm && formData.weight_kg && (
                    <span className="text-xs text-gray-600 mt-1 block">
                      BMI: {(formData.weight_kg / ((formData.height_cm / 100) ** 2)).toFixed(1)}
                    </span>
                  )}
                </div>
                <div>
                  <Label htmlFor="assessment_date" className="text-base font-medium mb-2 block" style={{color: 'var(--text-black)'}}>
                    Assessment Date
                  </Label>
                  <input
                    id="assessment_date"
                    name="assessment_date"
                    type="date"
                    value={formData.assessment_date}
                    onChange={handleChange}
                    required
                    className="input-field"
                  />
                </div>
              </div>
            </div>

            {/* Physical Performance - 20% Weight */}
            <div className="assessment-section">
              <h3>
                <Dumbbell className="w-6 h-6" />
                Physical Performance Tests
                <span className="weight-badge">20% Weight</span>
              </h3>
              
              {/* Non-VO2 Max Fields */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-6">
                {['sprint_30m', 'yo_yo_test', 'vertical_jump', 'body_fat'].map((field) => (
                  <div key={field}>
                    <Label className="text-base font-medium mb-2 block">
                      {field === 'sprint_30m' && '30m Sprint (seconds)'}
                      {field === 'yo_yo_test' && 'Yo-Yo Test (meters)'}
                      {field === 'vertical_jump' && 'Vertical Jump (cm)'}
                      {field === 'body_fat' && 'Body Fat (%)'}
                    </Label>
                    <input
                      name={field}
                      type="number"
                      step={field === 'sprint_30m' || field === 'body_fat' ? '0.1' : '1'}
                      value={formData[field]}
                      onChange={handleChange}
                      required
                      className={getFieldValidation(field, formData[field], formData.age)}
                      placeholder={
                        field === 'sprint_30m' ? 'e.g., 4.2' :
                        field === 'yo_yo_test' ? 'e.g., 1600' :
                        field === 'vertical_jump' ? 'e.g., 55' :
                        'e.g., 12.5'
                      }
                    />
                    <FieldExplanation 
                      fieldName={field} 
                      isVisible={explanationVisibility[field]}
                      onToggle={() => toggleExplanation(field)}
                    />
                  </div>
                ))}
              </div>

              {/* VO2 Max Special Section with Calculator */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {/* Manual VO2 Max Input */}
                <div>
                  <Label className="text-base font-medium mb-2 block">
                    VO2 Max (ml/kg/min)
                  </Label>
                  <input
                    name="vo2_max"
                    type="number"
                    step="0.1"
                    value={formData.vo2_max}
                    onChange={handleChange}
                    required
                    className={getFieldValidation('vo2_max', formData.vo2_max, formData.age)}
                    placeholder="e.g., 58.5"
                  />
                  <FieldExplanation 
                    fieldName="vo2_max" 
                    isVisible={explanationVisibility.vo2_max}
                    onToggle={() => toggleExplanation('vo2_max')}
                  />
                </div>

                {/* VO2 Max Calculator */}
                <div>
                  <VO2MaxCalculator
                    onCalculate={handleVO2MaxCalculation}
                    currentAge={formData.age}
                    currentGender="male" // You can make this dynamic based on form data
                    onSaveBenchmark={handleSaveBenchmark}
                  />
                </div>
              </div>
            </div>

            {/* Technical Skills - 40% Weight */}
            <div className="assessment-section">
              <h3>
                <Gamepad2 className="w-6 h-6" />
                Technical Skills Assessment
                <span className="weight-badge">40% Weight</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {['ball_control', 'passing_accuracy', 'dribbling_success', 'shooting_accuracy', 'defensive_duels'].map((field) => (
                  <div key={field}>
                    <Label className="text-base font-medium mb-2 block">
                      {field === 'ball_control' && 'Ball Control (1-5 scale)'}
                      {field === 'passing_accuracy' && 'Passing Accuracy (%)'}
                      {field === 'dribbling_success' && 'Dribbling Success (%)'}
                      {field === 'shooting_accuracy' && 'Shooting Accuracy (%)'}
                      {field === 'defensive_duels' && 'Defensive Duels (%)'}
                    </Label>
                    <input
                      name={field}
                      type="number"
                      step={field === 'ball_control' ? '1' : '0.1'}
                      min={field === 'ball_control' ? '1' : '0'}
                      max={field === 'ball_control' ? '5' : '100'}
                      value={formData[field]}
                      onChange={handleChange}
                      required
                      className={getFieldValidation(field, formData[field], formData.age)}
                      placeholder={
                        field === 'ball_control' ? '1-5 scale' : 'Percentage (0-100)'
                      }
                    />
                    <FieldExplanation 
                      fieldName={field} 
                      isVisible={explanationVisibility[field]}
                      onToggle={() => toggleExplanation(field)}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Tactical Awareness - 30% Weight */}
            <div className="assessment-section">
              <h3>
                <Brain className="w-6 h-6" />
                Tactical Awareness Assessment
                <span className="weight-badge">30% Weight</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {['game_intelligence', 'positioning', 'decision_making'].map((field) => (
                  <div key={field}>
                    <Label className="text-base font-medium mb-2 block">
                      {field === 'game_intelligence' && 'Game Intelligence (1-5)'}
                      {field === 'positioning' && 'Positioning (1-5)'}
                      {field === 'decision_making' && 'Decision Making (1-5)'}
                    </Label>
                    <input
                      name={field}
                      type="number"
                      min="1"
                      max="5"
                      value={formData[field]}
                      onChange={handleChange}
                      required
                      className={getFieldValidation(field, formData[field], formData.age)}
                      placeholder="1-5 scale"
                    />
                    <FieldExplanation 
                      fieldName={field} 
                      isVisible={explanationVisibility[field]}
                      onToggle={() => toggleExplanation(field)}
                    />
                  </div>
                ))}
              </div>
            </div>

            {/* Psychological Traits - 10% Weight */}
            <div className="assessment-section">
              <h3>
                <Heart className="w-6 h-6" />
                Psychological Traits Assessment
                <span className="weight-badge">10% Weight</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {['coachability', 'mental_toughness'].map((field) => (
                  <div key={field}>
                    <Label className="text-base font-medium mb-2 block">
                      {field === 'coachability' && 'Coachability (1-5)'}
                      {field === 'mental_toughness' && 'Mental Toughness (1-5)'}
                    </Label>
                    <input
                      name={field}
                      type="number"
                      min="1"
                      max="5"
                      value={formData[field]}
                      onChange={handleChange}
                      required
                      className={getFieldValidation(field, formData[field], formData.age)}
                      placeholder="1-5 scale"
                    />
                    <FieldExplanation 
                      fieldName={field} 
                      isVisible={explanationVisibility[field]}
                      onToggle={() => toggleExplanation(field)}
                    />
                  </div>
                ))}
              </div>
            </div>

            <button 
              type="submit" 
              disabled={isLoading}
              className={`btn-primary w-full py-4 text-lg font-semibold ${isLoading ? 'loading' : ''}`}
            >
              {isLoading ? 'Creating Assessment...' : 'Create Professional Assessment'}
            </button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

// Daily Progressive Program Component
const DailyProgressiveProgram = ({ weekNumber, playerData }) => {
  const { direction } = useLanguage();
  const weekStructure = DAILY_PROGRESSIVE_STRUCTURE[`week${weekNumber}`];
  
  if (!weekStructure) return null;
  
  return (
    <Card className="professional-card mb-6">
      <CardHeader>
        <CardTitle className="flex items-center gap-3">
          <Calendar className="w-5 h-5 text-[--primary-blue]" />
          Week {weekNumber}: {weekStructure.theme}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(weekStructure.daily_focus).map(([day, details]) => (
            <div key={day} className="professional-card p-4">
              <h4 className="font-semibold text-lg capitalize mb-2 text-[--primary-blue]">{day}</h4>
              <div className="space-y-2">
                <p className="text-sm font-medium">{details.focus}</p>
                <div className="flex justify-between items-center">
                  <span className={`badge-${
                    details.intensity === 'Very High' ? 'excellent' :
                    details.intensity === 'High' ? 'good' :
                    details.intensity === 'Medium' ? 'average' :
                    'poor'
                  }`}>
                    {details.intensity}
                  </span>
                  <span className="text-sm text-[--text-muted] flex items-center gap-1">
                    <Timer className="w-4 h-4" />
                    {details.duration}min
                  </span>
                </div>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
};

// Enhanced Training Program Component
const TrainingProgram = ({ playerId, playerName, playerData }) => {
  const { direction } = useLanguage();
  const [programs, setPrograms] = useState([]);
  const [isGenerating, setIsGenerating] = useState(false);
  const [showDailyProgression, setShowDailyProgression] = useState(false);
  const [selectedWeek, setSelectedWeek] = useState(1);

  useEffect(() => {
    fetchPrograms();
  }, [playerId]);

  const fetchPrograms = async () => {
    try {
      const response = await axios.get(`${API}/training-programs/${playerId}`);
      setPrograms(response.data);
    } catch (error) {
      console.error("Error fetching programs:", error);
    }
  };

  const generateProgram = async (programType) => {
    setIsGenerating(true);
    try {
      const response = await axios.post(`${API}/training-programs`, {
        player_id: playerId,
        program_type: programType
      });
      setPrograms([response.data, ...programs]);
    } catch (error) {
      console.error("Error generating program:", error);
    }
    setIsGenerating(false);
  };

  const scheduleRetest = async () => {
    try {
      await axios.post(`${API}/notifications`, {
        player_id: playerId,
        title: "Assessment Retest Scheduled",
        message: "Your training cycle is complete. Time for reassessment to track improvements!",
        notification_type: "retest",
        scheduled_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      });
      
      alert("Retest scheduled for next week!");
    } catch (error) {
      console.error("Error scheduling retest:", error);
    }
  };

  return (
    <div className="space-y-6">
      {/* Progress Tracker */}
      {playerData && (
        <ProgressTracker playerData={playerData} />
      )}

      {/* Daily Progressive Training Display */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Calendar className="w-5 h-5 text-[--primary-blue]" />
              Daily Progression Plan
            </div>
            <button
              onClick={() => setShowDailyProgression(!showDailyProgression)}
              className="btn-secondary"
            >
              {showDailyProgression ? 'Hide' : 'Show'} Daily Plan
            </button>
          </CardTitle>
        </CardHeader>
        {showDailyProgression && (
          <CardContent>
            <div className="mb-4">
              <Label className="text-base font-medium mb-2 block">Select Week:</Label>
              <Select value={selectedWeek.toString()} onValueChange={(value) => setSelectedWeek(parseInt(value))}>
                <SelectTrigger className="input-field w-64">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Week 1: Foundation Building</SelectItem>
                  <SelectItem value="2">Week 2: Skill Enhancement</SelectItem>
                  <SelectItem value="3">Week 3: Performance Optimization</SelectItem>
                  <SelectItem value="4">Week 4: Assessment & Planning</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DailyProgressiveProgram weekNumber={selectedWeek} playerData={playerData} />
          </CardContent>
        )}
      </Card>

      {/* Training Program Generation */}
      <div className="flex flex-wrap gap-4 mb-6">
        <button 
          onClick={() => generateProgram("AI_Generated")} 
          disabled={isGenerating}
          className={`btn-primary ${isGenerating ? 'loading' : ''}`}
        >
          <Zap className="w-4 h-4" />
          Generate AI Program
        </button>
        <button 
          onClick={() => generateProgram("Ronaldo_Template")} 
          disabled={isGenerating}
          className={`btn-secondary ${isGenerating ? 'loading' : ''}`}
        >
          <Crown className="w-4 h-4" />
          Elite Template
        </button>
        <button 
          onClick={scheduleRetest}
          className="btn-secondary"
        >
          <RefreshCw className="w-4 h-4" />
          Schedule Retest
        </button>
      </div>

      {/* Generated Programs */}
      {programs.map(program => (
        <Card key={program.id} className="professional-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-3">
              <Trophy className="w-5 h-5 text-[--secondary-gold]" />
              {program.program_type} - {playerName}
            </CardTitle>
            <CardDescription className="text-[--text-muted]">
              Created: {new Date(program.created_at).toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose max-w-none text-[--text-secondary]" dir={direction}>
              <div className="whitespace-pre-wrap">
                {program.program_content}
              </div>
            </div>
            
            {/* Weekly Schedule */}
            {program.weekly_schedule && Object.keys(program.weekly_schedule).length > 0 && (
              <div className="mt-6">
                <h4 className="text-lg font-semibold text-[--primary-blue] mb-3">Weekly Structure</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Object.entries(program.weekly_schedule).map(([day, activity]) => (
                    <div key={day} className="professional-card p-3">
                      <div className="font-medium text-[--primary-blue] capitalize">{day}</div>
                      <div className="text-sm text-[--text-secondary]" dir={direction}>{activity}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Milestones */}
            {program.milestones && program.milestones.length > 0 && (
              <div className="mt-6">
                <h4 className="text-lg font-semibold text-[--secondary-gold] mb-3">Milestones & Rewards</h4>
                <div className="space-y-2">
                  {program.milestones.map((milestone, index) => (
                    <div key={index} className="professional-card p-3 flex items-center justify-between">
                      <div>
                        <span className="font-medium text-[--primary-blue]">Week {milestone.week}:</span>
                        <span className="text-[--text-secondary] ml-2" dir={direction}>{milestone.target}</span>
                      </div>
                      <span className="badge-excellent flex items-center gap-1">
                        <Coins className="w-4 h-4" />
                        {milestone.coins}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      ))}
    </div>
  );
};

// Main App
const MainApp = () => {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <div className="min-h-screen">
          <Routes>
            <Route path="/" element={<MainDashboard />} />
            <Route path="/professional-report" element={<ProfessionalAssessmentReport />} />
            <Route path="/club-portal" element={<ClubPortalDashboard />} />
          </Routes>
        </div>
      </BrowserRouter>
    </LanguageProvider>
  );
};

// MainDashboard component with professional styling
const MainDashboard = () => {
  const { t, direction, toggleLanguage } = useLanguage();
  const { isAuthenticated, user, logout } = useAuth();
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [activeTab, setActiveTab] = useState("home");
  const [showAssessmentReport, setShowAssessmentReport] = useState(false);
  const [previousAssessments, setPreviousAssessments] = useState([]);
  const [isStartupReport, setIsStartupReport] = useState(false);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showForgotPasswordModal, setShowForgotPasswordModal] = useState(false);
  const [authMode, setAuthMode] = useState('login');

  // Redirect to assessment page after login
  useEffect(() => {
    if (isAuthenticated && activeTab === 'home') {
      setActiveTab('assessment');
    }
  }, [isAuthenticated]);

  // Clear all player-specific state when user changes or logs out
  useEffect(() => {
    console.log('=== USER STATE CHANGED ===');
    console.log('isAuthenticated:', isAuthenticated);
    console.log('user:', user);
    console.log('user.id:', user?.id);
    
    if (!isAuthenticated || !user) {
      // User logged out or not authenticated - clear everything
      console.log('Clearing all player state (user logged out)');
      setCurrentPlayer(null);
      setPreviousAssessments([]);
      setShowAssessmentReport(false);
      setActiveTab('home');
    } else {
      console.log('User authenticated, will load their data');
    }
  }, [user?.id, isAuthenticated]);

  // Check for existing player on startup - Load user's benchmarks
  useEffect(() => {
    const checkForExistingPlayer = async () => {
      if (!isAuthenticated || !user) {
        // Clear player data if not authenticated
        setCurrentPlayer(null);
        return;
      }
      
      // Clear current player first to ensure fresh data load
      setCurrentPlayer(null);
      
      try {
        // Load user's benchmarks (which are properly linked to user_id)
        const benchmarksRes = await axios.get(`${API}/auth/benchmarks`);
        const benchmarks = benchmarksRes.data || [];
        
        if (benchmarks.length > 0) {
          // Get the most recent benchmark
          const latestBenchmark = benchmarks[0]; // Already sorted by date desc from backend
          
          // Convert benchmark to assessment format for current player
          const assessmentData = {
            id: latestBenchmark.assessment_id,
            player_name: latestBenchmark.player_name,
            age: latestBenchmark.age,
            position: latestBenchmark.position,
            sprint_30m: latestBenchmark.sprint_30m,
            yo_yo_test: latestBenchmark.yo_yo_test,
            vo2_max: latestBenchmark.vo2_max,
            vertical_jump: latestBenchmark.vertical_jump,
            body_fat: latestBenchmark.body_fat,
            ball_control: latestBenchmark.ball_control,
            passing_accuracy: latestBenchmark.passing_accuracy,
            dribbling_success: latestBenchmark.dribbling_success,
            shooting_accuracy: latestBenchmark.shooting_accuracy,
            defensive_duels: latestBenchmark.defensive_duels,
            game_intelligence: latestBenchmark.game_intelligence,
            positioning: latestBenchmark.positioning,
            decision_making: latestBenchmark.decision_making,
            coachability: latestBenchmark.coachability,
            mental_toughness: latestBenchmark.mental_toughness,
            overall_score: latestBenchmark.overall_score,
            performance_level: latestBenchmark.performance_level,
            created_at: latestBenchmark.benchmark_date,
            user_id: user.id
          };
          
          await loadPreviousAssessments(assessmentData.player_name);
          setCurrentPlayer(assessmentData);
        }
      } catch (error) {
        console.error('Error checking for existing player:', error);
        setCurrentPlayer(null); // Ensure it's cleared on error
      }
    };

    checkForExistingPlayer();
  }, [isAuthenticated, user?.id]); // Added user?.id to dependencies

  const handleAssessmentCreated = async (assessment) => {
    // Load previous assessments for comparison
    await loadPreviousAssessments(assessment.player_name);
    
    setCurrentPlayer(assessment);
    setIsStartupReport(false);
    setShowAssessmentReport(true);
    
    // Auto-hide report after 20 seconds (no auto-print)
    setTimeout(() => {
      setShowAssessmentReport(false);
    }, 20000);
  };

  const loadPreviousAssessments = async (playerName) => {
    if (!isAuthenticated || !user) return;
    
    try {
      // ONLY load assessments created by this user
      const response = await axios.get(`${API}/assessments?user_id=${user.id}`);
      const playerAssessments = response.data
        .filter(assessment => assessment.player_name === playerName)
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(1); // Exclude the current (latest) assessment
      
      setPreviousAssessments(playerAssessments);
    } catch (error) {
      console.error('Error loading previous assessments:', error);
      setPreviousAssessments([]);
    }
  };

  const handleNavigate = (tab) => {
    setActiveTab(tab);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // If user is a parent, show Parent Dashboard
  if (user?.role === 'parent') {
    return <ParentDashboard />;
  }

  // If user is a coach, show Coach Dashboard
  if (user?.role === 'coach') {
    return <CoachDashboard />;
  }

  // If user is a player, show new Player Dashboard
  if (user?.role === 'player') {
    return <PlayerDashboard />;
  }

  // If user is a club admin, show Club Portal Dashboard
  if (user?.role === 'club') {
    return <ClubPortalDashboard />;
  }

  // If user is a system admin, show System Admin Portal
  if (user?.role === 'admin') {
    return <SystemAdminPortal />;
  }

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Assessment Report Modal */}
      {showAssessmentReport && currentPlayer && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg max-w-6xl max-h-[90vh] overflow-y-auto w-full">
            <div className="sticky top-0 bg-white border-b p-4 flex justify-between items-center">
              <h2 className="text-xl font-bold">
                {isStartupReport ? 'Program Startup Report' : 'Assessment Milestone Report'}
              </h2>
              <div className="flex gap-2">
                <Button
                  variant="outline"
                  onClick={() => {
                    setShowAssessmentReport(false);
                    if (!isStartupReport) {
                      setActiveTab("training");
                    }
                  }}
                >
                  Continue to Training
                </Button>
                <Button
                  variant="outline"
                  onClick={() => setShowAssessmentReport(false)}
                >
                  Close
                </Button>
              </div>
            </div>
            <div className="p-6">
              {/* Use new PlayerReport for milestone reports, keep old for startup */}
              {isStartupReport ? (
                <AssessmentReport
                  playerData={currentPlayer}
                  previousAssessments={previousAssessments}
                  showComparison={previousAssessments.length > 0}
                  isStartupReport={isStartupReport}
                />
              ) : (
                <PlayerReport playerName={currentPlayer.playerName} />
              )}
            </div>
          </div>
        </div>
      )}

      {/* Professional Header */}
      <div className="app-header">
        <div className="flex justify-between items-start w-full">
          <button
            onClick={toggleLanguage}
            className="language-toggle"
          >
            <Languages className="w-4 h-4 mr-2" />
            {direction === 'rtl' ? 'English' : 'العربية'}
          </button>
          
          <div className="flex gap-2">
            {currentPlayer && (
              <Button
                onClick={() => {
                  setIsStartupReport(false);
                  setShowAssessmentReport(true);
                }}
                variant="outline"
                size="sm"
                className="flex items-center gap-2"
              >
                <FileText className="w-4 h-4" />
                Player Reports
              </Button>
            )}
            
            {!isAuthenticated ? (
              <>
                <Button
                  onClick={() => {
                    setAuthMode('login');
                    setShowAuthModal(true);
                  }}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <LogIn className="w-4 h-4" />
                  Login
                </Button>
                <Button
                  onClick={() => {
                    setAuthMode('register');
                    setShowAuthModal(true);
                  }}
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <UserPlus className="w-4 h-4" />
                  Register
                </Button>
              </>
            ) : (
              <div className="flex items-center gap-3">
                <span className="text-sm font-medium">Welcome, {user?.full_name}</span>
                {user?.role === 'player' && (
                  <Button
                    onClick={() => setActiveTab('reports')}
                    variant="outline"
                    size="sm"
                    className="flex items-center gap-2 bg-blue-50 border-blue-300 hover:bg-blue-100"
                  >
                    <FileText className="w-4 h-4" />
                    Latest Reports
                  </Button>
                )}
                <Button
                  onClick={logout}
                  variant="outline"
                  size="sm"
                  className="flex items-center gap-2"
                >
                  <LogOut className="w-4 h-4" />
                  Logout
                </Button>
              </div>
            )}
          </div>
        </div>
        
        <h1 className="app-title">
          {t('app.title')}
        </h1>
        <p className="app-subtitle">{t('app.subtitle')}</p>
        <p className="app-description">{t('app.description')}</p>
      </div>

      {/* Professional Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <div className="tab-list">
          <button 
            onClick={() => setActiveTab("home")}
            className={`tab-trigger ${activeTab === "home" ? "active" : ""}`}
          >
            <Target className="w-4 h-4" />
            {t('nav.home')}
          </button>
          
          {/* Player Portal Tabs */}
          {(!user?.role || user?.role === 'player') && (
            <>
              <button 
                onClick={() => setActiveTab("assessment")}
                className={`tab-trigger ${activeTab === "assessment" ? "active" : ""}`}
              >
                <BarChart3 className="w-4 h-4" />
                My Assessments
              </button>
              <button 
                onClick={() => setActiveTab("training")}
                className={`tab-trigger ${activeTab === "training" ? "active" : ""}`}
              >
                <Zap className="w-4 h-4" />
                Training
              </button>
              <button 
                onClick={() => setActiveTab("progress")}
                className={`tab-trigger ${activeTab === "progress" ? "active" : ""}`}
              >
                <TrendingUp className="w-4 h-4" />
                Performance Progress
              </button>
              <button 
                onClick={() => setActiveTab("trophies")}
                className={`tab-trigger ${activeTab === "trophies" ? "active" : ""}`}
              >
                <Trophy className="w-4 h-4" />
                Achievements
              </button>
              <button 
                onClick={() => setActiveTab("inbox")}
                className={`tab-trigger ${activeTab === "inbox" ? "active" : ""}`}
              >
                <Inbox className="w-4 h-4" />
                Inbox
              </button>
              <button 
                onClick={() => setActiveTab("reports")}
                className={`tab-trigger ${activeTab === "reports" ? "active" : ""}`}
              >
                <FileText className="w-4 h-4" />
                Player Reports
              </button>
            </>
          )}
          
          {/* Coach Portal Tabs */}
          {user?.role === 'coach' && (
            <>
              <button 
                onClick={() => setActiveTab("group")}
                className={`tab-trigger ${activeTab === "group" ? "active" : ""}`}
              >
                <Users className="w-4 h-4" />
                My Roster
              </button>
              <button 
                onClick={() => setActiveTab("assessment")}
                className={`tab-trigger ${activeTab === "assessment" ? "active" : ""}`}
              >
                <BarChart3 className="w-4 h-4" />
                Player Assessments
              </button>
              <button 
                onClick={() => setActiveTab("training")}
                className={`tab-trigger ${activeTab === "training" ? "active" : ""}`}
              >
                <Zap className="w-4 h-4" />
                Training Plans
              </button>
              <button 
                onClick={() => setActiveTab("progress")}
                className={`tab-trigger ${activeTab === "progress" ? "active" : ""}`}
              >
                <TrendingUp className="w-4 h-4" />
                Team Analytics
              </button>
              <button 
                onClick={() => setActiveTab("inbox")}
                className={`tab-trigger ${activeTab === "inbox" ? "active" : ""}`}
              >
                <Inbox className="w-4 h-4" />
                Inbox
              </button>
            </>
          )}
          
          {/* Parent Portal Tabs */}
          {user?.role === 'parent' && (
            <>
              <button 
                onClick={() => setActiveTab("group")}
                className={`tab-trigger ${activeTab === "group" ? "active" : ""}`}
              >
                <Users className="w-4 h-4" />
                My Children
              </button>
              <button 
                onClick={() => setActiveTab("progress")}
                className={`tab-trigger ${activeTab === "progress" ? "active" : ""}`}
              >
                <TrendingUp className="w-4 h-4" />
                Performance Progress
              </button>
              <button 
                onClick={() => setActiveTab("reports")}
                className={`tab-trigger ${activeTab === "reports" ? "active" : ""}`}
              >
                <FileText className="w-4 h-4" />
                Reports
              </button>
              <button 
                onClick={() => setActiveTab("trophies")}
                className={`tab-trigger ${activeTab === "trophies" ? "active" : ""}`}
              >
                <Trophy className="w-4 h-4" />
                Achievements
              </button>
              <button 
                onClick={() => setActiveTab("inbox")}
                className={`tab-trigger ${activeTab === "inbox" ? "active" : ""}`}
              >
                <Inbox className="w-4 h-4" />
                Inbox
              </button>
            </>
          )}
          
          {/* Removed common tabs - each role has specific tabs only */}
          
          {user && user.role === 'admin' && (
            <button 
              onClick={() => setActiveTab("admin")}
              className={`tab-trigger ${activeTab === "admin" ? "active" : ""}`}
              style={{ backgroundColor: activeTab === "admin" ? "#dc2626" : "", color: activeTab === "admin" ? "white" : "" }}
            >
              <Shield className="w-4 h-4" />
              Admin
            </button>
          )}
        </div>

        <TabsContent value="home">
          <HomePage onNavigate={handleNavigate} onOpenAuth={() => setShowAuthModal(true)} />
        </TabsContent>

        <TabsContent value="assessment">
          <AssessmentForm onAssessmentCreated={handleAssessmentCreated} setActiveTab={setActiveTab} />
        </TabsContent>

        <TabsContent value="training">
          {currentPlayer ? (
            <TrainingDashboard 
              playerId={currentPlayer.player_name} 
              playerData={currentPlayer}
            />
          ) : (
            <Card className="professional-card text-center p-12">
              <CardContent>
                <Target className="w-16 h-16 mx-auto mb-4 text-[--text-muted]" />
                <h3 className="text-2xl font-semibold mb-2">Elite Training Dashboard</h3>
                <p className="text-[--text-muted]">Complete your assessment to unlock the advanced periodized training system with micro/macro cycles, detailed exercise instructions, and progress tracking.</p>
                <div className="mt-6 space-y-2 text-sm text-[--text-muted]">
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    Detailed exercise instructions with video guides
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    Periodized training with micro & macro cycles
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    Daily progress tracking and feedback
                  </div>
                  <div className="flex items-center justify-center gap-2">
                    <CheckCircle className="w-4 h-4 text-green-600" />
                    Performance visualization until assessment dates
                  </div>
                </div>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="inbox">
          <InboxDashboard />
        </TabsContent>

        <TabsContent value="aicoach">
          {currentPlayer ? (
            <AICoachDashboard 
              playerId={currentPlayer.player_name} 
              user={user}
            />
          ) : (
            <Card className="professional-card text-center p-12">
              <CardContent>
                <span className="text-6xl mb-4 block">🤖</span>
                <h3 className="text-2xl font-semibold mb-2">AI Coach & Analysis</h3>
                <p className="text-[--text-muted] mb-6">
                  Advanced AI-powered features including predictive modeling, computer vision form analysis, and personalized coaching feedback.
                </p>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-left max-w-2xl mx-auto">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <div className="font-semibold mb-2">📊 Predictive Analytics</div>
                    <ul className="text-sm space-y-1 text-gray-600">
                      <li>• Injury risk prediction</li>
                      <li>• Performance forecasting</li>
                      <li>• Match readiness scoring</li>
                      <li>• Optimal training load</li>
                    </ul>
                  </div>
                  <div className="p-4 bg-green-50 rounded-lg">
                    <div className="font-semibold mb-2">👁️ Computer Vision</div>
                    <ul className="text-sm space-y-1 text-gray-600">
                      <li>• Real-time pose detection</li>
                      <li>• Form analysis (squat, lunge, sprint)</li>
                      <li>• Automatic rep counting</li>
                      <li>• Video analysis</li>
                    </ul>
                  </div>
                </div>
                <Button onClick={() => setActiveTab('assessment')} className="mt-6">
                  Complete Assessment to Unlock
                </Button>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="progress">
          {currentPlayer ? (
            <ProgressTracker playerData={currentPlayer} />
          ) : (
            <ComingSoon 
              title="Advanced Progress Analytics"
              description="Comprehensive performance tracking and predictive analytics for elite player development"
              icon={TrendingUp}
              features={[
                "Real-time performance metrics",
                "Progress comparison analytics", 
                "Goal tracking and predictions",
                "Performance trend analysis"
              ]}
              estimatedRelease="Q1 2024"
              priority="high"
            />
          )}
        </TabsContent>

        <TabsContent value="voice">
          <ComingSoon 
            title="AI Voice Coaching Assistant"
            description="Intelligent voice analysis and personalized coaching feedback system"
            icon={Headphones}
            features={[
              "Voice-to-text coaching notes",
              "AI performance analysis",
              "Multilingual support",
              "Real-time coaching feedback"
            ]}
            estimatedRelease="Q2 2024"
            priority="medium"
          />
        </TabsContent>

        <TabsContent value="trophies">
          <AchievementsDisplay user={user} />
        </TabsContent>

        <TabsContent value="group">
          <ComingSoon 
            title="Team Management Platform"
            description="Advanced team coordination and group training management system"
            icon={Shield}
            features={[
              "Multi-player team management",
              "Group training coordination",
              "Coach dashboard interface",
              "Team performance analytics"
            ]}
            estimatedRelease="Q2 2024"
            priority="medium"
          />
        </TabsContent>

        <TabsContent value="highlights">
          <PerformanceHighlights playerData={currentPlayer} />
        </TabsContent>

        <TabsContent value="body">
          <PhysicalPerformanceMonitor playerData={currentPlayer} />
        </TabsContent>

        <TabsContent value="reports">
          <SavedReports />
        </TabsContent>

        <TabsContent value="admin">
          <AdminDashboard />
        </TabsContent>
      </Tabs>
      
      {/* Authentication Modal */}
      <AuthModal
        isOpen={showAuthModal}
        onClose={() => setShowAuthModal(false)}
        defaultMode={authMode}
        onForgotPassword={() => setShowForgotPasswordModal(true)}
      />

      {/* Forgot Password Modal */}
      <ForgotPasswordModal
        isOpen={showForgotPasswordModal}
        onClose={() => setShowForgotPasswordModal(false)}
        onBackToLogin={() => {
          setShowForgotPasswordModal(false);
          setShowAuthModal(true);
          setAuthMode('login');
        }}
      />
    </div>
  );
};

// Main App component with AuthProvider
export default function App() {
  return (
    <AuthProvider>
      <MainApp />
    </AuthProvider>
  );
}
