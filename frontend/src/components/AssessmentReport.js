import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { Printer, Download, X } from 'lucide-react';

// Professional Semicircle Gauge matching reference image
const SemicircleGauge = ({ value, label, percentOfStandard, description, unit = '' }) => {
  const [animated, setAnimated] = useState(0);
  
  useEffect(() => {
    setTimeout(() => setAnimated(percentOfStandard), 100);
  }, [percentOfStandard]);
  
  // Gauge parameters
  const size = 180;
  const strokeWidth = 18;
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  
  // Calculate angle based on percent (-90 to 90 degrees for semicircle)
  const percentage = Math.min(120, Math.max(0, animated));
  const angle = -90 + (percentage / 120) * 180;
  
  // Color coding
  let color;
  if (percentOfStandard >= 100) color = '#22c55e'; // green
  else if (percentOfStandard >= 85) color = '#eab308'; // yellow
  else color = '#ef4444'; // red
  
  // Create arc path
  const createArc = (startAngle, endAngle) => {
    const start = (startAngle * Math.PI) / 180;
    const end = (endAngle * Math.PI) / 180;
    const x1 = center + radius * Math.cos(start);
    const y1 = center + radius * Math.sin(start);
    const x2 = center + radius * Math.cos(end);
    const y2 = center + radius * Math.sin(end);
    const largeArc = endAngle - startAngle > 180 ? 1 : 0;
    return `M ${x1} ${y1} A ${radius} ${radius} 0 ${largeArc} 1 ${x2} ${y2}`;
  };
  
  return (
    <div className="flex flex-col items-center p-4 bg-white rounded-lg border border-gray-200">
      <svg width={size} height={size * 0.65} viewBox={`0 0 ${size} ${size * 0.65}`}>
        {/* Background arc */}
        <path
          d={createArc(-90, 90)}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Green zone */}
        <path
          d={createArc(-90, -30)}
          fill="none"
          stroke="#22c55e"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          opacity="0.3"
        />
        
        {/* Yellow zone */}
        <path
          d={createArc(-30, 30)}
          fill="none"
          stroke="#eab308"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          opacity="0.3"
        />
        
        {/* Red zone */}
        <path
          d={createArc(30, 90)}
          fill="none"
          stroke="#ef4444"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          opacity="0.3"
        />
        
        {/* Value arc */}
        <path
          d={createArc(-90, angle)}
          fill="none"
          stroke={color}
          strokeWidth={strokeWidth}
          strokeLinecap="round"
          style={{ transition: 'all 1s ease-out' }}
        />
        
        {/* Needle */}
        <g transform={`rotate(${angle} ${center} ${center})`} style={{ transition: 'transform 1s ease-out' }}>
          <line
            x1={center}
            y1={center}
            x2={center}
            y2={strokeWidth}
            stroke="#1f2937"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle cx={center} cy={center} r="7" fill="#1f2937" />
        </g>
        
        {/* Min/Max labels */}
        <text x="10" y={center + 5} fontSize="11" fill="#9ca3af" fontWeight="600">0</text>
        <text x={size - 25} y={center + 5} fontSize="11" fill="#9ca3af" fontWeight="600" textAnchor="end">
          {percentOfStandard >= 100 ? '100' : '110'}
        </text>
        
        {/* Value display */}
        <text
          x={center}
          y={center + 20}
          textAnchor="middle"
          fontSize="32"
          fontWeight="700"
          fill="#1f2937"
        >
          {value}{unit}
        </text>
      </svg>
      
      {/* Labels */}
      <div className="text-center mt-3 w-full">
        <h4 className="font-bold text-base text-gray-900 mb-1">{label}</h4>
        <p className="text-xs text-gray-600 mb-2 px-2 leading-tight">{description}</p>
        <div 
          className="inline-block px-3 py-1 rounded text-xs font-semibold"
          style={{ backgroundColor: color, color: 'white' }}
        >
          {percentOfStandard}% of standard
        </div>
      </div>
    </div>
  );
};

