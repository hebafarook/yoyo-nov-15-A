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

// Gauge Chart Component
const GaugeChart = ({ value, label, max = 100, unit = '', description = '' }) => {
  // Ensure value is a number
  const numericValue = Number(value) || 0;
  const maxValue = Number(max) || 100;
  
  // Calculate percentage (0-100)
  const percentage = Math.min(100, Math.max(0, (numericValue / maxValue) * 100));
  
  // Determine color based on percentage
  let color;
  if (percentage >= 75) {
    color = '#16a34a'; // green
  } else if (percentage >= 50) {
    color = '#eab308'; // yellow
  } else {
    color = '#ef4444'; // red
  }
  
  // SVG gauge parameters
  const size = 140;
  const strokeWidth = 14;
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  
  // Calculate angle for semicircle gauge (-90 to 90 degrees)
  const angle = -90 + (percentage / 100) * 180;
  
  // Calculate stroke dash
  const dashArray = circumference;
  const dashOffset = circumference - (percentage / 100) * (circumference / 2);
  
  return (
    <div className="flex flex-col items-center p-4">
      <svg width={size} height={size * 0.65} viewBox={`0 0 ${size} ${size * 0.65}`}>
        {/* Background arc */}
        <path
          d={`M ${strokeWidth/2},${center} A ${radius},${radius} 0 0 1 ${size - strokeWidth/2},${center}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Value arc */}
        <path
          d={`M ${strokeWidth/2},${center} A ${radius},${radius} 0 0 1 ${center + radius * Math.cos((angle * Math.PI) / 180)},${center + radius * Math.sin((angle * Math.PI) / 180)}`}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Needle */}
        <g transform={`rotate(${angle} ${center} ${center})`}>
          <line
            x1={center}
            y1={center}
            x2={center}
            y2={strokeWidth + 8}
            stroke="#1f2937"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle cx={center} cy={center} r="6" fill="#1f2937" />
        </g>
        
        {/* Value text */}
        <text
          x={center}
          y={center + 20}
          textAnchor="middle"
          className="font-bold text-2xl"
          fill="#1f2937"
        >
          {numericValue.toFixed(numericValue % 1 === 0 ? 0 : 1)}{unit}
        </text>
      </svg>
      
      <div className="text-center mt-2">
        <div className="font-semibold text-sm text-gray-900">{label}</div>
        {description && (
          <div className="text-xs text-gray-500 mt-1">{description}</div>
        )}
        <div className="text-xs font-medium mt-1" style={{ color }}>
          {percentage >= 75 ? 'Excellent' : percentage >= 50 ? 'Good' : 'Needs Improvement'}
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
