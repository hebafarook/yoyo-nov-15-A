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
import { Activity, Target, TrendingUp, Mic, MicOff, Volume2, VolumeX, Square, Trophy, Users, Music, Bell, Coins, Gift, Zap, Crown, Star, Flame, Languages, Globe, BarChart3, Award, ArrowUp, ArrowDown, Equal, BookOpen, Lightbulb, Scale, Heart, Timer, Ruler, Info, HelpCircle, RefreshCw, Calendar, CheckCircle, Brain, Eye, Dumbbell, Gamepad2 } from "lucide-react";
import { YOUTH_HANDBOOK_STANDARDS, ASSESSMENT_EXPLANATIONS, evaluatePerformance, getAgeCategory, calculateOverallScore } from "./AssessmentStandards";

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Daily Progressive Training Structure
const DAILY_PROGRESSIVE_STRUCTURE = {
  week1: {
    theme: "Foundation Building",
    daily_focus: {
      monday: { focus: "Speed Foundation", intensity: "Medium", duration: 60 },
      tuesday: { focus: "Ball Control Basics", intensity: "High", duration: 90 },
      wednesday: { focus: "Flexibility & Recovery", intensity: "Low", duration: 45 },
      thursday: { focus: "Agility Introduction", intensity: "Medium", duration: 75 },
      friday: { focus: "Shooting Technique", intensity: "High", duration: 60 },
      saturday: { focus: "Small-sided Games", intensity: "High", duration: 90 },
      sunday: { focus: "Active Recovery", intensity: "Low", duration: 30 }
    }
  },
  week2: {
    theme: "Skill Development",
    daily_focus: {
      monday: { focus: "Speed Progression", intensity: "High", duration: 60 },
      tuesday: { focus: "Advanced Ball Skills", intensity: "High", duration: 90 },
      wednesday: { focus: "Tactical Awareness", intensity: "Medium", duration: 75 },
      thursday: { focus: "Agility Challenges", intensity: "High", duration: 75 },
      friday: { focus: "Finishing Drills", intensity: "High", duration: 60 },
      saturday: { focus: "Match Simulation", intensity: "High", duration: 90 },
      sunday: { focus: "Analysis & Recovery", intensity: "Low", duration: 45 }
    }
  },
  week3: {
    theme: "Performance Enhancement",
    daily_focus: {
      monday: { focus: "Explosive Speed", intensity: "Very High", duration: 60 },
      tuesday: { focus: "1v1 Mastery", intensity: "High", duration: 90 },
      wednesday: { focus: "Positional Play", intensity: "Medium", duration: 75 },
      thursday: { focus: "Complex Agility", intensity: "High", duration: 75 },
      friday: { focus: "Power Shooting", intensity: "Very High", duration: 60 },
      saturday: { focus: "Competitive Matches", intensity: "Very High", duration: 90 },
      sunday: { focus: "Mental Training", intensity: "Low", duration: 45 }
    }
  },
  week4: {
    theme: "Assessment & Refinement",
    daily_focus: {
      monday: { focus: "Speed Testing", intensity: "High", duration: 60 },
      tuesday: { focus: "Skill Assessment", intensity: "High", duration: 90 },
      wednesday: { focus: "Tactical Testing", intensity: "Medium", duration: 75 },
      thursday: { focus: "Agility Evaluation", intensity: "High", duration: 75 },
      friday: { focus: "Shooting Assessment", intensity: "High", duration: 60 },
      saturday: { focus: "Performance Review", intensity: "Medium", duration: 60 },
      sunday: { focus: "Program Planning", intensity: "Low", duration: 30 }
    }
  }
};