const PlayerReport = ({ reportData, onClose }) => {
  const [trendData, setTrendData] = useState([]);
  
  useEffect(() => {
    if (reportData?.trend) {
      const formatted = reportData.trend.dates.map((date, i) => ({
        date: new Date(date).toLocaleDateString('en-US', { month: 'short', year: '2-digit' }),
        overall: reportData.trend.overall_scores[i] || 0,
        sprint: reportData.trend.sprint_30m_scores[i] || 0,
        passing: reportData.trend.passing_accuracy_scores[i] || 0
      }));
      setTrendData(formatted);
    }
  }, [reportData]);
  
  if (!reportData) {
    return (
      <div className="p-8 text-center text-gray-500">
        No report data available
      </div>
    );
  }
  
  const { player_name, age, position, overall_score, metrics } = reportData;
  
  // Determine performance level
  let performanceLevel = 'NEEDS DEVELOPMENT';
  if (overall_score >= 90) performanceLevel = 'ELITE';
  else if (overall_score >= 75) performanceLevel = 'ADVANCED';
  else if (overall_score >= 60) performanceLevel = 'STANDARD';
  
  const handlePrint = () => window.print();
  
  const handleDownload = () => {
    const content = `
PLAYER PERFORMANCE REPORT
========================

Player: ${player_name}
Age: ${age}
Position: ${position}
Overall Score: ${overall_score}/100
Performance Level: ${performanceLevel}

PERFORMANCE METRICS
==================
Sprint 30m: ${metrics.sprint_30m.score}s (${metrics.sprint_30m.percent_of_standard}% of standard)
Agility: ${metrics.agility.score} (${metrics.agility.percent_of_standard}% of standard)
Reaction Time: ${metrics.reaction_time.score_ms}ms (${metrics.reaction_time.percent_of_standard}% of standard)
Endurance: ${metrics.endurance.score} (${metrics.endurance.percent_of_standard}% of standard)
Ball Control: ${metrics.ball_control.score_1_to_10}/10 (${metrics.ball_control.percent_of_standard}% of standard)
Passing Accuracy: ${metrics.passing_accuracy.score_percent}% (${metrics.passing_accuracy.percent_of_standard}% of standard)

Generated by Yo-Yo Elite Soccer Player AI Coach
    `;
    
    const blob = new Blob([content], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `Report_${player_name.replace(/\s/g, '_')}_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };
  
  return (
    <div className="w-full max-w-7xl mx-auto bg-white p-8 print:p-0">
      {/* Close button */}
      {onClose && (
        <button
          onClick={onClose}
          className="absolute top-4 right-4 p-2 hover:bg-gray-100 rounded-full print:hidden"
        >
          <X className="w-5 h-5" />
        </button>
      )}
      
      {/* Header */}
      <div className="flex justify-between items-start mb-8 pb-6 border-b-2 border-gray-200">
        <div>
          <h1 className="text-4xl font-bold text-gray-900 uppercase tracking-tight mb-2">
            {player_name}
          </h1>
          <p className="text-lg text-gray-600">
            Age: {age} | Position: {position}
          </p>
        </div>
        <div className="text-right">
          <div className="text-sm text-gray-500 uppercase tracking-wide mb-1">Overall Score</div>
          <div className="bg-gray-100 rounded-2xl px-6 py-4">
            <div className="text-6xl font-bold text-gray-900">{overall_score}</div>
          </div>
        </div>
      </div>
      
      {/* Performance Level */}
      <div className="mb-8">
        <div className="text-sm text-gray-500 uppercase tracking-wide mb-1">Performance Level</div>
        <div className="text-3xl font-bold text-gray-900">{performanceLevel}</div>
      </div>
      
      {/* Performance Metrics Gauges */}
      <div className="mb-8">
        <h2 className="text-2xl font-bold text-gray-900 mb-6">PERFORMANCE METRICS</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <SemicircleGauge
            value={metrics.sprint_30m.score}
            label="Sprint 30m"
            percentOfStandard={metrics.sprint_30m.percent_of_standard}
            description="30m sprint time. Measures acceleration and top-end speed."
            unit=""
          />
          
          <SemicircleGauge
            value={metrics.agility.score}
            label="Agility test"
            percentOfStandard={metrics.agility.percent_of_standard}
            description="Change-of-direction speed. Measures footwork and body control."
            unit=""
          />
          
          <SemicircleGauge
            value={metrics.reaction_time.score_ms}
            label="Reaction time"
            percentOfStandard={metrics.reaction_time.percent_of_standard}
            description="Measures neuromotor / cognitive response speed."
            unit="ms"
          />
          
          <SemicircleGauge
            value={metrics.endurance.score}
            label="Endurance Beep test"
            percentOfStandard={metrics.endurance.percent_of_standard}
            description="Yo Yo / Beep test level. Measures aerobic capacity."
            unit=""
          />
          
          <SemicircleGauge
            value={metrics.ball_control.score_1_to_10}
            label="Ball control"
            percentOfStandard={metrics.ball_control.percent_of_standard}
            description="1-10 rating of first touch and dribbling."
            unit=""
          />
          
          <SemicircleGauge
            value={metrics.passing_accuracy.score_percent}
            label="Passing Accuracy"
            percentOfStandard={metrics.passing_accuracy.percent_of_standard}
            description="Percentage of successful passes to a target."
            unit="%"
          />
        </div>
      </div>
      
      {/* Assessment Trend Chart */}
      {trendData.length > 1 && (
        <div className="mb-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">ASSESSMENT TREND</h2>
          <div className="bg-gray-50 p-6 rounded-lg">
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={trendData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
                <XAxis 
                  dataKey="date" 
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <YAxis 
                  domain={[0, 100]} 
                  stroke="#6b7280"
                  style={{ fontSize: '12px' }}
                />
                <Tooltip 
                  contentStyle={{ 
                    backgroundColor: '#ffffff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px'
                  }}
                />
                <Legend />
                <Line 
                  type="monotone" 
                  dataKey="overall" 
                  stroke="#2563eb" 
                  strokeWidth={3}
                  name="Overall Score"
                  dot={{ fill: '#2563eb', r: 4 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="sprint" 
                  stroke="#ef4444" 
                  strokeWidth={2}
                  name="Sprint 30 m"
                  dot={{ fill: '#ef4444', r: 3 }}
                />
                <Line 
                  type="monotone" 
                  dataKey="passing" 
                  stroke="#22c55e" 
                  strokeWidth={2}
                  name="Passing Accuracy"
                  dot={{ fill: '#22c55e', r: 3 }}
                />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
      
      {/* Strengths, Weaknesses, Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">STRENGTHS</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start">
              <span className="text-green-600 mr-2">•</span>
              YouYo / Beep test
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-2">•</span>
              Neuromotor / cognitive speed
            </li>
            <li className="flex items-start">
              <span className="text-green-600 mr-2">•</span>
              Dribbling
            </li>
          </ul>
        </div>
        
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">WEAKNESSES</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start">
              <span className="text-red-600 mr-2">•</span>
              Acceleration
            </li>
            <li className="flex items-start">
              <span className="text-red-600 mr-2">•</span>
              Change-of-direction speed
            </li>
            <li className="flex items-start">
              <span className="text-red-600 mr-2">•</span>
              First touch
            </li>
          </ul>
        </div>
        
        <div>
          <h3 className="text-xl font-bold text-gray-900 mb-4">RECOMMENDATIONS</h3>
          <ul className="space-y-2 text-sm text-gray-700">
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              Improve sprint starts and acceleration
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              Include agility ladder and shuffle runs
            </li>
            <li className="flex items-start">
              <span className="text-blue-600 mr-2">•</span>
              Refine first touch under pressure
            </li>
          </ul>
        </div>
      </div>
      
      {/* Action Buttons */}
      <div className="flex gap-4 justify-center print:hidden pt-6 border-t">
        <Button onClick={handlePrint} variant="outline" className="flex items-center gap-2">
          <Printer className="w-4 h-4" />
          Print Report
        </Button>
        <Button onClick={handleDownload} variant="outline" className="flex items-center gap-2">
          <Download className="w-4 h-4" />
          Download Report
        </Button>
      </div>
      
      {/* Footer */}
      <div className="mt-8 pt-4 border-t text-center text-sm text-gray-500">
        Generated by Yo-Yo Elite Soccer Player AI Coach
      </div>
    </div>
  );
};

export default PlayerReport;
