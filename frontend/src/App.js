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
import { Activity, Target, TrendingUp, Mic, MicOff, Volume2, VolumeX, Square, Trophy, Users, Music, Bell, Coins, Gift, Zap, Crown, Star, Flame, Languages, Globe, BarChart3, Award, ArrowRight, BookOpen, Lightbulb, Scale, Heart, Timer, Ruler, Info, HelpCircle, RefreshCw, Calendar, CheckCircle, Brain, Eye, Dumbbell, Gamepad2, Sparkles, Clock, Shield, Headphones, Camera, MessageSquare, Settings } from "lucide-react";
import { YOUTH_HANDBOOK_STANDARDS, ASSESSMENT_EXPLANATIONS, evaluatePerformance, getAgeCategory, calculateOverallScore } from "./AssessmentStandards";
import ProgressTracker from "./components/ProgressTracker";
import ComingSoon from "./components/ComingSoon";
import VO2MaxCalculator from "./components/VO2MaxCalculator";

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
      'nav.assessment': 'Assessment',
      'nav.training': 'Training Programs',
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
      'nav.assessment': 'التقييم',
      'nav.training': 'برامج التدريب',
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
const AssessmentForm = ({ onAssessmentCreated }) => {
  const { t, direction } = useLanguage();
  const [formData, setFormData] = useState({
    player_name: "",
    age: "",
    position: "",
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

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);
    try {
      const response = await axios.post(`${API}/assessments`, formData);
      onAssessmentCreated(response.data);
      // Reset form
      setFormData({
        player_name: "",
        age: "",
        position: "",
        sprint_30m: "",
        yo_yo_test: "",
        vo2_max: "",
        vertical_jump: "",
        body_fat: "",
        ball_control: "",
        passing_accuracy: "",
        dribbling_success: "",
        shooting_accuracy: "",
        defensive_duels: "",
        game_intelligence: "",
        positioning: "",
        decision_making: "",
        coachability: "",
        mental_toughness: ""
      });
    } catch (error) {
      console.error("Error creating assessment:", error);
    }
    setIsLoading(false);
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
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Information */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <Label htmlFor="player_name" className="text-base font-medium mb-2 block" style={{color: 'var(--text-black)'}}>
                  Player Name
                </Label>
                <input
                  id="player_name"
                  name="player_name"
                  value={formData.player_name}
                  onChange={handleChange}
                  required
                  className="input-field"
                  placeholder="Enter player name"
                />
              </div>
              <div>
                <Label htmlFor="age" className="text-base font-medium mb-2 block" style={{color: 'var(--text-black)'}}>
                  Age
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
                  Position
                </Label>
                <Select onValueChange={(value) => setFormData({...formData, position: value})}>
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

            {/* Physical Performance - 20% Weight */}
            <div className="assessment-section">
              <h3>
                <Dumbbell className="w-6 h-6" />
                Physical Performance Tests
                <span className="weight-badge">20% Weight</span>
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {['sprint_30m', 'yo_yo_test', 'vo2_max', 'vertical_jump', 'body_fat'].map((field) => (
                  <div key={field}>
                    <Label className="text-base font-medium mb-2 block">
                      {field === 'sprint_30m' && '30m Sprint (seconds)'}
                      {field === 'yo_yo_test' && 'Yo-Yo Test (meters)'}
                      {field === 'vo2_max' && 'VO2 Max (ml/kg/min)'}
                      {field === 'vertical_jump' && 'Vertical Jump (cm)'}
                      {field === 'body_fat' && 'Body Fat (%)'}
                    </Label>
                    <input
                      name={field}
                      type="number"
                      step={field === 'sprint_30m' || field === 'vo2_max' || field === 'body_fat' ? '0.1' : '1'}
                      value={formData[field]}
                      onChange={handleChange}
                      required
                      className={getFieldValidation(field, formData[field], formData.age)}
                      placeholder={
                        field === 'sprint_30m' ? 'e.g., 4.2' :
                        field === 'yo_yo_test' ? 'e.g., 1600' :
                        field === 'vo2_max' ? 'e.g., 58.5' :
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
const App = () => {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <div className="min-h-screen">
          <Routes>
            <Route path="/" element={<MainDashboard />} />
          </Routes>
        </div>
      </BrowserRouter>
    </LanguageProvider>
  );
};

// MainDashboard component with professional styling
const MainDashboard = () => {
  const { t, direction, toggleLanguage } = useLanguage();
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [activeTab, setActiveTab] = useState("assessment");

  const handleAssessmentCreated = (assessment) => {
    setCurrentPlayer(assessment);
    setActiveTab("training");
  };

  return (
    <div className="container mx-auto px-4 py-8 max-w-7xl">
      {/* Professional Header */}
      <div className="app-header">
        <button
          onClick={toggleLanguage}
          className="language-toggle"
        >
          <Languages className="w-4 h-4 mr-2" />
          {direction === 'rtl' ? 'English' : 'العربية'}
        </button>
        
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
            onClick={() => setActiveTab("assessment")}
            className={`tab-trigger ${activeTab === "assessment" ? "active" : ""}`}
          >
            <Target className="w-4 h-4" />
            {t('nav.assessment')}
          </button>
          <button 
            onClick={() => setActiveTab("training")}
            className={`tab-trigger ${activeTab === "training" ? "active" : ""}`}
          >
            <Zap className="w-4 h-4" />
            {t('nav.training')}
          </button>
          <button 
            onClick={() => setActiveTab("progress")}
            className={`tab-trigger ${activeTab === "progress" ? "active" : ""}`}
          >
            <TrendingUp className="w-4 h-4" />
            {t('nav.progress')}
          </button>
          <button 
            onClick={() => setActiveTab("voice")}
            className={`tab-trigger ${activeTab === "voice" ? "active" : ""}`}
          >
            <Mic className="w-4 h-4" />
            {t('nav.voice')}
          </button>
          <button 
            onClick={() => setActiveTab("trophies")}
            className={`tab-trigger ${activeTab === "trophies" ? "active" : ""}`}
          >
            <Trophy className="w-4 h-4" />
            {t('nav.trophies')}
          </button>
          <button 
            onClick={() => setActiveTab("group")}
            className={`tab-trigger ${activeTab === "group" ? "active" : ""}`}
          >
            <Users className="w-4 h-4" />
            {t('nav.group')}
          </button>
          <button 
            onClick={() => setActiveTab("highlights")}
            className={`tab-trigger ${activeTab === "highlights" ? "active" : ""}`}
          >
            <BarChart3 className="w-4 h-4" />
            {t('nav.highlights')}
          </button>
          <button 
            onClick={() => setActiveTab("body")}
            className={`tab-trigger ${activeTab === "body" ? "active" : ""}`}
          >
            <Activity className="w-4 h-4" />
            {t('nav.body')}
          </button>
        </div>

        <TabsContent value="assessment">
          <AssessmentForm onAssessmentCreated={handleAssessmentCreated} />
        </TabsContent>

        <TabsContent value="training">
          {currentPlayer ? (
            <TrainingProgram 
              playerId={currentPlayer.id} 
              playerName={currentPlayer.player_name}
              playerData={currentPlayer}
            />
          ) : (
            <Card className="professional-card text-center p-12">
              <CardContent>
                <Target className="w-16 h-16 mx-auto mb-4 text-[--text-muted]" />
                <h3 className="text-2xl font-semibold mb-2">Complete Assessment First</h3>
                <p className="text-[--text-muted]">Create a professional player assessment to unlock personalized training programs.</p>
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
          <ComingSoon 
            title="Achievement & Recognition System"
            description="Comprehensive achievement tracking with performance milestones and rewards"
            icon={Trophy}
            features={[
              "Performance achievement badges",
              "Milestone tracking system",
              "Digital certificate generation",
              "Global player rankings"
            ]}
            estimatedRelease="Q1 2024"
            priority="high"
          />
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
          <ComingSoon 
            title="Performance Analytics Dashboard"
            description="Advanced analytics and performance visualization for data-driven improvement"
            icon={BarChart3}
            features={[
              "Advanced performance analytics",
              "Video analysis integration",
              "Performance highlight generation",
              "Comparative analysis tools"
            ]}
            estimatedRelease="Q3 2024"
            priority="low"
          />
        </TabsContent>

        <TabsContent value="body">
          <ComingSoon 
            title="Physical Performance Monitor"
            description="Comprehensive fitness tracking and body composition analysis system"
            icon={Activity}
            features={[
              "Body composition tracking",
              "Fitness goal management",
              "Nutrition planning integration",
              "Recovery monitoring system"
            ]}
            estimatedRelease="Q1 2024"
            priority="high"
          />
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default App;