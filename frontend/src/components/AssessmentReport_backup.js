import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import axios from 'axios';
import { useAuth } from '../contexts/AuthContext';
import { Printer, Download, Save, Bookmark } from 'lucide-react';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Gauge Chart Component matching the design
const GaugeChart = ({ value, label, standardValue, unit = '', isLowerBetter = false }) => {
  // Calculate percentage of standard
  let percentage;
  if (isLowerBetter) {
    // For metrics like sprint time where lower is better
    percentage = standardValue ? (standardValue / value) * 100 : 0;
  } else {
    // For metrics where higher is better
    percentage = standardValue ? (value / standardValue) * 100 : 0;
  }
  
  // Clamp percentage between 0 and 120
  percentage = Math.max(0, Math.min(120, percentage));
  
  // Determine color based on percentage
  let color;
  if (percentage >= 100) {
    color = '#16a34a'; // green
  } else if (percentage >= 80) {
    color = '#eab308'; // yellow/orange
  } else {
    color = '#ef4444'; // red
  }
  
  // SVG gauge parameters
  const size = 140;
  const strokeWidth = 14;
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  
  // Calculate rotation angle (0-180 degrees for semicircle)
  const angle = -90 + (Math.min(percentage, 110) / 110) * 180;
  
  return (
    <div className="flex flex-col items-center p-4">
      <svg width={size} height={size * 0.65} viewBox={`0 0 ${size} ${size * 0.65}`}>
        {/* Background arc (green-yellow-red gradient) */}
        <path
          d={`M ${strokeWidth/2},${center} A ${radius},${radius} 0 0 1 ${size - strokeWidth/2},${center}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Green section (0-90 degrees) */}
        <path
          d={`M ${strokeWidth/2},${center} A ${radius},${radius} 0 0 1 ${center},${center - radius}`}
          fill="none"
          stroke="#16a34a"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          opacity="0.3"
        />
        
        {/* Yellow section (90-135 degrees) */}
        <path
          d={`M ${center},${center - radius} A ${radius},${radius} 0 0 1 ${center + radius * 0.707},${center - radius * 0.707}`}
          fill="none"
          stroke="#eab308"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          opacity="0.3"
        />
        
        {/* Red section (135-180 degrees) */}
        <path
          d={`M ${center + radius * 0.707},${center - radius * 0.707} A ${radius},${radius} 0 0 1 ${size - strokeWidth/2},${center}`}
          fill="none"
          stroke="#ef4444"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          opacity="0.3"
        />
        
        {/* Needle/pointer */}
        <g transform={`rotate(${angle} ${center} ${center})`}>
          <line
            x1={center}
            y1={center}
            x2={center}
            y2={strokeWidth + 8}
            stroke="#1f2937"
            strokeWidth="4"
            strokeLinecap="round"
          />
          <circle cx={center} cy={center} r="8" fill="#1f2937" />
        </g>
        
        {/* Value text */}
        <text
          x={center}
          y={center + 20}
          textAnchor="middle"
          className="font-bold"
          style={{ fontSize: '24px' }}
          fill="#1f2937"
        >
          {typeof value === 'number' ? value.toFixed(1) : value}
        </text>
        
        {/* Standard value indicator (top right) */}
        {standardValue && (
          <text
            x={size - 15}
            y={20}
            textAnchor="end"
            style={{ fontSize: '12px', fill: '#16a34a', fontWeight: 'bold' }}
          >
            {standardValue}
          </text>
        )}
      </svg>
      
      <div className="text-center mt-2">
        <div className="font-bold text-base text-gray-900">{label}</div>
        {standardValue && (
          <div className="text-sm text-gray-600 mt-1">
            {percentage < 80 ? 'Needs work. ' : percentage >= 100 ? 'Excellent! ' : 'Good. '}
            {Math.round(percentage)}% of standard
          </div>
        )}
        {unit && (
          <div className="text-xs text-gray-500 mt-1">{unit}</div>
        )}
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
  const [strengths, setStrengths] = useState([]);
  const [weaknesses, setWeaknesses] = useState([]);
  const [recommendations, setRecommendations] = useState([]);
  const { user, isAuthenticated } = useAuth();
  
  useEffect(() => {
    if (playerData && playerData.player_name) {
      fetchAssessmentHistory();
      analyzePerformance();
    }
  }, [playerData]);
  
  const fetchAssessmentHistory = async () => {
    try {
      setLoading(true);
      const response = await axios.get(`${API}/assessments/player/${playerData.player_name}`);
      
      // Format data for the trend chart
      const historyData = response.data.slice(0, 10).reverse().map((assessment, index) => ({
        date: new Date(assessment.created_at || assessment.assessment_date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
        overallScore: assessment.overall_score || 0,
        sprint30m: assessment.sprint_30m || 0,
        passingAccuracy: assessment.passing_accuracy || 0,
        ballControl: (assessment.ball_control || 0) * 20, // Convert 1-5 scale to percentage
      }));
      
      setAssessmentHistory(historyData);
    } catch (error) {
      console.error('Error fetching assessment history:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const analyzePerformance = () => {
    if (!playerData) return;
    
    // Define standards based on age group (example - you can adjust)
    const standards = {
      sprint_30m: 4.5,
      yo_yo_test: 1600,
      passing_accuracy: 75,
      ball_control: 4,
      game_intelligence: 4,
    };
    
    const strengthsList = [];
    const weaknessesList = [];
    const recommendationsList = [];
    
    // Analyze Physical
    if (playerData.sprint_30m && playerData.sprint_30m <= standards.sprint_30m) {
      strengthsList.push('YouYo / Beep test');
      strengthsList.push('Sprint acceleration');
    } else if (playerData.sprint_30m > standards.sprint_30m) {
      weaknessesList.push('Acceleration');
      weaknessesList.push('Change-of-direction speed');
      recommendationsList.push('Improve sprint starts and acceleration');
      recommendationsList.push('Include agility ladder and shuffle runs');
    }
    
    // Analyze Technical
    if (playerData.ball_control && playerData.ball_control >= standards.ball_control) {
      strengthsList.push('Dribbling');
    } else if (playerData.ball_control < standards.ball_control) {
      weaknessesList.push('First touch');
      recommendationsList.push('Refine first touch under pressure');
    }
    
    if (playerData.passing_accuracy && playerData.passing_accuracy >= standards.passing_accuracy) {
      strengthsList.push('Passing accuracy');
    }
    
    // Analyze Tactical
    if (playerData.game_intelligence && playerData.game_intelligence >= standards.game_intelligence) {
      strengthsList.push('Neuromotor / cognitive speed');
    }
    
    // Set default recommendations if none
    if (recommendationsList.length === 0) {
      recommendationsList.push('Continue current training regimen');
      recommendationsList.push('Focus on maintaining strengths');
      recommendationsList.push('Work on consistency across all areas');
    }
    
    setStrengths(strengthsList);
    setWeaknesses(weaknessesList);
    setRecommendations(recommendationsList);
  };
  
  const handlePrint = () => {
    window.print();
  };
  
  const handleDownloadPDF = async () => {
    try {
      // Create a simple text-based report
      const reportText = `
========================================
SOCCER PERFORMANCE REPORT
========================================

Player: ${playerData.player_name}
Age: ${playerData.age}
Position: ${playerData.position}
Assessment Date: ${new Date().toLocaleDateString()}

OVERALL SCORE: ${playerData.overall_score || 'N/A'}

PERFORMANCE METRICS:
--------------------
Sprint 30m: ${playerData.sprint_30m || 'N/A'} sec
Agility Test: ${playerData.yo_yo_test || 'N/A'} m
Endurance Beep Test: ${playerData.yo_yo_test || 'N/A'} m
Ball Control: ${playerData.ball_control || 'N/A'} / 5
Passing Accuracy: ${playerData.passing_accuracy || 'N/A'}%

STRENGTHS:
${strengths.map(s => `• ${s}`).join('\n')}

WEAKNESSES:
${weaknesses.map(w => `• ${w}`).join('\n')}

RECOMMENDATIONS:
${recommendations.map(r => `• ${r}`).join('\n')}

========================================
Generated by Yo-Yo Elite Soccer Player AI Coach
      `;
      
      const blob = new Blob([reportText], { type: 'text/plain' });
      const url = URL.createObjectURL(blob);
      const link = document.createElement('a');
      link.href = url;
      link.download = `Soccer_Performance_Report_${playerData.player_name.replace(/\s+/g, '_')}.txt`;
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
      const reportData = {
        player_name: playerData.player_name,
        assessment_summary: {
          overall_score: playerData.overall_score,
          physical_score: playerData.physical_score || 0,
          technical_score: playerData.technical_score || 0,
          tactical_score: playerData.tactical_score || 0,
          psychological_score: playerData.psychological_score || 0,
        },
        strengths: strengths,
        weaknesses: weaknesses,
        recommendations: recommendations,
      };
      
      const response = await axios.post(`${API}/auth/save-report`, reportData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      alert('Report saved to profile successfully!');
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
      const benchmarkData = {
        player_name: playerData.player_name,
        age: playerData.age,
        position: playerData.position,
        assessment_data: {
          // Physical
          sprint_30m: playerData.sprint_30m,
          yo_yo_test: playerData.yo_yo_test,
          vo2_max: playerData.vo2_max,
          vertical_jump: playerData.vertical_jump,
          body_fat: playerData.body_fat,
          // Technical
          ball_control: playerData.ball_control,
          passing_accuracy: playerData.passing_accuracy,
          dribbling_success: playerData.dribbling_success,
          shooting_accuracy: playerData.shooting_accuracy,
          defensive_duels: playerData.defensive_duels,
          // Tactical
          game_intelligence: playerData.game_intelligence,
          positioning: playerData.positioning,
          decision_making: playerData.decision_making,
          // Psychological
          coachability: playerData.coachability,
          mental_toughness: playerData.mental_toughness,
        },
        overall_score: playerData.overall_score,
      };
      
      const response = await axios.post(`${API}/auth/save-benchmark`, benchmarkData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('token')}`,
        },
      });
      
      alert('Benchmark saved successfully!');
    } catch (error) {
      console.error('Error saving benchmark:', error);
      alert('Failed to save benchmark: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  if (!playerData) {
    return (
      <Card className="w-full">
        <CardContent className="p-8 text-center">
          <p className="text-gray-500">No player data available</p>
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
  
  return (
    <div className="w-full max-w-7xl mx-auto p-6 bg-white rounded-lg shadow-lg print:shadow-none">
      {/* Header */}
      <div className="mb-8 border-b pb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 uppercase tracking-tight">
              {playerData.player_name}
            </h1>
            <p className="text-lg text-gray-600 mt-2">
              Age: {playerData.age} | Position: {playerData.position}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 uppercase tracking-wide">Overall Score</div>
            <div className="text-6xl font-bold text-gray-900">{Math.round(overallScore)}</div>
          </div>
        </div>
      </div>
      
      {/* Performance Level */}
      <div className="mb-8">
        <div className="text-sm text-gray-500 uppercase tracking-wide mb-2">Performance Level</div>
        <div className="text-3xl font-bold text-gray-900">{performanceLevel}</div>
      </div>
      
      {/* Gauge Charts Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardContent className="p-2">
            <GaugeChart
              value={playerData.sprint_30m || 0}
              label="Sprint 30m"
              standardValue={4.5}
              unit="30m sprint time. Measures acceleration and explosive speed."
              isLowerBetter={true}
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-2">
            <GaugeChart
              value={playerData.yo_yo_test || 0}
              label="Agility test"
              standardValue={1600}
              unit="Change-of-direction speed. Measures footwork and body control."
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-2">
            <GaugeChart
              value={playerData.vo2_max || 0}
              label="Reaction time"
              standardValue={55}
              unit="Measures neuromotor/ cognitive response speed."
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-2">
            <GaugeChart
              value={playerData.yo_yo_test || 0}
              label="Endurance Beep test"
              standardValue={1600}
              unit="Yo Yo / Beep test level. Measures aerobic capacity."
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-2">
            <GaugeChart
              value={(playerData.ball_control || 0)}
              label="Ball control"
              standardValue={5}
              unit="1-10 rating of first touch and dribbling."
            />
          </CardContent>
        </Card>
        
        <Card>
          <CardContent className="p-2">
            <GaugeChart
              value={playerData.passing_accuracy || 0}
              label="Passing Accuracy"
              standardValue={85}
              unit="Percentage of successful passes to a target."
            />
          </CardContent>
        </Card>
      </div>
      
      {/* Assessment Trend Chart */}
      {assessmentHistory.length > 0 && (
        <Card className="mb-8">
          <CardHeader>
            <CardTitle>Assessment Trend</CardTitle>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={assessmentHistory}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis domain={[0, 100]} />
                <Tooltip />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="overallScore" 
                  stroke="#2563eb" 
                  strokeWidth={2}
                  name="Overall Score"
                />
                <Line 
                  type="monotone" 
                  dataKey="sprint30m" 
                  stroke="#f97316" 
                  strokeWidth={2}
                  name="Sprint 30m"
                />
                <Line 
                  type="monotone" 
                  dataKey="passingAccuracy" 
                  stroke="#22c55e" 
                  strokeWidth={2}
                  name="Passing Accuracy"
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}
      
      {/* Strengths, Weaknesses, Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <Card>
          <CardHeader>
            <CardTitle className="text-green-700">Strengths</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-2">
              {strengths.length > 0 ? (
                strengths.map((strength, index) => (
                  <li key={index} className="text-gray-700">{strength}</li>
                ))
              ) : (
                <li className="text-gray-500">No specific strengths identified yet</li>
              )}
            </ul>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-red-700">Weaknesses</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-2">
              {weaknesses.length > 0 ? (
                weaknesses.map((weakness, index) => (
                  <li key={index} className="text-gray-700">{weakness}</li>
                ))
              ) : (
                <li className="text-gray-500">No specific weaknesses identified yet</li>
              )}
            </ul>
          </CardContent>
        </Card>
        
        <Card>
          <CardHeader>
            <CardTitle className="text-blue-700">Recommendations</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="list-disc list-inside space-y-2">
              {recommendations.length > 0 ? (
                recommendations.map((recommendation, index) => (
                  <li key={index} className="text-gray-700">{recommendation}</li>
                ))
              ) : (
                <li className="text-gray-500">Complete assessment to receive recommendations</li>
              )}
            </ul>
          </CardContent>
        </Card>
      </div>
      
      {/* Action Buttons */}
      <div className="flex flex-wrap gap-4 justify-center print:hidden">
        <Button onClick={handlePrint} variant="outline" className="flex items-center gap-2">
          <Printer className="h-4 w-4" />
          Print Report
        </Button>
        
        <Button onClick={handleDownloadPDF} variant="outline" className="flex items-center gap-2">
          <Download className="h-4 w-4" />
          Download PDF
        </Button>
        
        <Button onClick={handleSaveToProfile} variant="outline" className="flex items-center gap-2">
          <Save className="h-4 w-4" />
          Save to Profile
        </Button>
        
        <Button onClick={handleSaveBenchmark} className="flex items-center gap-2">
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
        <p className="mt-1">For players, parents & coaches</p>
      </div>
    </div>
  );
};

export default AssessmentReport;
