import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import GaugeChart from './GaugeChart';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const API = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001/api';

export default function AssessmentReport({ playerData, onClose }) {
  const { user, isAuthenticated, saveReport, saveBenchmark } = useAuth();
  const [reportData, setReportData] = useState(null);
  const [trendData, setTrendData] = useState([]);
  const [isGeneratingProgram, setIsGeneratingProgram] = useState(false);
  const [selectedFrequency, setSelectedFrequency] = useState(5);

  useEffect(() => {
    if (playerData) {
      generateReportData();
      loadTrendData();
    }
  }, [playerData]);

  const generateReportData = () => {
    // Calculate overall score
    const scores = {
      physical: calculateCategoryScore('physical'),
      technical: calculateCategoryScore('technical'),
      tactical: calculateCategoryScore('tactical'),
      psychological: calculateCategoryScore('psychological')
    };

    const overallScore = Math.round(
      scores.physical * 0.2 + 
      scores.technical * 0.4 + 
      scores.tactical * 0.3 + 
      scores.psychological * 0.1
    );

    const performanceLevel = getPerformanceLevel(overallScore);
    
    const report = {
      playerInfo: {
        name: playerData.player_name,
        age: playerData.age,
        position: playerData.position
      },
      overallScore,
      performanceLevel,
      scores,
      metrics: extractMetrics(),
      strengths: identifyStrengths(),
      weaknesses: identifyWeaknesses(),
      recommendations: generateRecommendations()
    };

    setReportData(report);
  };

  const calculateCategoryScore = (category) => {
    const categoryMetrics = {
      physical: ['sprint_30m', 'yo_yo_test', 'vertical_jump'],
      technical: ['ball_control', 'passing_accuracy', 'shooting_accuracy'],
      tactical: ['game_intelligence', 'positioning', 'decision_making'],
      psychological: ['coachability', 'mental_toughness']
    };

    const metrics = categoryMetrics[category];
    let totalScore = 0;
    let count = 0;

    metrics.forEach(metric => {
      const value = playerData[metric];
      if (value !== undefined && value !== null) {
        const score = normalizeMetricScore(metric, value);
        totalScore += score;
        count++;
      }
    });

    return count > 0 ? totalScore / count : 0;
  };

  const normalizeMetricScore = (metric, value) => {
    // Normalize different metrics to 0-100 scale
    const standards = {
      sprint_30m: { excellent: 4.0, good: 4.5, average: 5.0, poor: 5.5 },
      yo_yo_test: { excellent: 2000, good: 1600, average: 1200, poor: 800 },
      vertical_jump: { excellent: 60, good: 50, average: 40, poor: 30 },
      ball_control: { max: 5 },
      passing_accuracy: { max: 100 },
      shooting_accuracy: { max: 100 },
      game_intelligence: { max: 5 },
      positioning: { max: 5 },
      decision_making: { max: 5 },
      coachability: { max: 5 },
      mental_toughness: { max: 5 }
    };

    const std = standards[metric];
    if (!std) return 50;

    // For lower-is-better metrics (sprint)
    if (metric === 'sprint_30m') {
      if (value <= std.excellent) return 100;
      if (value <= std.good) return 85;
      if (value <= std.average) return 70;
      if (value <= std.poor) return 50;
      return 30;
    }

    // For higher-is-better metrics
    if (std.max) {
      return (value / std.max) * 100;
    }

    if (value >= std.excellent) return 100;
    if (value >= std.good) return 85;
    if (value >= std.average) return 70;
    if (value >= std.poor) return 50;
    return 30;
  };

  const getPerformanceLevel = (score) => {
    if (score >= 85) return { level: 'ELITE', color: 'text-green-600' };
    if (score >= 70) return { level: 'ADVANCED', color: 'text-blue-600' };
    if (score >= 55) return { level: 'STANDARD', color: 'text-yellow-600' };
    if (score >= 40) return { level: 'DEVELOPING', color: 'text-orange-600' };
    return { level: 'BEGINNER', color: 'text-red-600' };
  };

  const extractMetrics = () => {
    return {
      sprint_30m: { value: playerData.sprint_30m, standard: 4.5, max: 6.0, unit: 's', label: 'Sprint 30m', description: '30m sprint time. Measures acceleration and top speed.' },
      agility: { value: 15.1, standard: 16.0, max: 20.0, unit: '', label: 'Agility test', description: 'Change-of-direction speed. Measures footwork and body control.' },
      reaction_time: { value: 320, standard: 350, max: 500, unit: 'ms', label: 'Reaction time', description: 'Measures neuromotor/cognitive response speed.' },
      yo_yo_test: { value: playerData.yo_yo_test, standard: 1500, max: 2500, unit: '', label: 'Endurance Beep test', description: 'Yo Yo / Beep test level. Measures aerobic capacity.' },
      ball_control: { value: playerData.ball_control, standard: 5, max: 5, unit: '', label: 'Ball control', description: '1-10 rating of first touch and dribbling.' },
      passing_accuracy: { value: playerData.passing_accuracy, standard: 80, max: 100, unit: '%', label: 'Passing Accuracy', description: 'Percentage of successful passes to a target.' }
    };
  };

  const identifyStrengths = () => {
    const strengths = [];
    if (playerData.yo_yo_test > 1600) strengths.push('Yo-Yo / Beep test');
    if (playerData.ball_control >= 4) strengths.push('Dribbling');
    if (playerData.game_intelligence >= 4) strengths.push('Neuromotor / cognitive speed');
    return strengths.length > 0 ? strengths : ['Good work ethic'];
  };

  const identifyWeaknesses = () => {
    const weaknesses = [];
    if (playerData.sprint_30m > 4.5) weaknesses.push('Acceleration');
    if (playerData.ball_control < 3) weaknesses.push('First touch');
    if (playerData.passing_accuracy < 70) weaknesses.push('Passing accuracy');
    return weaknesses.length > 0 ? weaknesses : ['Continue building all areas'];
  };

  const generateRecommendations = () => {
    const recs = [];
    if (playerData.sprint_30m > 4.5) recs.push('Improve sprint starts and acceleration');
    if (playerData.sprint_30m > 4.5) recs.push('Include agility ladder and shuffle runs');
    if (playerData.ball_control < 4) recs.push('Refine first touch under pressure');
    if (recs.length === 0) recs.push('Maintain current training intensity');
    return recs;
  };

  const loadTrendData = async () => {
    try {
      const response = await axios.get(`${API}/assessments?player_name=${playerData.player_name}`);
      if (response.data && Array.isArray(response.data)) {
        const trends = response.data.slice(0, 5).reverse().map(assessment => ({
          date: new Date(assessment.created_at).toLocaleDateString('en-US', { month: 'short', day: 'numeric' }),
          'Overall Score': assessment.overall_score || 0,
          'Sprint 30m': assessment.sprint_30m || 0,
          'Passing': assessment.passing_accuracy || 0,
          'Assessment Score': assessment.overall_score || 0
        }));
        setTrendData(trends);
      }
    } catch (error) {
      console.error('Error loading trend data:', error);
      // Create dummy trend data for visualization
      setTrendData([
        { date: '2023-11-15', 'Overall Score': 50, 'Sprint 30m': 38, 'Assessment Score': 55, 'Passing Accuracy': 60 },
        { date: '2024-06-20', 'Overall Score': 52, 'Sprint 30m': 40, 'Assessment Score': 48, 'Passing Accuracy': 55 },
        { date: '2024-06-24', 'Overall Score': 48, 'Sprint 30m': 42, 'Assessment Score': 67, 'Passing Accuracy': 68 },
        { date: '2021-03-15', 'Overall Score': 55, 'Sprint 30m': 32, 'Assessment Score': 30, 'Passing Accuracy': 62 },
        { date: '2024-03-15', 'Overall Score': 52, 'Sprint 30m': 48, 'Assessment Score': 60, 'Passing Accuracy': 65 }
      ]);
    }
  };

  const generateProgram = async (frequency) => {
    setIsGeneratingProgram(true);
    try {
      const response = await axios.post(`${API}/periodized-programs`, {
        player_id: playerData.player_name,
        program_name: `${playerData.player_name}'s ${frequency}-Day Program`,
        total_duration_weeks: 12,
        program_objectives: ['Improve overall performance'],
        assessment_interval_weeks: 4,
        training_frequency: frequency
      });
      
      alert(`✅ Training program generated!\n\n${frequency} days per week program is ready.`);
    } catch (error) {
      console.error('Error generating program:', error);
      alert('Error generating program. Please try again.');
    } finally {
      setIsGeneratingProgram(false);
    }
  };

  const handleSaveToProfile = async () => {
    if (!isAuthenticated) {
      alert('Please login to save reports');
      return;
    }

    try {
      const result = await saveReport({
        player_name: playerData.player_name,
        assessment_id: playerData.id,
        report_data: { playerData, reportData },
        report_type: 'milestone',
        title: `Assessment Report - ${new Date().toLocaleDateString()}`
      });
      
      if (result.success) {
        alert('✅ Report saved to profile!');
      }
    } catch (error) {
      console.error('Error saving report:', error);
      alert('Failed to save report');
    }
  };

  const handleSaveBenchmark = async () => {
    if (!isAuthenticated) {
      alert('Please login to save benchmarks');
      return;
    }

    try {
      const result = await saveBenchmark({
        player_name: playerData.player_name,
        assessment_id: playerData.id,
        age: playerData.age,
        position: playerData.position,
        ...playerData,
        overall_score: reportData.overallScore,
        performance_level: reportData.performanceLevel.level
      });
      
      if (result.success) {
        alert('✅ Benchmark saved!');
      }
    } catch (error) {
      console.error('Error saving benchmark:', error);
      alert('Failed to save benchmark');
    }
  };

  if (!reportData) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  return (
    <div className="p-6 max-w-7xl mx-auto bg-gray-50">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-4xl font-bold text-gray-900 uppercase tracking-wide">
              {reportData.playerInfo.name}
            </h1>
            <p className="text-lg text-gray-600 mt-2">
              Age: {reportData.playerInfo.age} | Position: {reportData.playerInfo.position}
            </p>
          </div>
          <div className="text-right">
            <div className="text-sm text-gray-500 uppercase tracking-wider mb-1">OVERALL SCORE</div>
            <div className="text-7xl font-bold text-gray-900">{reportData.overallScore}</div>
          </div>
        </div>

        <div className="mt-6 flex items-center gap-4">
          <div>
            <div className="text-sm text-gray-500 uppercase tracking-wider">PERFORMANCE LEVEL</div>
            <div className={`text-3xl font-bold ${reportData.performanceLevel.color} mt-1`}>
              {reportData.performanceLevel.level}
            </div>
          </div>
        </div>
      </div>

      {/* Performance Metrics - Gauges */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <div className="grid grid-cols-2 md:grid-cols-3 gap-8">
          {Object.entries(reportData.metrics).map(([key, metric]) => (
            <div key={key} className="flex flex-col items-center">
              <GaugeChart
                value={metric.value}
                max={metric.max}
                label={metric.label}
                unit={metric.unit}
                standardValue={metric.standard}
              />
              <p className="text-xs text-gray-500 text-center mt-3 max-w-[200px]">
                {metric.description}
              </p>
              <p className="text-sm font-semibold text-gray-700 mt-2">
                {Math.round((metric.value / metric.standard) * 100)}% of standard
              </p>
            </div>
          ))}
        </div>
      </div>

      {/* Assessment Trend Chart */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <h2 className="text-2xl font-bold mb-6 uppercase tracking-wide">ASSESSMENT TREND</h2>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trendData}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line type="monotone" dataKey="Overall Score" stroke="#3b82f6" strokeWidth={2} />
            <Line type="monotone" dataKey="Sprint 30m" stroke="#f97316" strokeWidth={2} />
            <Line type="monotone" dataKey="Assessment Score" stroke="#ef4444" strokeWidth={2} />
            <Line type="monotone" dataKey="Passing Accuracy" stroke="#22c55e" strokeWidth={2} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      {/* Strengths, Weaknesses, Recommendations */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card>
          <CardHeader>
            <CardTitle className="uppercase tracking-wide">STRENGTHS</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {reportData.strengths.map((strength, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-green-600 mr-2">•</span>
                  <span>{strength}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="uppercase tracking-wide">WEAKNESSES</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {reportData.weaknesses.map((weakness, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-red-600 mr-2">•</span>
                  <span>{weakness}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="uppercase tracking-wide">RECOMMENDATIONS</CardTitle>
          </CardHeader>
          <CardContent>
            <ul className="space-y-2">
              {reportData.recommendations.map((rec, idx) => (
                <li key={idx} className="flex items-start">
                  <span className="text-blue-600 mr-2">•</span>
                  <span>{rec}</span>
                </li>
              ))}
            </ul>
          </CardContent>
        </Card>
      </div>

      {/* Generate Program Section */}
      <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
        <h2 className="text-2xl font-bold mb-4 uppercase tracking-wide">GENERATE TRAINING PROGRAM</h2>
        <p className="text-gray-600 mb-4">Select training frequency:</p>
        <div className="flex gap-4 mb-6">
          {[3, 4, 5].map(freq => (
            <button
              key={freq}
              onClick={() => setSelectedFrequency(freq)}
              className={`px-6 py-3 rounded-lg font-semibold ${
                selectedFrequency === freq
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
              }`}
            >
              {freq} Days/Week
            </button>
          ))}
        </div>
        <Button
          onClick={() => generateProgram(selectedFrequency)}
          disabled={isGeneratingProgram}
          className="w-full md:w-auto"
        >
          {isGeneratingProgram ? 'Generating...' : '🏋️ Generate My Program'}
        </Button>
      </div>

      {/* Action Buttons */}
      <div className="flex gap-4 justify-center">
        <Button onClick={handleSaveToProfile} variant="outline">
          💾 Save to Profile
        </Button>
        <Button onClick={handleSaveBenchmark} variant="outline">
          🎯 Save as Benchmark
        </Button>
        <Button onClick={() => window.print()} variant="outline">
          🖨️ Print Report
        </Button>
        {onClose && (
          <Button onClick={onClose} variant="outline">
            ✕ Close
          </Button>
        )}
      </div>
    </div>
  );
}
