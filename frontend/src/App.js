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

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Daily Progressive Training Structure
const DAILY_PROGRESSIVE_STRUCTURE = {
  week1: {
    theme: "Elite Foundation Building",
    daily_focus: {
      monday: { focus: "Royal Speed Foundation", intensity: "Medium", duration: 60 },
      tuesday: { focus: "Elite Ball Control", intensity: "High", duration: 90 },
      wednesday: { focus: "Recovery & Flexibility", intensity: "Low", duration: 45 },
      thursday: { focus: "Tactical Awareness", intensity: "Medium", duration: 75 },
      friday: { focus: "Precision Shooting", intensity: "High", duration: 60 },
      saturday: { focus: "Match Simulation", intensity: "High", duration: 90 },
      sunday: { focus: "Active Recovery", intensity: "Low", duration: 30 }
    }
  },
  week2: {
    theme: "Skill Mastery Development",
    daily_focus: {
      monday: { focus: "Explosive Speed Training", intensity: "High", duration: 60 },
      tuesday: { focus: "Advanced Technical Skills", intensity: "High", duration: 90 },
      wednesday: { focus: "Elite Tactical Play", intensity: "Medium", duration: 75 },
      thursday: { focus: "Competition Agility", intensity: "High", duration: 75 },
      friday: { focus: "Clinical Finishing", intensity: "High", duration: 60 },
      saturday: { focus: "Elite Match Play", intensity: "High", duration: 90 },
      sunday: { focus: "Mental Training", intensity: "Low", duration: 45 }
    }
  },
  week3: {
    theme: "Performance Maximization",
    daily_focus: {
      monday: { focus: "Championship Speed", intensity: "Very High", duration: 60 },
      tuesday: { focus: "Elite 1v1 Mastery", intensity: "High", duration: 90 },
      wednesday: { focus: "Tactical Intelligence", intensity: "Medium", duration: 75 },
      thursday: { focus: "Pro-Level Agility", intensity: "High", duration: 75 },
      friday: { focus: "Elite Power Shooting", intensity: "Very High", duration: 60 },
      saturday: { focus: "Championship Matches", intensity: "Very High", duration: 90 },
      sunday: { focus: "Elite Recovery", intensity: "Low", duration: 45 }
    }
  },
  week4: {
    theme: "Assessment & Elite Progression",
    daily_focus: {
      monday: { focus: "Speed Assessment", intensity: "High", duration: 60 },
      tuesday: { focus: "Technical Evaluation", intensity: "High", duration: 90 },
      wednesday: { focus: "Tactical Assessment", intensity: "Medium", duration: 75 },
      thursday: { focus: "Agility Testing", intensity: "High", duration: 75 },
      friday: { focus: "Shooting Evaluation", intensity: "High", duration: 60 },
      saturday: { focus: "Performance Review", intensity: "Medium", duration: 60 },
      sunday: { focus: "Next Level Planning", intensity: "Low", duration: 30 }
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
      'app.subtitle': 'Elite Soccer Training Tracker',
      'nav.assessment': 'Assessment',
      'nav.training': 'Training Programs',
      'nav.progress': 'Progress Tracking',
      'nav.voice': 'Voice Notes',
      'nav.trophies': 'Trophies & Achievements',
      'nav.group': 'Group Training',
      'nav.highlights': 'Player Highlights',
      'nav.body': 'Body & Fitness',
      'assessment.title': 'Elite Fire Boy Assessment 🔥',
      'assessment.subtitle': 'Professional Elite Training Framework',
      'common.excellent': 'Excellent',
      'common.good': 'Good',
      'common.average': 'Average',
      'common.poor': 'Needs Improvement'
    },
    ar: {
      'app.title': 'يويو الفتى الناري ⚽🔥',
      'app.subtitle': 'متتبع التدريب النخبوي لكرة القدم',
      'nav.assessment': 'التقييم',
      'nav.training': 'برامج التدريب',
      'nav.progress': 'تتبع التقدم',
      'nav.voice': 'الملاحظات الصوتية',
      'nav.trophies': 'الكؤوس والإنجازات',
      'nav.group': 'التدريب الجماعي',
      'nav.highlights': 'أبرز اللاعبين',
      'nav.body': 'الجسم واللياقة',
      'assessment.title': 'تقييم الفتى الناري النخبوي 🔥',
      'assessment.subtitle': 'إطار التدريب النخبوي المحترف',
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
      <Card className="elite-card-gradient border-2 border-royal-gold/30">
        <CardHeader>
          <CardTitle className="text-royal-gold flex items-center text-lg">
            <Crown className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
            Elite Performance Standards Guide
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 performance-card rounded-lg">
              <Crown className="w-8 h-8 mx-auto mb-2 text-royal-gold" />
              <h4 className="font-bold text-royal-gold">{t('common.excellent')}</h4>
              <p className="text-sm text-elite-white/70">Elite/International level</p>
            </div>
            <div className="text-center p-4 performance-card rounded-lg">
              <Award className="w-8 h-8 mx-auto mb-2 text-royal-blue" />
              <h4 className="font-bold text-royal-blue">{t('common.good')}</h4>
              <p className="text-sm text-elite-white/70">High competitive standard</p>
            </div>
            <div className="text-center p-4 performance-card rounded-lg">
              <Star className="w-8 h-8 mx-auto mb-2 text-elite-silver" />
              <h4 className="font-bold text-elite-silver">{t('common.average')}</h4>
              <p className="text-sm text-elite-white/70">Solid club level</p>
            </div>
            <div className="text-center p-4 performance-card rounded-lg">
              <Target className="w-8 h-8 mx-auto mb-2 text-royal-red" />
              <h4 className="font-bold text-royal-red">{t('common.poor')}</h4>
              <p className="text-sm text-elite-white/70">Development needed</p>
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
        className="text-xs text-royal-gold hover:text-royal-gold-light elite-button"
      >
        <HelpCircle className="w-3 h-3 mr-1" />
        {isVisible ? 'Hide Explanation' : 'Show Explanation'}
      </Button>
      
      {isVisible && (
        <div className="mt-2 p-3 elite-card-gradient rounded-lg border border-royal-gold/30">
          <h5 className="font-bold text-royal-gold mb-1">{explanation.title}</h5>
          <p className="text-sm text-elite-white/90 mb-2" dir={direction}>{explanation.description}</p>
          <p className="text-xs text-royal-blue mb-1"><strong>Why it matters:</strong> {explanation.importance}</p>
          <p className="text-xs text-royal-red mb-1"><strong>Tips:</strong> {explanation.tips}</p>
          <p className="text-xs text-royal-gold"><strong>Scoring:</strong> {explanation.scoring}</p>
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
      excellent: 'border-royal-gold bg-royal-gold/20',
      good: 'border-royal-blue bg-royal-blue/20',
      average: 'border-elite-silver bg-elite-silver/20',
      poor: 'border-royal-red bg-royal-red/20'
    };
    
    return colors[performance];
  };

  return (
    <div>
      <StandardsLegend />
      <Card className="max-w-6xl mx-auto elite-card-gradient border-2 border-royal-gold/30 fire-glow">
        <CardHeader className="text-center">
          <CardTitle className="text-4xl font-bold elite-royal-gradient bg-clip-text text-transparent">
            {t('assessment.title')}
          </CardTitle>
          <CardDescription className="text-royal-gold text-lg font-semibold">
            {t('assessment.subtitle')}
          </CardDescription>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-8">
            {/* Basic Info */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div>
                <Label htmlFor="player_name" className="text-royal-gold font-bold flex items-center">
                  <Flame className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-4 h-4`} />
                  Player Name
                </Label>
                <Input
                  id="player_name"
                  name="player_name"
                  value={formData.player_name}
                  onChange={handleChange}
                  required
                  className="elite-input"
                  dir={direction}
                  placeholder="Enter elite player name"
                />
              </div>
              <div>
                <Label htmlFor="age" className="text-royal-gold font-bold flex items-center">
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
                  className="elite-input"
                  placeholder="Your age"
                />
                {formData.age && (
                  <Badge className="mt-1 status-good">
                    Age Group: {getAgeCategory(parseInt(formData.age))}
                  </Badge>
                )}
              </div>
              <div>
                <Label htmlFor="position" className="text-royal-gold font-bold flex items-center">
                  <Target className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-4 h-4`} />
                  Position
                </Label>
                <Select onValueChange={(value) => setFormData({...formData, position: value})}>
                  <SelectTrigger className="elite-input">
                    <SelectValue placeholder="Select your position" />
                  </SelectTrigger>
                  <SelectContent className="elite-card-gradient border border-royal-gold/30">
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
            <div className="performance-card p-6 rounded-lg border-2 border-royal-red/30">
              <h3 className="text-xl font-bold text-royal-red mb-4 flex items-center">
                <Dumbbell className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} text-royal-gold`} />
                Physical Performance Tests (20% Weight) 💪
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="sprint_30m" className="text-royal-red font-semibold">30m Sprint (seconds)</Label>
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
                    className={`elite-input ${getFieldValidation('sprint_30m', formData.sprint_30m, formData.age) || ''}`}
                    placeholder="e.g., 4.2"
                  />
                  <FieldExplanation 
                    fieldName="sprint_30m" 
                    isVisible={explanationVisibility.sprint_30m}
                    onToggle={() => toggleExplanation('sprint_30m')}
                  />
                </div>
                <div>
                  <Label htmlFor="yo_yo_test" className="text-royal-red font-semibold">Yo-Yo Test (meters)</Label>
                  <Input
                    id="yo_yo_test"
                    name="yo_yo_test"
                    type="number"
                    min="400"
                    max="3000"
                    value={formData.yo_yo_test}
                    onChange={handleChange}
                    required
                    className={`elite-input ${getFieldValidation('yo_yo_test', formData.yo_yo_test, formData.age) || ''}`}
                    placeholder="e.g., 1600"
                  />
                  <FieldExplanation 
                    fieldName="yo_yo_test" 
                    isVisible={explanationVisibility.yo_yo_test}
                    onToggle={() => toggleExplanation('yo_yo_test')}
                  />
                </div>
                <div>
                  <Label htmlFor="vo2_max" className="text-royal-red font-semibold">VO2 Max (ml/kg/min)</Label>
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
                    className={`elite-input ${getFieldValidation('vo2_max', formData.vo2_max, formData.age) || ''}`}
                    placeholder="e.g., 58.5"
                  />
                  <FieldExplanation 
                    fieldName="vo2_max" 
                    isVisible={explanationVisibility.vo2_max}
                    onToggle={() => toggleExplanation('vo2_max')}
                  />
                </div>
                <div>
                  <Label htmlFor="vertical_jump" className="text-royal-red font-semibold">Vertical Jump (cm)</Label>
                  <Input
                    id="vertical_jump"
                    name="vertical_jump"
                    type="number"
                    min="20"
                    max="80"
                    value={formData.vertical_jump}
                    onChange={handleChange}
                    required
                    className={`elite-input ${getFieldValidation('vertical_jump', formData.vertical_jump, formData.age) || ''}`}
                    placeholder="e.g., 55"
                  />
                  <FieldExplanation 
                    fieldName="vertical_jump" 
                    isVisible={explanationVisibility.vertical_jump}
                    onToggle={() => toggleExplanation('vertical_jump')}
                  />
                </div>
                <div>
                  <Label htmlFor="body_fat" className="text-royal-red font-semibold">Body Fat (%)</Label>
                  <Input
                    id="body_fat"
                    name="body_fat"
                    type="number"
                    step="0.1"
                    min="5"
                    max="30"
                    value={formData.body_fat}
                    onChange={handleRange}
                    required
                    className={`elite-input ${getFieldValidation('body_fat', formData.body_fat, formData.age) || ''}`}
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
            <div className="performance-card p-6 rounded-lg border-2 border-royal-blue/30">
              <h3 className="text-xl font-bold text-royal-blue mb-4 flex items-center">
                <Gamepad2 className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} text-royal-gold`} />
                Technical Skills Assessment (40% Weight) ⚽✨
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="ball_control" className="text-royal-blue font-semibold">Ball Control (1-5 scale)</Label>
                  <Input
                    id="ball_control"
                    name="ball_control"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.ball_control}
                    onChange={handleChange}
                    required
                    className={`elite-input ${getFieldValidation('ball_control', formData.ball_control, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="ball_control" 
                    isVisible={explanationVisibility.ball_control}
                    onToggle={() => toggleExplanation('ball_control')}
                  />
                </div>
                <div>
                  <Label htmlFor="passing_accuracy" className="text-royal-blue font-semibold">Passing Accuracy (%)</Label>
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
                    className={`elite-input ${getFieldValidation('passing_accuracy', formData.passing_accuracy, formData.age) || ''}`}
                    placeholder="e.g., 85.5"
                  />
                  <FieldExplanation 
                    fieldName="passing_accuracy" 
                    isVisible={explanationVisibility.passing_accuracy}
                    onToggle={() => toggleExplanation('passing_accuracy')}
                  />
                </div>
                <div>
                  <Label htmlFor="dribbling_success" className="text-royal-blue font-semibold">Dribbling Success (%)</Label>
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
                    className={`elite-input ${getFieldValidation('dribbling_success', formData.dribbling_success, formData.age) || ''}`}
                    placeholder="e.g., 65.0"
                  />
                  <FieldExplanation 
                    fieldName="dribbling_success" 
                    isVisible={explanationVisibility.dribbling_success}
                    onToggle={() => toggleExplanation('dribbling_success')}
                  />
                </div>
                <div>
                  <Label htmlFor="shooting_accuracy" className="text-royal-blue font-semibold">Shooting Accuracy (%)</Label>
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
                    className={`elite-input ${getFieldValidation('shooting_accuracy', formData.shooting_accuracy, formData.age) || ''}`}
                    placeholder="e.g., 72.5"
                  />
                  <FieldExplanation 
                    fieldName="shooting_accuracy" 
                    isVisible={explanationVisibility.shooting_accuracy}
                    onToggle={() => toggleExplanation('shooting_accuracy')}
                  />
                </div>
                <div>
                  <Label htmlFor="defensive_duels" className="text-royal-blue font-semibold">Defensive Duels (%)</Label>
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
                    className={`elite-input ${getFieldValidation('defensive_duels', formData.defensive_duels, formData.age) || ''}`}
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
            <div className="performance-card p-6 rounded-lg border-2 border-royal-gold/30">
              <h3 className="text-xl font-bold text-royal-gold mb-4 flex items-center">
                <Brain className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} text-royal-blue`} />
                Tactical Awareness Assessment (30% Weight) 🧠⚽
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div>
                  <Label htmlFor="game_intelligence" className="text-royal-gold font-semibold">Game Intelligence (1-5)</Label>
                  <Input
                    id="game_intelligence"
                    name="game_intelligence"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.game_intelligence}
                    onChange={handleChange}
                    required
                    className={`elite-input ${getFieldValidation('game_intelligence', formData.game_intelligence, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="game_intelligence" 
                    isVisible={explanationVisibility.game_intelligence}
                    onToggle={() => toggleExplanation('game_intelligence')}
                  />
                </div>
                <div>
                  <Label htmlFor="positioning" className="text-royal-gold font-semibold">Positioning (1-5)</Label>
                  <Input
                    id="positioning"
                    name="positioning"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.positioning}
                    onChange={handleChange}
                    required
                    className={`elite-input ${getFieldValidation('positioning', formData.positioning, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="positioning" 
                    isVisible={explanationVisibility.positioning}
                    onToggle={() => toggleExplanation('positioning')}
                  />
                </div>
                <div>
                  <Label htmlFor="decision_making" className="text-royal-gold font-semibold">Decision Making (1-5)</Label>
                  <Input
                    id="decision_making"
                    name="decision_making"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.decision_making}
                    onChange={handleChange}
                    required
                    className={`elite-input ${getFieldValidation('decision_making', formData.decision_making, formData.age) || ''}`}
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
            <div className="performance-card p-6 rounded-lg border-2 border-elite-silver/30">
              <h3 className="text-xl font-bold text-elite-silver mb-4 flex items-center">
                <Heart className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} text-royal-red`} />
                Psychological Traits Assessment (10% Weight) 💚🧠
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <Label htmlFor="coachability" className="text-elite-silver font-semibold">Coachability (1-5)</Label>
                  <Input
                    id="coachability"
                    name="coachability"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.coachability}
                    onChange={handleChange}
                    required
                    className={`elite-input ${getFieldValidation('coachability', formData.coachability, formData.age) || ''}`}
                    placeholder="1-5 scale"
                  />
                  <FieldExplanation 
                    fieldName="coachability" 
                    isVisible={explanationVisibility.coachability}
                    onToggle={() => toggleExplanation('coachability')}
                  />
                </div>
                <div>
                  <Label htmlFor="mental_toughness" className="text-elite-silver font-semibold">Mental Toughness (1-5)</Label>
                  <Input
                    id="mental_toughness"
                    name="mental_toughness"
                    type="number"
                    min="1"
                    max="5"
                    value={formData.mental_toughness}
                    onChange={handleChange}
                    required
                    className={`elite-input ${getFieldValidation('mental_toughness', formData.mental_toughness, formData.age) || ''}`}
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
              className="w-full elite-button py-4 px-8 rounded-lg text-xl font-bold"
            >
              {isLoading ? 'Creating Elite Assessment...' : 'Create Elite Fire Boy Assessment 🔥'}
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
    <Card className="elite-card-gradient border-2 border-royal-blue/30 mb-6">
      <CardHeader>
        <CardTitle className="text-royal-blue flex items-center">
          <Calendar className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
          Week {weekNumber}: {weekStructure.theme}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {Object.entries(weekStructure.daily_focus).map(([day, details]) => (
            <div key={day} className="performance-card p-4 rounded-lg">
              <h4 className="font-bold text-royal-gold capitalize mb-2">{day}</h4>
              <div className="space-y-2">
                <p className="text-sm font-semibold text-royal-blue">{details.focus}</p>
                <div className="flex justify-between items-center">
                  <Badge className={`text-xs ${
                    details.intensity === 'Very High' ? 'status-excellent' :
                    details.intensity === 'High' ? 'status-good' :
                    details.intensity === 'Medium' ? 'status-average' :
                    'bg-royal-blue/20 text-royal-blue'
                  }`}>
                    {details.intensity}
                  </Badge>
                  <span className="text-xs text-elite-white/70 flex items-center">
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
      await axios.post(`${API}/notifications`, {
        player_id: playerId,
        title: "🔥 Elite Retest Scheduled - Time to Show Your Elite Progress!",
        message: "Your elite assessment cycle is complete. Time for reassessment to track your elite improvements!",
        notification_type: "retest",
        scheduled_at: new Date(Date.now() + 7 * 24 * 60 * 60 * 1000)
      });
      
      alert("Elite retest scheduled for next week! You'll receive a notification.");
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
      <Card className="elite-card-gradient border-2 border-royal-gold/30">
        <CardHeader>
          <CardTitle className="text-royal-gold flex items-center justify-between">
            <div className="flex items-center">
              <Calendar className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
              Elite Daily Progression Plan
            </div>
            <Button
              variant="outline"
              onClick={() => setShowDailyProgression(!showDailyProgression)}
              className="elite-button"
            >
              {showDailyProgression ? 'Hide' : 'Show'} Daily Plan
            </Button>
          </CardTitle>
        </CardHeader>
        {showDailyProgression && (
          <CardContent>
            <div className="mb-4">
              <Label className="text-royal-gold font-semibold mb-2 block">Select Week:</Label>
              <Select value={selectedWeek.toString()} onValueChange={(value) => setSelectedWeek(parseInt(value))}>
                <SelectTrigger className="w-48 elite-input">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent className="elite-card-gradient border border-royal-gold/30">
                  <SelectItem value="1">Week 1: Elite Foundation Building</SelectItem>
                  <SelectItem value="2">Week 2: Skill Mastery Development</SelectItem>
                  <SelectItem value="3">Week 3: Performance Maximization</SelectItem>
                  <SelectItem value="4">Week 4: Assessment & Elite Progression</SelectItem>
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
          className="elite-button"
        >
          <Zap className="w-4 h-4 mr-2" />
          Generate Elite AI Program
        </Button>
        <Button 
          onClick={() => generateProgram("Ronaldo_Template")} 
          disabled={isGenerating}
          className="elite-button"
        >
          <Crown className="w-4 h-4 mr-2" />
          Elite Ronaldo Template
        </Button>
        <Button 
          onClick={scheduleRetest}
          className="elite-button"
        >
          <RefreshCw className="w-4 h-4 mr-2" />
          Schedule Elite Retest
        </Button>
      </div>

      {/* Generated Programs */}
      {programs.map(program => (
        <Card key={program.id} className="elite-card-gradient border-2 border-royal-blue/30">
          <CardHeader>
            <CardTitle className="text-royal-blue flex items-center">
              <Trophy className={`${direction === 'rtl' ? 'ml-2' : 'mr-2'} w-5 h-5`} />
              {program.program_type} - {playerName}
            </CardTitle>
            <CardDescription className="text-elite-white/70">
              Created: {new Date(program.created_at).toLocaleDateString()}
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="prose prose-sm max-w-none text-elite-white" dir={direction}>
              <div className="whitespace-pre-wrap">
                {program.program_content}
              </div>
            </div>
            
            {/* Weekly Schedule */}
            {program.weekly_schedule && Object.keys(program.weekly_schedule).length > 0 && (
              <div className="mt-6">
                <h4 className="text-lg font-bold text-royal-gold mb-3">Elite Weekly Structure</h4>
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-3">
                  {Object.entries(program.weekly_schedule).map(([day, activity]) => (
                    <div key={day} className="performance-card p-3 rounded-lg">
                      <div className="font-semibold text-royal-gold capitalize">{day}</div>
                      <div className="text-sm text-elite-white/80" dir={direction}>{activity}</div>
                    </div>
                  ))}
                </div>
              </div>
            )}
            
            {/* Milestones */}
            {program.milestones && program.milestones.length > 0 && (
              <div className="mt-6">
                <h4 className="text-lg font-bold text-royal-red mb-3">Elite Milestones & Rewards</h4>
                <div className="space-y-2">
                  {program.milestones.map((milestone, index) => (
                    <div key={index} className="performance-card p-3 rounded-lg flex items-center justify-between">
                      <div>
                        <span className="font-semibold text-royal-gold">Week {milestone.week}:</span>
                        <span className="text-elite-white ml-2" dir={direction}>{milestone.target}</span>
                      </div>
                      <Badge className="status-excellent flex items-center">
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

// MainDashboard component with elite royal theme
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
      {/* Elite Header */}
      <div className="text-center mb-8 relative">
        <Button
          onClick={toggleLanguage}
          variant="outline"
          size="sm"
          className="absolute top-0 right-0 elite-button"
        >
          <Languages className="w-4 h-4 mr-2" />
          {direction === 'rtl' ? 'English' : 'العربية'}
        </Button>
        
        <h1 className="text-6xl font-bold elite-royal-gradient bg-clip-text text-transparent mb-2">
          {t('app.title')}
        </h1>
        <p className="text-xl text-royal-gold font-semibold">{t('app.subtitle')}</p>
      </div>

      {/* Elite Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="w-full">
        <TabsList className="grid w-full grid-cols-4 lg:grid-cols-8 mb-8">
          <TabsTrigger value="assessment" className="elite-tab data-[state=active]:elite-tab">
            <Target className="w-4 h-4 mr-2" />
            Assessment
          </TabsTrigger>
          <TabsTrigger value="training" className="elite-tab">
            <Zap className="w-4 h-4 mr-2" />
            Training
          </TabsTrigger>
          <TabsTrigger value="progress" className="elite-tab">
            <TrendingUp className="w-4 h-4 mr-2" />
            Progress
          </TabsTrigger>
          <TabsTrigger value="voice" className="elite-tab">
            <Mic className="w-4 h-4 mr-2" />
            Voice Notes
          </TabsTrigger>
          <TabsTrigger value="trophies" className="elite-tab">
            <Trophy className="w-4 h-4 mr-2" />
            Trophies
          </TabsTrigger>
          <TabsTrigger value="group" className="elite-tab">
            <Users className="w-4 h-4 mr-2" />
            Group
          </TabsTrigger>
          <TabsTrigger value="highlights" className="elite-tab">
            <Star className="w-4 h-4 mr-2" />
            Highlights
          </TabsTrigger>
          <TabsTrigger value="body" className="elite-tab">
            <Activity className="w-4 h-4 mr-2" />
            Body & Fitness
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
            <Card className="elite-card-gradient text-center p-8 border-2 border-royal-gold/30">
              <CardContent>
                <Target className="w-16 h-16 mx-auto mb-4 text-royal-gold" />
                <h3 className="text-xl font-bold text-royal-gold mb-2">Complete Elite Assessment First</h3>
                <p className="text-elite-white/70">Create your elite fire boy assessment to unlock personalized training programs!</p>
              </CardContent>
            </Card>
          )}
        </TabsContent>

        <TabsContent value="progress">
          {currentPlayer ? (
            <ProgressTracker playerData={currentPlayer} />
          ) : (
            <ComingSoon 
              title="Elite Progress Tracking"
              description="Advanced analytics and progress visualization for elite performance monitoring"
              icon={TrendingUp}
              features={[
                "Real-time performance metrics",
                "Progress comparison charts", 
                "Goal tracking system",
                "Performance predictions"
              ]}
              estimatedRelease="Q1 2024"
              priority="high"
            />
          )}
        </TabsContent>

        <TabsContent value="voice">
          <ComingSoon 
            title="Elite Voice Notes"
            description="AI-powered voice analysis and coaching feedback system"
            icon={Headphones}
            features={[
              "Voice-to-text coaching notes",
              "AI performance analysis",
              "Multilingual support",
              "Voice command training"
            ]}
            estimatedRelease="Q2 2024"
            priority="medium"
          />
        </TabsContent>

        <TabsContent value="trophies">
          <ComingSoon 
            title="Elite Trophies & Achievements"
            description="Comprehensive achievement system with elite badges and rewards"
            icon={Crown}
            features={[
              "Elite achievement badges",
              "Performance milestones",
              "Reward system",
              "Leaderboards"
            ]}
            estimatedRelease="Q1 2024"
            priority="high"
          />
        </TabsContent>

        <TabsContent value="group">
          <ComingSoon 
            title="Elite Group Training"
            description="Team coordination and group training management system"
            icon={Shield}
            features={[
              "Team management",
              "Group challenges",
              "Coach dashboard",
              "Team analytics"
            ]}
            estimatedRelease="Q2 2024"
            priority="medium"
          />
        </TabsContent>

        <TabsContent value="highlights">
          <ComingSoon 
            title="Elite Player Highlights"
            description="AI-powered performance highlights and video analysis"
            icon={Camera}
            features={[
              "Performance video analysis",
              "Skill highlight reels",
              "Improvement suggestions",
              "Share achievements"
            ]}
            estimatedRelease="Q3 2024"
            priority="low"
          />
        </TabsContent>

        <TabsContent value="body">
          <ComingSoon 
            title="Elite Body & Fitness Tracker"
            description="Comprehensive fitness monitoring and body composition analysis"
            icon={Activity}
            features={[
              "Body composition tracking",
              "Fitness goal setting",
              "Nutrition planning",
              "Recovery monitoring"
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