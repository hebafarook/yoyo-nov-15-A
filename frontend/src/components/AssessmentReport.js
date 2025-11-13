import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Textarea } from './ui/textarea';
import { Label } from './ui/label';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Printer, Download, Save, Bookmark, MessageSquare } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Interactive Gauge Chart Component with Animation
const GaugeChart = ({ value, label, max = 100, unit = '', description = '', isLowerBetter = false }) => {
  const [animatedValue, setAnimatedValue] = useState(0);
  const [isHovered, setIsHovered] = useState(false);
  
  // Ensure value is a number
  const numericValue = Number(value) || 0;
  const maxValue = Number(max) || 100;
  
  // Calculate percentage (0-100)
  let percentage = Math.min(100, Math.max(0, (numericValue / maxValue) * 100));
  
  // For "lower is better" metrics (like sprint times), invert the percentage for color coding
  const displayPercentage = isLowerBetter ? Math.max(0, 100 - percentage) : percentage;
  
  // Animate the gauge on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedValue(percentage);
    }, 100);
    return () => clearTimeout(timer);
  }, [percentage]);
  
  // Determine color based on display percentage
  let color, colorName;
  if (displayPercentage >= 75) {
    color = '#16a34a'; // green
    colorName = 'Excellent';
  } else if (displayPercentage >= 50) {
    color = '#eab308'; // yellow/orange
    colorName = 'Good';
  } else {
    color = '#ef4444'; // red
    colorName = 'Needs Work';
  }
  
  // SVG gauge parameters
  const size = 160;
  const strokeWidth = 16;
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  
  // Calculate angle for semicircle gauge (-90 to 90 degrees)
  const angle = -90 + (animatedValue / 100) * 180;
  
  // Create arc path for background and value
  const createArcPath = (startAngle, endAngle) => {
    const start = (startAngle * Math.PI) / 180;
    const end = (endAngle * Math.PI) / 180;
    const x1 = center + radius * Math.cos(start);
    const y1 = center + radius * Math.sin(start);
    const x2 = center + radius * Math.cos(end);
    const y2 = center + radius * Math.sin(end);
    const largeArc = endAngle - startAngle > 180 ? 1 : 0;
    return `M ${x1},${y1} A ${radius},${radius} 0 ${largeArc} 1 ${x2},${y2}`;
  };
  
  return (
    <div 
      className="flex flex-col items-center p-4 transition-transform hover:scale-105 cursor-pointer"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <svg width={size} height={size * 0.7} viewBox={`0 0 ${size} ${size * 0.7}`}>
        {/* Background arc (gray) */}
        <path
          d={createArcPath(-90, 90)}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Gradient zones (green, yellow, red) */}
        <defs>
          <linearGradient id={`gradient-${label.replace(/\s/g, '')}`} x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" stopColor="#ef4444" />
            <stop offset="50%" stopColor="#eab308" />
            <stop offset="100%" stopColor="#16a34a" />
          </linearGradient>
        </defs>
        
        {/* Value arc with transition */}
        <path
          d={createArcPath(-90, angle)}
          fill="none"
          stroke={color}
          strokeWidth={isHovered ? strokeWidth + 2 : strokeWidth}
          strokeLinecap="round"
          style={{ 
            transition: 'all 0.8s cubic-bezier(0.4, 0, 0.2, 1)',
            filter: isHovered ? 'drop-shadow(0 0 8px rgba(0,0,0,0.3))' : 'none'
          }}
        />
        
        {/* Needle indicator */}
        <g 
          transform={`rotate(${angle} ${center} ${center})`}
          style={{ transition: 'transform 0.8s cubic-bezier(0.4, 0, 0.2, 1)' }}
        >
          <line
            x1={center}
            y1={center}
            x2={center}
            y2={strokeWidth + 5}
            stroke="#1f2937"
            strokeWidth="4"
            strokeLinecap="round"
          />
          <circle cx={center} cy={center} r="8" fill="#1f2937" />
          <circle cx={center} cy={center} r="4" fill="#ffffff" />
        </g>
        
        {/* Min/Max labels */}
        <text x="15" y={center + 5} fill="#9ca3af" fontSize="10" fontWeight="600">0</text>
        <text x={size - 15} y={center + 5} fill="#9ca3af" fontSize="10" fontWeight="600" textAnchor="end">{maxValue}</text>
        
        {/* Value text */}
        <text
          x={center}
          y={center + 25}
          textAnchor="middle"
          fontSize="28"
          fontWeight="700"
          fill="#1f2937"
        >
          {numericValue.toFixed(numericValue % 1 === 0 ? 0 : 1)}
        </text>
        <text
          x={center}
          y={center + 42}
          textAnchor="middle"
          fontSize="12"
          fill="#6b7280"
        >
          {unit}
        </text>
      </svg>
      
      <div className="text-center mt-3 w-full">
        <div className="font-bold text-base text-gray-900 mb-1">{label}</div>
        {description && (
          <div className="text-xs text-gray-600 mb-2 px-2">{description}</div>
        )}
        <div 
          className="inline-block px-3 py-1 rounded-full text-xs font-semibold text-white"
          style={{ backgroundColor: color }}
        >
          {colorName} • {Math.round(displayPercentage)}%
        </div>
      </div>
    </div>
  );
};