// Exercise library with detailed explanations
const EXERCISE_LIBRARY = {
  speed: {
    "Sprint Intervals": {
      description: "High-intensity short bursts to improve acceleration and maximum speed",
      technique: "Focus on proper starting position, drive phase, and stride mechanics",
      progression: "Week 1: 6x30m, Week 2: 8x30m, Week 3: 6x50m, Week 4: Assessment",
      rest_interval: "90-120 seconds between reps"
    },
    "Acceleration Drills": {
      description: "Multi-directional starts to improve first-step quickness",
      technique: "Low body position, powerful first steps, gradual stride lengthening",
      progression: "Week 1: 5x20m, Week 2: 6x20m, Week 3: 8x25m, Week 4: Testing",
      rest_interval: "60-90 seconds between reps"
    }
  },
  ballSkills: {
    "Juggling Progression": {
      description: "Sequential ball control using different body parts",
      technique: "Start with thighs, progress to feet, then head combinations",
      progression: "Week 1: 50 touches, Week 2: 100 touches, Week 3: 200 touches, Week 4: Mixed body parts",
      rest_interval: "30 seconds between sets"
    },
    "1v1 Moves": {
      description: "Individual dribbling techniques to beat defenders",
      technique: "Close control, body feints, change of pace and direction",
      progression: "Week 1: Basic moves, Week 2: Combined moves, Week 3: Under pressure, Week 4: Game situation",
      rest_interval: "45 seconds between attempts"
    }
  },
  fitness: {
    "Yo-Yo Intermittent Test": {
      description: "Progressive shuttle run test measuring aerobic and anaerobic capacity",
      technique: "Controlled pace, efficient turning, listen to audio cues",
      progression: "Week 1: Familiarization, Week 2: Baseline, Week 3: Improvement, Week 4: Retest",
      rest_interval: "Dictated by audio cues"
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
      'app.title': 'Yoyo the Fire Boy ⚽🔥',
      'app.subtitle': 'Professional Soccer Training Tracker',
      'nav.assessment': 'Assessment',
      'nav.training': 'Training Programs',
      'nav.progress': 'Progress Tracking',
      'nav.voice': 'Voice Notes',
      'nav.trophies': 'Trophies & Achievements',
      'nav.group': 'Group Training',
      'nav.highlights': 'Player Highlights',
      'nav.body': 'Body & Fitness',
      'assessment.title': 'Fire Boy Assessment 🔥',
      'assessment.subtitle': 'Ignite Your Soccer Journey!',
      'assessment.playerName': 'Player Name',
      'assessment.playerNamePlaceholder': 'Enter your fire name',
      'assessment.starAge': 'Age',
      'assessment.agePlaceholder': 'Your age',
      'assessment.powerPosition': 'Position',
      'assessment.positionPlaceholder': 'Select your position',
      'assessment.positions.goalkeeper': 'Goalkeeper',
      'assessment.positions.defender': 'Defender', 
      'assessment.positions.midfielder': 'Midfielder',
      'assessment.positions.forward': 'Forward',
      'assessment.positions.striker': 'Striker',
      'assessment.speedMetrics': 'Speed & Acceleration 🏃‍♂️⚡',
      'assessment.agilityMetrics': 'Agility & Movement 🎯⚡',
      'assessment.flexibilityMetrics': 'Flexibility & Mobility 🤸‍♂️',
      'assessment.ballHandling': 'Ball Control & Skills ⚽✨',
      'assessment.bodyComposition': 'Body Composition & Fitness 💪',
      'assessment.fields.sprint30': '30m Sprint (seconds)',
      'assessment.fields.yoyoTest': 'Yo-Yo Test (meters)',
      'assessment.fields.vo2Max': 'VO2 Max (ml/kg/min)',
      'assessment.fields.verticalJump': 'Vertical Jump (cm)',
      'assessment.fields.bodyFat': 'Body Fat (%)',
      'assessment.fields.ballControl': 'Ball Control (1-5)',
      'assessment.fields.passing': 'Passing Accuracy (%)',
      'assessment.fields.dribbling': 'Dribbling Success (%)',
      'assessment.fields.shooting': 'Shooting Accuracy (%)',
      'assessment.fields.defensive': 'Defensive Duels (%)',
      'assessment.submitButton': 'Create Fire Boy Assessment 🔥',
      'assessment.submitting': 'Creating Assessment...',
      'training.title': 'Training Programs 🏆',
      'training.generateAI': 'Generate AI Program',
      'training.generateRonaldo': 'Ronaldo Template',
      'training.benchmarkTitle': 'Performance Benchmark Analysis',
      'training.ageGroup': 'Age Group: {age} years ({category})',
      'training.mainWeaknesses': 'Priority Areas for Improvement',
      'training.mainStrengths': 'Current Strengths',
      'training.trainingFocus': 'Recommended Training Focus',
      'training.weeklyStructure': 'Weekly Training Structure',
      'training.dailyProgression': 'Daily Progression Plan',
      'training.retestButton': 'Schedule Retest',
      'common.youth_12_14': '12-14 Years',
      'common.youth_15_16': '15-16 Years', 
      'common.youth_17_18': '17-18 Years',
      'common.elite': 'Elite/Professional',
      'common.excellent': 'Excellent',
      'common.good': 'Good',
      'common.average': 'Average',
      'common.poor': 'Needs Improvement'
    },
    ar: {
      'app.title': 'يويو الفتى الناري ⚽🔥',
      'app.subtitle': 'متتبع التدريب الاحترافي لكرة القدم',
      'nav.assessment': 'التقييم',
      'nav.training': 'برامج التدريب',
      'nav.progress': 'تتبع التقدم',
      'nav.voice': 'الملاحظات الصوتية',
      'nav.trophies': 'الكؤوس والإنجازات',
      'nav.group': 'التدريب الجماعي',
      'nav.highlights': 'أبرز اللاعبين',
      'nav.body': 'الجسم واللياقة',
      'assessment.title': 'تقييم الفتى الناري 🔥',
      'assessment.subtitle': 'اشعل رحلة كرة القدم!',
      'assessment.playerName': 'اسم اللاعب',
      'assessment.playerNamePlaceholder': 'أدخل اسمك الناري',
      'assessment.starAge': 'العمر',
      'assessment.agePlaceholder': 'عمرك',
      'assessment.powerPosition': 'المركز',
      'assessment.positionPlaceholder': 'اختر مركزك',
      'assessment.positions.goalkeeper': 'حارس مرمى',
      'assessment.positions.defender': 'مدافع',
      'assessment.positions.midfielder': 'لاعب وسط',
      'assessment.positions.forward': 'مهاجم',
      'assessment.positions.striker': 'مهاجم صريح',
      'assessment.speedMetrics': 'السرعة والتسارع 🏃‍♂️⚡',
      'assessment.agilityMetrics': 'الرشاقة والحركة 🎯⚡',
      'assessment.flexibilityMetrics': 'المرونة والحركة 🤸‍♂️',
      'assessment.ballHandling': 'التحكم بالكرة والمهارات ⚽✨',
      'assessment.bodyComposition': 'تركيب الجسم واللياقة 💪',
      'assessment.fields.sprint30': 'عدو 30 متر (ثواني)',
      'assessment.fields.yoyoTest': 'اختبار يو-يو (أمتار)',
      'assessment.fields.vo2Max': 'الحد الأقصى للأكسجين',
      'assessment.fields.verticalJump': 'القفز العمودي (سم)',
      'assessment.fields.bodyFat': 'دهون الجسم (%)',
      'assessment.fields.ballControl': 'التحكم بالكرة (1-5)',
      'assessment.fields.passing': 'دقة التمرير (%)',
      'assessment.fields.dribbling': 'نجاح المراوغة (%)',
      'assessment.fields.shooting': 'دقة التسديد (%)',
      'assessment.fields.defensive': 'المواجهات الدفاعية (%)',
      'assessment.submitButton': 'إنشاء تقييم الفتى الناري 🔥',
      'assessment.submitting': 'جاري إنشاء التقييم...',
      'training.title': 'برامج التدريب 🏆',
      'training.generateAI': 'إنشاء برنامج ذكي',
      'training.generateRonaldo': 'قالب رونالدو',
      'training.benchmarkTitle': 'تحليل معايير الأداء',
      'training.ageGroup': 'الفئة العمرية: {age} سنة ({category})',
      'training.mainWeaknesses': 'المجالات ذات الأولوية للتحسين',
      'training.mainStrengths': 'نقاط القوة الحالية',
      'training.trainingFocus': 'التركيز التدريبي الموصى به',
      'training.weeklyStructure': 'هيكل التدريب الأسبوعي',
      'training.dailyProgression': 'خطة التقدم اليومي',
      'training.retestButton': 'جدولة إعادة الاختبار',
      'common.youth_12_14': '12-14 سنة',
      'common.youth_15_16': '15-16 سنة',
      'common.youth_17_18': '17-18 سنة',
      'common.elite': 'نخبة/محترف',
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
    <div className="mb-6">
      <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300">
        <CardHeader>
          <CardTitle className="text-blue-800 flex items-center text-lg">
            <Award className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
            Performance Standards Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-white rounded-lg border border-yellow-200">
              <Crown className="w-8 h-8 mx-auto mb-2 text-yellow-600" />
              <h4 className="font-bold text-yellow-800">{t('common.excellent')}</h4>
              <p className="text-sm text-yellow-600">Elite/International level</p>
            </div>
            <div className="text-center p-4 bg-white rounded-lg border border-green-200">
              <Award className="w-8 h-8 mx-auto mb-2 text-green-600" />
              <h4 className="font-bold text-green-800">{t('common.good')}</h4>
              <p className="text-sm text-green-600">High competitive standard</p>
            </div>
            <div className="text-center p-4 bg-white rounded-lg border border-blue-200">
              <Star className="w-8 h-8 mx-auto mb-2 text-blue-600" />
              <h4 className="font-bold text-blue-800">{t('common.average')}</h4>
              <p className="text-sm text-blue-600">Solid club level</p>
            </div>
            <div className="text-center p-4 bg-white rounded-lg border border-orange-200">
              <Users className="w-8 h-8 mx-auto mb-2 text-orange-600" />
              <h4 className="font-bold text-orange-800">{t('common.poor')}</h4>
              <p className="text-sm text-orange-600">Development needed</p>
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
    <div className="mt-2">
      <Button
        type="button"
        variant="ghost"
        size="sm"
        onClick={onToggle}
        className="text-xs text-blue-600 hover:text-blue-800"
      >
        <HelpCircle className="w-3 h-3 mr-1" />
        {isVisible ? 'Hide Explanation' : 'Show Explanation'}
      </Button>
      
      {isVisible && (
        <div className="mt-2 p-3 bg-blue-50 rounded-lg border border-blue-200">
          <h5 className="font-bold text-blue-800 mb-1">{explanation.title}</h5>
          <p className="text-sm text-blue-700 mb-2" dir={direction}>{explanation.description}</p>
          <p className="text-xs text-blue-600 mb-1"><strong>Why it matters:</strong> {explanation.importance}</p>
          <p className="text-xs text-green-600 mb-1"><strong>Tips:</strong> {explanation.tips}</p>
          <p className="text-xs text-purple-600"><strong>Scoring:</strong> {explanation.scoring}</p>
        </div>
      )}
    </div>
  );
};

// Enhanced Assessment Component with Complete Handbook Standards
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
    if (!value || !age) return null;
    
    const numValue = parseFloat(value);
    const ageCategory = getAgeCategory(parseInt(age));
    const performance = evaluatePerformance(numValue, fieldName, ageCategory);
    
    if (!performance) return null;
    
    const colors = {
      excellent: 'border-yellow-400 bg-yellow-50',
      good: 'border-green-400 bg-green-50',
      average: 'border-blue-400 bg-blue-50',
      poor: 'border-orange-400 bg-orange-50'
    };
    
    return colors[performance];
  };

  return (
    <div>
      <StandardsLegend />
      <Card className="max-w-6xl mx-auto bg-gradient-to-br from-orange-50 via-red-50 to-yellow-50 border-orange-300 fire-glow">
        <CardHeader className="text-center">
          <CardTitle className="text-4xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 bg-clip-text text-transparent">
            {t('assessment.title')}
          </CardTitle>
          <CardDescription className="text-orange-700 text-lg font-semibold">
            Complete Youth Handbook Assessment Framework
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <Label htmlFor="player_name" className="text-orange-800 font-bold flex items-center">
                  <Flame className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-4 h-4`} />
                  Player Name
                </Label>
                <Input
                  id="player_name"
                  name="player_name"
                  value={formData.player_name}
                  onChange={handleChange}
                  required
                  className="border-orange-400 focus:border-red-500 bg-gradient-to-r from-orange-100 to-yellow-100"
                  dir={direction}
                  placeholder="Enter fire boy name"
                />
              </div>
              <div>
                <Label htmlFor="age" className="text-orange-800 font-bold flex items-center">
                  <Star className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-4 h-4`} />
                  Age
                </Label>
                <Input
                  id="age"
                  name="age"
                  type="number"
                  min="12"
                  max="25"
                  value={formData.age}
                  onChange={handleChange}
                  required
                  className="border-orange-400 focus:border-red-500 bg-gradient-to-r from-orange-100 to-yellow-100"
                  placeholder="Your age"
                />
                {formData.age && (
                  <Badge className="mt-1 bg-blue-100 text-blue-800">
                    Age Group: {getAgeCategory(parseInt(formData.age))}
                  </Badge>
                )}
              </div>
              <div>
                <Label htmlFor="position" className="text-orange-800 font-bold flex items-center">
                  <Target className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-4 h-4`} />
                  Position
                </Label>
                <Select onValueChange={(value) => setFormData({...formData, position: value})}>
                  <SelectTrigger className="border-orange-400 focus:border-red-500 bg-gradient-to-r from-orange-100 to-yellow-100">
                    <SelectValue placeholder="Select your position" />
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

            {/* Physical Metrics - 20% Weight */}
            <div className="bg-gradient-to-r from-red-100 to-orange-100 rounded-lg p-6 border-2 border-red-300 fire-glow">
              <h3 className="text-xl font-bold text-red-800 mb-4 flex items-center">
                <Dumbbell className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} text-yellow-500`} />
                Physical Performance Tests (20% Weight) 💪
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="sprint_30m" className="text-red-700 font-semibold">30m Sprint (seconds)</Label>
                  <Input
                    id="sprint_30m"
                    name="sprint_30m"
                    type="number"
                    step="0.01"
                    min="3.5"
                    max="8"
                    value={formData.sprint_30m}
                    onChange={handleChange}
                    required
                    className={`border-red-400 focus:border-red-600 bg-gradient-to-r from-red-50 to-orange-50 ${getFieldValidation('sprint_30m', formData.sprint_30m, formData.age) || ''}`}
                    placeholder="e.g., 4.2"
                  />
                  <FieldExplanation 
                    fieldName="sprint_30m" 
                    isVisible={explanationVisibility.sprint_30m}
                    onToggle={() => toggleExplanation('sprint_30m')}
                  />
                </div>
                <div>
                  <Label htmlFor="yo_yo_test" className="text-red-700 font-semibold">Yo-Yo Test (meters)</Label>
                  <Input
                    id="yo_yo_test"
                    name="yo_yo_test"
                    type="number"
                    min="400"
                    max="3000"
                    value={formData.yo_yo_test}
                    onChange={handleChange}
                    required
                    className={`border-red-400 focus:border-red-600 bg-gradient-to-r from-red-50 to-orange-50 ${getFieldValidation('yo_yo_test', formData.yo_yo_test, formData.age) || ''}`}
                    placeholder="e.g., 1600"
                  />
                  <FieldExplanation 
                    fieldName="yo_yo_test" 
                    isVisible={explanationVisibility.yo_yo_test}
                    onToggle={() => toggleExplanation('yo_yo_test')}
                  />
                </div>
                <div>
                  <Label htmlFor="vo2_max" className="text-red-700 font-semibold">VO2 Max (ml/kg/min)</Label>
                  <Input
                    id="vo2_max"
                    name="vo2_max"
                    type="number"
                    step="0.1"
                    min="35"
                    max="80"
                    value={formData.vo2_max}
                    onChange={handleChange}
                    required
                    className={`border-red-400 focus:border-red-600 bg-gradient-to-r from-red-50 to-orange-50 ${getFieldValidation('vo2_max', formData.vo2_max, formData.age) || ''}`}
                    placeholder="e.g., 58.5"
                  />
                  <FieldExplanation 
                    fieldName="vo2_max" 
                    isVisible={explanationVisibility.vo2_max}
                    onToggle={() => toggleExplanation('vo2_max')}
                  />
                </div>
                <div>
                  <Label htmlFor="vertical_jump" className="text-red-700 font-semibold">Vertical Jump (cm)</Label>
                  <Input
                    id="vertical_jump"
                    name="vertical_jump"
                    type="number"
                    min="20"
                    max="80"
                    value={formData.vertical_jump}
                    onChange={handleChange}
                    required
                    className={`border-red-400 focus:border-red-600 bg-gradient-to-r from-red-50 to-orange-50 ${getFieldValidation('vertical_jump', formData.vertical_jump, formData.age) || ''}`}
                    placeholder="e.g., 55"
                  />
                  <FieldExplanation 
                    fieldName="vertical_jump" 
                    isVisible={explanationVisibility.vertical_jump}
                    onToggle={() => toggleExplanation('vertical_jump')}
                  />
                </div>
                <div>
                  <Label htmlFor="body_fat" className="text-red-700 font-semibold">Body Fat (%)</Label>
                  <Input
                    id="body_fat"
                    name="body_fat"
                    type="number"
                    step="0.1"
                    min="5"
                    max="30"
                    value={formData.body_fat}
                    onChange={handleChange}
                    required
                    className={`border-red-400 focus:border-red-600 bg-gradient-to-r from-red-50 to-orange-50 ${getFieldValidation('body_fat', formData.body_fat, formData.age) || ''}`}
                    placeholder="e.g., 12.5"
                  />
                  <FieldExplanation 
                    fieldName="body_fat" 
                    isVisible={explanationVisibility.body_fat}
                    onToggle={() => toggleExplanation('body_fat')}
                  />
                </div>
              </div>
            </div>

            {/* Technical Skills - 40% Weight */}
            <div className="bg-gradient-to-r from-purple-100 to-pink-100 rounded-lg p-6 border-2 border-purple-400 fire-glow">
              <h3 className="text-xl font-bold text-purple-800 mb-4 flex items-center">
                <Gamepad2 className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} text-pink-500`} />
                Technical Skills Assessment (40% Weight) ⚽✨
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="ball_control" className="text-purple-700 font-semibold">Ball Control (1-5 scale)</Label>
                  <Input
                    id="ball_control"
                    name="ball_control"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.ball_control}
                    onChange={handleChange}
                    required
                    className={`border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50 ${getFieldValidation('ball_control', formData.ball_control, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="ball_control" 
                    isVisible={explanationVisibility.ball_control}
                    onToggle={() => toggleExplanation('ball_control')}
                  />
                </div>
                <div>
                  <Label htmlFor="passing_accuracy" className="text-purple-700 font-semibold">Passing Accuracy (%)</Label>
                  <Input
                    id="passing_accuracy"
                    name="passing_accuracy"
                    type="number"
                    step="0.1"
                    min="40"
                    max="100"
                    value={formData.passing_accuracy}
                    onChange={handleChange}
                    required
                    className={`border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50 ${getFieldValidation('passing_accuracy', formData.passing_accuracy, formData.age) || ''}`}
                    placeholder="e.g., 85.5"
                  />
                  <FieldExplanation 
                    fieldName="passing_accuracy" 
                    isVisible={explanationVisibility.passing_accuracy}
                    onToggle={() => toggleExplanation('passing_accuracy')}
                  />
                </div>
                <div>
                  <Label htmlFor="dribbling_success" className="text-purple-700 font-semibold">Dribbling Success (%)</Label>
                  <Input
                    id="dribbling_success"
                    name="dribbling_success"
                    type="number"
                    step="0.1"
                    min="20"
                    max="100"
                    value={formData.dribbling_success}
                    onChange={handleChange}
                    required
                    className={`border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50 ${getFieldValidation('dribbling_success', formData.dribbling_success, formData.age) || ''}`}
                    placeholder="e.g., 65.0"
                  />
                  <FieldExplanation 
                    fieldName="dribbling_success" 
                    isVisible={explanationVisibility.dribbling_success}
                    onToggle={() => toggleExplanation('dribbling_success')}
                  />
                </div>
                <div>
                  <Label htmlFor="shooting_accuracy" className="text-purple-700 font-semibold">Shooting Accuracy (%)</Label>
                  <Input
                    id="shooting_accuracy"
                    name="shooting_accuracy"
                    type="number"
                    step="0.1"
                    min="30"
                    max="100"
                    value={formData.shooting_accuracy}
                    onChange={handleChange}
                    required
                    className={`border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50 ${getFieldValidation('shooting_accuracy', formData.shooting_accuracy, formData.age) || ''}`}
                    placeholder="e.g., 72.5"
                  />
                  <FieldExplanation 
                    fieldName="shooting_accuracy" 
                    isVisible={explanationVisibility.shooting_accuracy}
                    onToggle={() => toggleExplanation('shooting_accuracy')}
                  />
                </div>
                <div>
                  <Label htmlFor="defensive_duels" className="text-purple-700 font-semibold">Defensive Duels (%)</Label>
                  <Input
                    id="defensive_duels"
                    name="defensive_duels"
                    type="number"
                    step="0.1"
                    min="30"
                    max="100"
                    value={formData.defensive_duels}
                    onChange={handleChange}
                    required
                    className={`border-purple-400 focus:border-pink-500 bg-gradient-to-r from-purple-50 to-pink-50 ${getFieldValidation('defensive_duels', formData.defensive_duels, formData.age) || ''}`}
                    placeholder="e.g., 68.0"
                  />
                  <FieldExplanation 
                    fieldName="defensive_duels" 
                    isVisible={explanationVisibility.defensive_duels}
                    onToggle={() => toggleExplanation('defensive_duels')}
                  />
                </div>
              </div>
            </div>

            {/* Tactical Awareness - 30% Weight */}
            <div className="bg-gradient-to-r from-blue-100 to-green-100 rounded-lg p-6 border-2 border-blue-400 fire-glow">
              <h3 className="text-xl font-bold text-blue-800 mb-4 flex items-center">
                <Brain className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} text-green-500`} />
                Tactical Awareness Assessment (30% Weight) 🧠⚽
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="game_intelligence" className="text-blue-700 font-semibold">Game Intelligence (1-5)</Label>
                  <Input
                    id="game_intelligence"
                    name="game_intelligence"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.game_intelligence}
                    onChange={handleChange}
                    required
                    className={`border-blue-400 focus:border-green-500 bg-gradient-to-r from-blue-50 to-green-50 ${getFieldValidation('game_intelligence', formData.game_intelligence, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="game_intelligence" 
                    isVisible={explanationVisibility.game_intelligence}
                    onToggle={() => toggleExplanation('game_intelligence')}
                  />
                </div>
                <div>
                  <Label htmlFor="positioning" className="text-blue-700 font-semibold">Positioning (1-5)</Label>
                  <Input
                    id="positioning"
                    name="positioning"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.positioning}
                    onChange={handleChange}
                    required
                    className={`border-blue-400 focus:border-green-500 bg-gradient-to-r from-blue-50 to-green-50 ${getFieldValidation('positioning', formData.positioning, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="positioning" 
                    isVisible={explanationVisibility.positioning}
                    onToggle={() => toggleExplanation('positioning')}
                  />
                </div>
                <div>
                  <Label htmlFor="decision_making" className="text-blue-700 font-semibold">Decision Making (1-5)</Label>
                  <Input
                    id="decision_making"
                    name="decision_making"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.decision_making}
                    onChange={handleChange}
                    required
                    className={`border-blue-400 focus:border-green-500 bg-gradient-to-r from-blue-50 to-green-50 ${getFieldValidation('decision_making', formData.decision_making, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="decision_making" 
                    isVisible={explanationVisibility.decision_making}
                    onToggle={() => toggleExplanation('decision_making')}
                  />
                </div>
              </div>
            </div>

            {/* Psychological Traits - 10% Weight */}
            <div className="bg-gradient-to-r from-teal-100 to-cyan-100 rounded-lg p-6 border-2 border-teal-400 fire-glow">
              <h3 className="text-xl font-bold text-teal-800 mb-4 flex items-center">
                <Heart className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} text-cyan-500`} />
                Psychological Traits Assessment (10% Weight) 💚🧠
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="coachability" className="text-teal-700 font-semibold">Coachability (1-5)</Label>
                  <Input
                    id="coachability"
                    name="coachability"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.coachability}
                    onChange={handleChange}
                    required
                    className={`border-teal-400 focus:border-cyan-500 bg-gradient-to-r from-teal-50 to-cyan-50 ${getFieldValidation('coachability', formData.coachability, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="coachability" 
                    isVisible={explanationVisibility.coachability}
                    onToggle={() => toggleExplanation('coachability')}
                  />
                </div>
                <div>
                  <Label htmlFor="mental_toughness" className="text-teal-700 font-semibold">Mental Toughness (1-5)</Label>
                  <Input
                    id="mental_toughness"
                    name="mental_toughness"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.mental_toughness}
                    onChange={handleChange}
                    required
                    className={`border-teal-400 focus:border-cyan-500 bg-gradient-to-r from-teal-50 to-cyan-50 ${getFieldValidation('mental_toughness', formData.mental_toughness, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="mental_toughness" 
                    isVisible={explanationVisibility.mental_toughness}
                    onToggle={() => toggleExplanation('mental_toughness')}
                  />
                </div>
              </div>
            </div>

            <Button 
              type="submit" 
              disabled={isLoading}
              className="w-full bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 hover:from-orange-700 hover:via-red-700 hover:to-yellow-700 text-white font-bold py-4 px-8 rounded-lg transition-all duration-300 transform hover:scale-105 fire-glow text-xl"
            >
              {isLoading ? 'Creating Complete Assessment...' : 'Create Fire Boy Assessment 🔥'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  );
};

// Daily Progressive Program Component
const DailyProgressiveProgram = ({ weekNumber, playerData }) => {
  const { t, direction } = useLanguage();
  const weekStructure = DAILY_PROGRESSIVE_STRUCTURE[`week${weekNumber}`];
  
  if (!weekStructure) return null;
  
  return (
    <Card className="bg-gradient-to-r from-green-50 to-blue-50 border-2 border-green-300 mb-6">
      <CardHeader>
        <CardTitle className="text-green-800 flex items-center">
          <Calendar className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
          Week {weekNumber}: {weekStructure.theme}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(weekStructure.daily_focus).map(([day, details]) => (
            <div key={day} className="bg-white p-4 rounded-lg border border-gray-200">
              <h4 className="font-bold text-gray-800 capitalize mb-2">{day}</h4>
              <div className="space-y-2">
                <p className="text-sm font-semibold text-blue-700">{details.focus}</p>
                <div className="flex justify-between items-center">
                  <Badge className={`text-xs ${
                    details.intensity === 'Very High' ? 'bg-red-100 text-red-800' :
                    details.intensity === 'High' ? 'bg-orange-100 text-orange-800' :
                    details.intensity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                    'bg-green-100 text-green-800'
                  }`}>
                    {details.intensity}
                  </Badge>
                  <span className="text-xs text-gray-600 flex items-center">
                    <Timer className="w-3 h-3 mr-1" />
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
  const { t, formatText, direction } = useLanguage();
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
      // Create a retest notification
      await axios.post(`${API}/notifications`, {
        player_id: playerId,
        title: "🔥 Retest Scheduled - Time to Show Your Progress!",
        message: "Your 4-week training cycle is complete. Time for reassessment to track your improvements!",
        notification_type: "retest",
        scheduled_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000) // 1 week from now
      });
      
      alert("Retest scheduled for next week! You'll receive a notification.");
    } catch (error) {
      console.error("Error scheduling retest:", error);
    }
  };

  // Performance Analysis with Handbook Standards
  const analyzePerformance = (playerData) => {
    if (!playerData || !playerData.age) return null;
    
    const age = parseInt(playerData.age);
    const ageCategory = getAgeCategory(age);
    const standards = YOUTH_HANDBOOK_STANDARDS[ageCategory];
    
    if (!standards) return null;
    
    const metrics = [
      'sprint_30m', 'yo_yo_test', 'vo2_max', 'vertical_jump', 'body_fat',
      'ball_control', 'passing_accuracy', 'dribbling_success', 'shooting_accuracy', 'defensive_duels'
    ];
    
    const weaknesses = [];
    const strengths = [];
    let overallScore = 0;
    let validMetrics = 0;
    
    metrics.forEach(metric => {
      const playerValue = parseFloat(playerData[metric]);
      if (!playerValue || !standards[metric]) return;
      
      const performance = evaluatePerformance(playerValue, metric, ageCategory);
      if (!performance) return;
      
      validMetrics++;
      
      // Score: excellent=4, good=3, average=2, poor=1
      const scoreMap = { excellent: 4, good: 3, average: 2, poor: 1 };
      overallScore += scoreMap[performance];
      
      if (performance === 'poor' || performance === 'average') {
        const target = standards[metric].good;
        weaknesses.push({
          metric,
          current: playerValue,
          target,
          performance,
          improvement: metric === 'sprint_30m' || metric === 'body_fat' ? 
            (playerValue - target).toFixed(2) : 
            (target - playerValue).toFixed(2)
        });
      } else if (performance === 'excellent' || performance === 'good') {
        strengths.push({
          metric,
          current: playerValue,
          performance
        });
      }
    });
    
    const averageScore = validMetrics > 0 ? (overallScore / validMetrics) : 0;
    
    return { 
      weaknesses: weaknesses.slice(0, 4), 
      strengths: strengths.slice(0, 4), 
      ageCategory, 
      age,
      overallScore: averageScore.toFixed(1)
    };
  };

  const performanceAnalysis = analyzePerformance(playerData);

  return (
    <div className="space-y-6">
      {/* Performance Benchmark Analysis */}
      {performanceAnalysis && (
        <Card className="bg-gradient-to-r from-blue-50 to-purple-50 border-2 border-blue-300">
          <CardHeader>
            <CardTitle className="text-blue-800 flex items-center justify-between">
              <div className="flex items-center">
                <BarChart3 className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
                {t('training.benchmarkTitle')}
              </div>
              <Badge className="bg-blue-100 text-blue-800 text-lg px-3 py-1">
                Overall Score: {performanceAnalysis.overallScore}/4.0
              </Badge>
            </CardTitle>
            <CardDescription>
              {formatText(t('training.ageGroup'), { 
                age: performanceAnalysis.age, 
                category: t(`common.${performanceAnalysis.ageCategory}`)
              })}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              {/* Current Status vs Ultimate Goals */}
              <div className="bg-gradient-to-r from-yellow-50 to-orange-50 p-4 rounded-lg border border-yellow-300">
                <h4 className="font-bold text-orange-800 mb-3 flex items-center">
                  <Target className="w-4 h-4 mr-2" />
                  Current Status vs Ultimate Goals
                </h4>
                <div className="space-y-3">
                  <div className="bg-white p-3 rounded border">
                    <h5 className="font-semibold text-yellow-700">Current Level</h5>
                    <p className="text-sm text-gray-600">
                      Overall performance score of {performanceAnalysis.overallScore}/4.0 for {t(`common.${performanceAnalysis.ageCategory}`)} category
                    </p>
                  </div>
                  <div className="bg-white p-3 rounded border">
                    <h5 className="font-semibold text-green-700">Ultimate Goal</h5>
                    <p className="text-sm text-gray-600">
                      Achieve 4.0/4.0 across all metrics to reach excellent/elite standards for your age group
                    </p>
                  </div>
                  <div className="bg-white p-3 rounded border">
                    <h5 className="font-semibold text-blue-700">Next Target</h5>
                    <p className="text-sm text-gray-600">
                      Focus on {performanceAnalysis.weaknesses.length > 0 ? 
                        `improving ${performanceAnalysis.weaknesses[0].metric.replace(/_/g, ' ')}` : 
                        'maintaining current performance levels'}
                    </p>
                  </div>
                </div>
              </div>

              {/* Action Plan */}
              <div className="bg-gradient-to-r from-green-50 to-blue-50 p-4 rounded-lg border border-green-300">
                <h4 className="font-bold text-green-800 mb-3 flex items-center">
                  <CheckCircle className="w-4 h-4 mr-2" />
                  Priority Training Focus
                </h4>
                {performanceAnalysis.weaknesses.length > 0 ? (
                  <div className="space-y-2">
                    {performanceAnalysis.weaknesses.slice(0, 3).map((weakness) => (
                      <div key={weakness.metric} className="bg-white p-2 rounded border">
                        <div className="font-semibold text-red-700 capitalize text-sm">
                          {weakness.metric.replace(/_/g, ' ')}
                        </div>
                        <div className="text-xs text-gray-600">
                          Current: {weakness.current} → Target: {weakness.target}
                          <Badge className="ml-2 bg-red-100 text-red-800 text-xs">
                            {weakness.performance}
                          </Badge>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : (
                  <p className="text-green-600">Excellent! All metrics are performing well. Focus on maintaining standards.</p>
                )}
              </div>
            </div>
            
            {/* Retest Button */}
            <div className="mt-6 text-center">
              <Button 
                onClick={scheduleRetest}
                className="bg-gradient-to-r from-purple-600 to-blue-600 hover:from-purple-700 hover:to-blue-700 text-white font-bold px-6 py-3"
              >
                <RefreshCw className="w-4 h-4 mr-2" />
                {t('training.retestButton')}
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Daily Progressive Training Display */}
      <Card className="bg-gradient-to-r from-orange-50 to-yellow-50 border-2 border-orange-300">
        <CardHeader>
          <CardTitle className="text-orange-800 flex items-center justify-between">
            <div className="flex items-center">
              <Calendar className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
              {t('training.dailyProgression')}
            </div>
            <Button
              variant="outline"
              onClick={() => setShowDailyProgression(!showDailyProgression)}
              className="border-orange-400 text-orange-700 hover:bg-orange-100"
            >
              {showDailyProgression ? 'Hide' : 'Show'} Daily Plan
            </Button>
          </CardTitle>
        </CardHeader>
        {showDailyProgression && (
          <CardContent>
            <div className="mb-4">
              <Label className="text-orange-700 font-semibold mb-2 block">Select Week:</Label>
              <Select value={selectedWeek.toString()} onValueChange={(value) => setSelectedWeek(parseInt(value))}>
                <SelectTrigger className="w-48 border-orange-400">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="1">Week 1: Foundation Building</SelectItem>
                  <SelectItem value="2">Week 2: Skill Development</SelectItem>
                  <SelectItem value="3">Week 3: Performance Enhancement</SelectItem>
                  <SelectItem value="4">Week 4: Assessment & Refinement</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <DailyProgressiveProgram weekNumber={selectedWeek} playerData={playerData} />
          </CardContent>
        )}
      </Card>

      {/* Training Program Generation */}
      <div className="flex flex-wrap gap-4 mb-6">
        <Button 
          onClick={() => generateProgram("AI_Generated")} 
          disabled={isGenerating}
          className="bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white font-bold"
        >
          <Zap className="w-4 h-4 mr-2" />
          {t('training.generateAI')}
        </Button>
        <Button 
          onClick={() => generateProgram("Ronaldo_Template")} 
          disabled={isGenerating}
          className="bg-gradient-to-r from-yellow-600 to-red-600 hover:from-yellow-700 hover:to-red-700 text-white font-bold"
        >
          <Crown className="w-4 h-4 mr-2" />
          {t('training.generateRonaldo')}
        </Button>
      </div>

      {/* Generated Programs */}
      {programs.map(program => (
        <Card key={program.id} className="bg-gradient-to-br from-green-50 via-blue-50 to-purple-50 border-2 border-green-300">
          <CardHeader>
            <CardTitle className="text-green-800 flex items-center">
              <Trophy className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
              {program.program_type} - {playerName}
            </CardTitle>
            <CardDescription>
              Created: {new Date(program.created_at).toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none" dir={direction}>
              <div className="whitespace-pre-wrap text-gray-700">
                {program.program_content}
              </div>
            </div>
            
            {/* Weekly Schedule */}
            {program.weekly_schedule && Object.keys(program.weekly_schedule).length > 0 && (
              <div className="mt-6">
                <h4 className="text-lg font-bold text-green-800 mb-3">{t('training.weeklyStructure')}</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Object.entries(program.weekly_schedule).map(([day, activity]) => (
                    <div key={day} className="bg-white p-3 rounded-lg border border-green-200">
                      <div className="font-semibold text-green-700 capitalize">{day}</div>
                      <div className="text-sm text-gray-600" dir={direction}>{activity}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Milestones */}
            {program.milestones && program.milestones.length > 0 && (
              <div className="mt-6">
                <h4 className="text-lg font-bold text-purple-800 mb-3">Milestones & Rewards</h4>
                <div className="space-y-2">
                  {program.milestones.map((milestone, index) => (
                    <div key={index} className="bg-white p-3 rounded-lg border border-purple-200 flex items-center justify-between">
                      <div>
                        <span className="font-semibold text-purple-700">Week {milestone.week}:</span>
                        <span className="text-gray-700 ml-2" dir={direction}>{milestone.target}</span>
                      </div>
                      <Badge className="bg-yellow-100 text-yellow-800 flex items-center">
                        <Coins className="w-3 h-3 mr-1" />
                        {milestone.coins}
                      </Badge>
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

// Main App continues with existing components...
// [Rest of the App component remains the same as in the original file]
// Including ProgressTracking, VoiceNotes, TrophyDisplay, GroupTraining, etc.

const App = () => {
  return (
    <LanguageProvider>
      <BrowserRouter>
        <div className="min-h-screen bg-gradient-to-br from-orange-100 via-red-50 to-yellow-100">
          {/* Navigation and other components remain the same */}
          <Routes>
            <Route path="/" element={<MainDashboard />} />
          </Routes>
        </div>
      </BrowserRouter>
    </LanguageProvider>
  );
};

// MainDashboard component with all tabs remains the same...
const MainDashboard = () => {
  const { t, direction, toggleLanguage } = useLanguage();
  const [currentPlayer, setCurrentPlayer] = useState(null);
  const [activeTab, setActiveTab] = useState("assessment");

  const handleAssessmentCreated = (assessment) => {
    setCurrentPlayer(assessment);
    setActiveTab("training");
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="text-center mb-8 relative">
        <Button
          onClick={toggleLanguage}
          variant="outline"
          size="sm"
          className="absolute top-0 right-0 border-orange-400 text-orange-700 hover:bg-orange-100"
        >
          <Languages className="w-4 h-4 mr-2" />
          {direction === 'rtl' ? 'English' : 'العربية'}
        </Button>
        
        <h1 className="text-6xl font-bold bg-gradient-to-r from-orange-600 via-red-600 to-yellow-600 bg-clip-text text-transparent mb-2">
          {t('app.title')}
        </h1>
        <p className="text-xl text-orange-700 font-semibold">{t('app.subtitle')}</p>
      </div>

      {/* Main Content */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8 bg-gradient-to-r from-orange-200 to-red-200 border-2 border-orange-400">
          <TabsTrigger value="assessment" className="data-[state=active]:bg-orange-500 data-[state=active]:text-white font-bold">
            <Target className="w-4 h-4 mr-2" />
            {t('nav.assessment')}
          </TabsTrigger>
          <TabsTrigger value="training" className="data-[state=active]:bg-red-500 data-[state=active]:text-white font-bold">
            <Zap className="w-4 h-4 mr-2" />
            {t('nav.training')}
          </TabsTrigger>
          <TabsTrigger value="progress" className="data-[state=active]:bg-yellow-500 data-[state=active]:text-white font-bold">
            <TrendingUp className="w-4 h-4 mr-2" />
            {t('nav.progress')}
          </TabsTrigger>
          <TabsTrigger value="voice" className="data-[state=active]:bg-green-500 data-[state=active]:text-white font-bold">
            <Mic className="w-4 h-4 mr-2" />
            {t('nav.voice')}
          </TabsTrigger>
          <TabsTrigger value="trophies" className="data-[state=active]:bg-purple-500 data-[state=active]:text-white font-bold">
            <Trophy className="w-4 h-4 mr-2" />
            {t('nav.trophies')}
          </TabsTrigger>
          <TabsTrigger value="group" className="data-[state=active]:bg-pink-500 data-[state=active]:text-white font-bold">
            <Users className="w-4 h-4 mr-2" />
            {t('nav.group')}
          </TabsTrigger>
          <TabsTrigger value="highlights" className="data-[state=active]:bg-indigo-500 data-[state=active]:text-white font-bold">
            <Star className="w-4 h-4 mr-2" />
            {t('nav.highlights')}
          </TabsTrigger>
          <TabsTrigger value="body" className="data-[state=active]:bg-cyan-500 data-[state=active]:text-white font-bold">
            <Activity className="w-4 h-4 mr-2" />
            {t('nav.body')}
          </TabsTrigger>
        </TabsList>

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
            <Card className="text-center p-8">
              <CardContent>
                <Target className="w-16 h-16 mx-auto mb-4 text-gray-400" />
                <h3 className="text-xl font-bold text-gray-600 mb-2">Complete Assessment First</h3>
                <p className="text-gray-500">Create your fire boy assessment to unlock personalized training programs!</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Other tab contents remain the same */}
        <TabsContent value="progress">
          <Card>
            <CardContent className="p-8 text-center">
              <TrendingUp className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-bold text-gray-600">Progress Tracking Coming Soon</h3>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="voice">
          <Card>
            <CardContent className="p-8 text-center">
              <Mic className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-bold text-gray-600">Voice Notes Coming Soon</h3>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="trophies">
          <Card>
            <CardContent className="p-8 text-center">
              <Trophy className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-bold text-gray-600">Trophies Coming Soon</h3>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="group">
          <Card>
            <CardContent className="p-8 text-center">
              <Users className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-bold text-gray-600">Group Training Coming Soon</h3>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="highlights">
          <Card>
            <CardContent className="p-8 text-center">
              <Star className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-bold text-gray-600">Player Highlights Coming Soon</h3>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="body">
          <Card>
            <CardContent className="p-8 text-center">
              <Activity className="w-16 h-16 mx-auto mb-4 text-gray-400" />
              <h3 className="text-xl font-bold text-gray-600">Body & Fitness Coming Soon</h3>
            </CardContent>
          </Card>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default App;