const AssessmentReport = ({ 
  playerData, 
  previousAssessments = [], 
  showComparison = true, 
  onClose 
}) => {
  const [assessmentHistory, setAssessmentHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [coachComment, setCoachComment] = useState('');
  const [strengths, setStrengths] = useState([]);
  const [weaknesses, setWeaknesses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const { user, isAuthenticated } = useAuth();
  
  useEffect(() => {
    if (playerData) {
      fetchAssessmentHistory();
      analyzePerformance();
      setCoachComment(playerData.coach_notes || '');
    }
  }, [playerData]);
  
  const fetchAssessmentHistory = async () => {
    if (!playerData?.player_name) return;
    
    try {
      setLoading(true);
      const response = await axios.get(`${API}/assessments/player/${encodeURIComponent(playerData.player_name)}`);
      
      // Format data for the trend chart
      const historyData = response.data.slice(0, 10).reverse().map((assessment) => ({
        date: new Date(assessment.created_at || assessment.assessment_date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
        overall: assessment.overall_score || 0,
        physical: assessment.physical_score || 0,
        technical: assessment.technical_score || 0,
        tactical: assessment.tactical_score || 0,
        psychological: assessment.psychological_score || 0,
      }));
      
      setAssessmentHistory(historyData);
    } catch (error) {
      console.error('Error fetching assessment history:', error);
      setAssessmentHistory([]);
    } finally {
      setLoading(false);
    }
  };
  
  const analyzePerformance = () => {
    if (!playerData) return;
    
    const strengthsList = [];
    const weaknessesList = [];
    const recommendationsList = [];
    
    // Analyze physical metrics
    if (playerData.sprint_30m && playerData.sprint_30m < 4.5) {
      strengthsList.push('Excellent sprint speed and acceleration');
    } else if (playerData.sprint_30m && playerData.sprint_30m > 5.0) {
      weaknessesList.push('Sprint speed needs improvement');
      recommendationsList.push('Focus on acceleration drills and plyometric training');
    }
    
    if (playerData.yo_yo_test && playerData.yo_yo_test > 1800) {
      strengthsList.push('Outstanding endurance capacity');
    } else if (playerData.yo_yo_test && playerData.yo_yo_test < 1200) {
      weaknessesList.push('Endurance below optimal level');
      recommendationsList.push('Increase aerobic training with interval running');
    }
    
    // Analyze technical skills
    if (playerData.passing_accuracy && playerData.passing_accuracy >= 80) {
      strengthsList.push('Excellent passing accuracy');
    } else if (playerData.passing_accuracy && playerData.passing_accuracy < 65) {
      weaknessesList.push('Passing accuracy needs work');
      recommendationsList.push('Practice passing drills under pressure');
    }
    
    if (playerData.ball_control && playerData.ball_control >= 4) {
      strengthsList.push('Strong ball control and first touch');
    } else if (playerData.ball_control && playerData.ball_control < 3) {
      weaknessesList.push('Ball control requires development');
      recommendationsList.push('Increase ball mastery training sessions');
    }
    
    // Analyze tactical intelligence
    if (playerData.game_intelligence && playerData.game_intelligence >= 4) {
      strengthsList.push('High tactical awareness and game reading');
    } else if (playerData.game_intelligence && playerData.game_intelligence < 3) {
      weaknessesList.push('Tactical understanding needs improvement');
      recommendationsList.push('Study game footage and work on positioning');
    }
    
    // Analyze psychological attributes
    if (playerData.mental_toughness && playerData.mental_toughness >= 4) {
      strengthsList.push('Strong mental resilience');
    }
    
    // Add general recommendations if none specific
    if (recommendationsList.length === 0) {
      recommendationsList.push('Continue current training program');
      recommendationsList.push('Focus on maintaining consistency');
      recommendationsList.push('Set progressive goals for next assessment');
    }
    
    setStrengths(strengthsList.length > 0 ? strengthsList : ['All-around solid performance']);
    setWeaknesses(weaknessesList.length > 0 ? weaknessesList : ['No major weaknesses identified']);
    setRecommendations(recommendationsList);
  };
  
  const handlePrint = () => {
    window.print();
  };
  
  const handleDownloadPDF = () => {
    try {
      const reportContent = `
╔════════════════════════════════════════════════════════════╗
║           YO-YO ELITE SOCCER ASSESSMENT REPORT            ║
╚════════════════════════════════════════════════════════════╝

PLAYER INFORMATION
──────────────────────────────────────────────────────────────
Name:                ${playerData.player_name || 'N/A'}
Age:                 ${playerData.age || 'N/A'} years
Position:            ${playerData.position || 'N/A'}
Assessment Date:     ${new Date().toLocaleDateString()}

PERFORMANCE SCORES
──────────────────────────────────────────────────────────────
Overall Score:       ${Math.round(playerData.overall_score || 0)}/100
Physical Score:      ${Math.round(playerData.physical_score || 0)}/100
Technical Score:     ${Math.round(playerData.technical_score || 0)}/100
Tactical Score:      ${Math.round(playerData.tactical_score || 0)}/100
Psychological Score: ${Math.round(playerData.psychological_score || 0)}/100

DETAILED METRICS
──────────────────────────────────────────────────────────────
Physical:
  • Sprint 30m:        ${playerData.sprint_30m || 'N/A'} sec
  • Yo-Yo Test:        ${playerData.yo_yo_test || 'N/A'} m
  • VO₂ Max:           ${playerData.vo2_max || 'N/A'} ml/kg/min
  • Vertical Jump:     ${playerData.vertical_jump || 'N/A'} cm
  • Body Fat:          ${playerData.body_fat || 'N/A'}%

Technical:
  • Ball Control:      ${playerData.ball_control || 'N/A'}/5
  • Passing Accuracy:  ${playerData.passing_accuracy || 'N/A'}%
  • Dribbling Success: ${playerData.dribbling_success || 'N/A'}%
  • Shooting Accuracy: ${playerData.shooting_accuracy || 'N/A'}%

Tactical:
  • Game Intelligence: ${playerData.game_intelligence || 'N/A'}/5
  • Positioning:       ${playerData.positioning || 'N/A'}/5
  • Decision Making:   ${playerData.decision_making || 'N/A'}/5

Psychological:
  • Mental Toughness:  ${playerData.mental_toughness || 'N/A'}/5
  • Coachability:      ${playerData.coachability || 'N/A'}/5

STRENGTHS
──────────────────────────────────────────────────────────────
${strengths.map((s, i) => `${i + 1}. ${s}`).join('\n')}

AREAS FOR IMPROVEMENT
──────────────────────────────────────────────────────────────
${weaknesses.map((w, i) => `${i + 1}. ${w}`).join('\n')}

RECOMMENDATIONS
──────────────────────────────────────────────────────────────
${recommendations.map((r, i) => `${i + 1}. ${r}`).join('\n')}

${coachComment ? `COACH COMMENTS
──────────────────────────────────────────────────────────────
${coachComment}
` : ''}
──────────────────────────────────────────────────────────────
Generated by Yo-Yo Elite Soccer Player AI Coach
Report Date: ${new Date().toLocaleString()}
      `;
      
      const blob = new Blob([reportContent], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Assessment_Report_${playerData.player_name?.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`;
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);
      URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Error downloading report:', error);
      alert('Failed to download report');
    }
  };
  
  const handleSaveToProfile = async () => {
    if (!isAuthenticated) {
      alert('Please login to save reports');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Authentication required');
        return;
      }
      
      const reportData = {
        player_name: playerData.player_name,
        title: `Assessment Report - ${playerData.player_name}`,
        report_type: 'milestone',
        report_data: {
          playerData: playerData,
          assessmentDate: new Date().toISOString(),
          strengths: strengths,
          weaknesses: weaknesses,
          recommendations: recommendations,
          coachComment: coachComment
        },
        notes: coachComment
      };
      
      const response = await axios.post(`${API}/auth/save-report`, reportData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      alert('✅ Report saved to profile successfully!');
    } catch (error) {
      console.error('Error saving report:', error);
      alert('Failed to save report: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  const handleSaveBenchmark = async () => {
    if (!isAuthenticated) {
      alert('Please login to save benchmarks');
      return;
    }
    
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        alert('Authentication required');
        return;
      }
      
      const benchmarkData = {
        player_name: playerData.player_name,
        age: playerData.age,
        position: playerData.position,
        assessment_date: new Date().toISOString(),
        // Physical metrics
        sprint_30m: playerData.sprint_30m,
        yo_yo_test: playerData.yo_yo_test,
        vo2_max: playerData.vo2_max,
        vertical_jump: playerData.vertical_jump,
        body_fat: playerData.body_fat,
        // Technical metrics
        ball_control: playerData.ball_control,
        passing_accuracy: playerData.passing_accuracy,
        dribbling_success: playerData.dribbling_success,
        shooting_accuracy: playerData.shooting_accuracy,
        defensive_duels: playerData.defensive_duels,
        // Tactical metrics
        game_intelligence: playerData.game_intelligence,
        positioning: playerData.positioning,
        decision_making: playerData.decision_making,
        // Psychological metrics
        coachability: playerData.coachability,
        mental_toughness: playerData.mental_toughness,
        // Scores
        overall_score: playerData.overall_score,
        physical_score: playerData.physical_score,
        technical_score: playerData.technical_score,
        tactical_score: playerData.tactical_score,
        psychological_score: playerData.psychological_score,
        // Additional info
        coach_notes: coachComment
      };
      
      const response = await axios.post(`${API}/auth/save-benchmark`, benchmarkData, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
      });
      
      alert('✅ Benchmark saved successfully!');
    } catch (error) {
      console.error('Error saving benchmark:', error);
      alert('Failed to save benchmark: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  if (!playerData) {
    return (
      <Card className="w-full">
        <CardContent className="p-8 text-center">
          <p className="text-gray-500">No assessment data available</p>
        </CardContent>
      </Card>
    );
  }
  
  // Calculate performance level
  const overallScore = playerData.overall_score || 0;
  let performanceLevel = 'DEVELOPING';
  if (overallScore >= 80) performanceLevel = 'ELITE';
  else if (overallScore >= 70) performanceLevel = 'ADVANCED';
  else if (overallScore >= 60) performanceLevel = 'STANDARD';
  
  const assessmentDate = playerData.assessment_date 
    ? new Date(playerData.assessment_date).toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' })
    : new Date().toLocaleDateString('en-US', { month: 'long', day: 'numeric', year: 'numeric' });
  
  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-white rounded-lg shadow-lg print:shadow-none">
      {/* Header with Player Info */}
      <div className="mb-8 pb-6 border-b-2 border-gray-200">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 uppercase tracking-tight mb-2">
              {playerData.player_name || 'Player Name'}
            </h1>
            <div className="flex gap-6 text-lg text-gray-600">
              <span><strong>Age:</strong> {playerData.age || 'N/A'}</span>
              <span><strong>Position:</strong> {playerData.position || 'N/A'}</span>
              <span><strong>Date:</strong> {assessmentDate}</span>
            </div>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 uppercase tracking-wide">Overall Score</div>
            <div className="text-6xl font-bold text-gray-900">{Math.round(overallScore)}</div>
            <div className="text-lg font-semibold text-blue-600 mt-1">{performanceLevel}</div>
          </div>
        </div>
      </div>
      
      {/* Performance Category Scores */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-blue-600">{Math.round(playerData.physical_score || 0)}</div>
            <div className="text-sm font-semibold text-gray-700 mt-1">Physical</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-green-600">{Math.round(playerData.technical_score || 0)}</div>
            <div className="text-sm font-semibold text-gray-700 mt-1">Technical</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-purple-600">{Math.round(playerData.tactical_score || 0)}</div>
            <div className="text-sm font-semibold text-gray-700 mt-1">Tactical</div>
          </CardContent>
        </Card>
        <Card>
          <CardContent className="p-4 text-center">
            <div className="text-3xl font-bold text-orange-600">{Math.round(playerData.psychological_score || 0)}</div>
            <div className="text-sm font-semibold text-gray-700 mt-1">Psychological</div>
          </CardContent>
        </Card>
      </div>
      
      {/* Gauge Charts - Physical Metrics */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Physical Performance Metrics</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <GaugeChart
              value={playerData.sprint_30m || 0}
              label="Sprint 30m"
              max={6}
              unit="s"
              description="Lower is better (Elite: <4.5s)"
            />
            <GaugeChart
              value={playerData.yo_yo_test || 0}
              label="Yo-Yo Test"
              max={2400}
              unit="m"
              description="Endurance capacity"
            />
            <GaugeChart
              value={playerData.vo2_max || 0}
              label="VO₂ Max"
              max={70}
              unit=""
              description="Aerobic fitness"
            />
            <GaugeChart
              value={playerData.vertical_jump || 0}
              label="Vertical Jump"
              max={80}
              unit="cm"
              description="Explosive power"
            />
            <GaugeChart
              value={playerData.body_fat || 0}
              label="Body Fat"
              max={20}
              unit="%"
              description="Body composition"
            />
          </div>
        </CardContent>
      </Card>
      
      {/* Gauge Charts - Technical & Tactical */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle>Technical & Tactical Skills</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <GaugeChart
              value={playerData.ball_control || 0}
              label="Ball Control"
              max={5}
              unit="/5"
              description="First touch & mastery"
            />
            <GaugeChart
              value={playerData.passing_accuracy || 0}
              label="Passing Accuracy"
              max={100}
              unit="%"
              description="Successful passes"
            />
            <GaugeChart
              value={playerData.dribbling_success || 0}
              label="Dribbling"
              max={100}
              unit="%"
              description="1v1 effectiveness"
            />
            <GaugeChart
              value={playerData.shooting_accuracy || 0}
              label="Shooting"
              max={100}
              unit="%"
              description="Shots on target"
            />
            <GaugeChart
              value={playerData.game_intelligence || 0}
              label="Game Intelligence"
              max={5}
              unit="/5"
              description="Tactical awareness"
            />
            <GaugeChart
              value={playerData.positioning || 0}
              label="Positioning"
              max={5}
              unit="/5"
              description="Off-ball movement"
            />
          </div>
        </CardContent>
      </Card>
      
      {/* Assessment Trend Chart */}
      {assessmentHistory.length > 1 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Performance Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={assessmentHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line type="monotone" dataKey="overall" stroke="#2563eb" strokeWidth={3} name="Overall" />
                <Line type="monotone" dataKey="physical" stroke="#0891b2" strokeWidth={2} name="Physical" />
                <Line type="monotone" dataKey="technical" stroke="#16a34a" strokeWidth={2} name="Technical" />
                <Line type="monotone" dataKey="tactical" stroke="#9333ea" strokeWidth={2} name="Tactical" />
                <Line type="monotone" dataKey="psychological" stroke="#f97316" strokeWidth={2} name="Psychological" />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
      
      {/* Analysis: Strengths, Weaknesses, Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card className="border-l-4 border-green-500">
          <CardHeader>
            <CardTitle className="text-green-700 flex items-center gap-2">
              <span className="text-2xl">✓</span> Strengths
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {strengths.map((strength, index) => (
                <li key={index} className="text-gray-700 text-sm">• {strength}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-red-500">
          <CardHeader>
            <CardTitle className="text-red-700 flex items-center gap-2">
              <span className="text-2xl">!</span> Areas for Improvement
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {weaknesses.map((weakness, index) => (
                <li key={index} className="text-gray-700 text-sm">• {weakness}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
        
        <Card className="border-l-4 border-blue-500">
          <CardHeader>
            <CardTitle className="text-blue-700 flex items-center gap-2">
              <span className="text-2xl">→</span> Recommendations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {recommendations.map((recommendation, index) => (
                <li key={index} className="text-gray-700 text-sm">• {recommendation}</li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>
      
      {/* Coach Comment Section */}
      <Card className="mb-8">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <MessageSquare className="w-5 h-5" />
            Coach Comments
          </CardTitle>
        </CardHeader>
        <CardContent>
          <Textarea
            value={coachComment}
            onChange={(e) => setCoachComment(e.target.value)}
            placeholder="Add coach observations, feedback, or specific notes about this assessment..."
            rows={4}
            className="w-full"
          />
        </CardContent>
      </Card>
      
      {/* Action Buttons */}
      <div className="flex flex-wrap gap-4 justify-center print:hidden">
        <Button onClick={handlePrint} variant="outline" className="flex items-center gap-2">
          <Printer className="h-4 w-4" />
          Print Report
        </Button>
        
        <Button onClick={handleDownloadPDF} variant="outline" className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Download Report
        </Button>
        
        <Button onClick={handleSaveToProfile} variant="outline" className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          Save to Profile
        </Button>
        
        <Button onClick={handleSaveBenchmark} className="flex items-center gap-2 bg-blue-600 hover:bg-blue-700">
          <Bookmark className="h-4 w-4" />
          Save as Benchmark
        </Button>
        
        {onClose && (
          <Button onClick={onClose} variant="secondary">
            Close
          </Button>
        )}
      </div>
      
      {/* Footer */}
      <div className="mt-8 pt-6 border-t text-center text-sm text-gray-500">
        <p>Generated by Yo-Yo Elite Soccer Player AI Coach</p>
        <p className="mt-1">Professional Assessment & Training Platform</p>
      </div>
    </div>
  );
};

export default AssessmentReport;
