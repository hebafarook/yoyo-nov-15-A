import React, { useState, useEffect } from 'react';
import { Card, CardHeader, CardTitle, CardContent } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { 
  FileText, Printer, Download, TrendingUp, TrendingDown, 
  Minus, Target, Calendar, User, Award, BarChart3,
  Clock, Zap, Brain, Eye, Activity, Trophy, Bookmark
} from 'lucide-react';
import { YOUTH_HANDBOOK_STANDARDS, evaluatePerformance, getAgeCategory, calculateOverallScore } from '../AssessmentStandards';
import { useAuth } from '../contexts/AuthContext';
import axios from 'axios';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const AssessmentReport = ({ playerData, previousAssessments = [], showComparison = true, isStartupReport = false }) => {
  const [reportData, setReportData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);
  const [selectedTrainingFrequency, setSelectedTrainingFrequency] = useState(null);
  const [isGeneratingProgram, setIsGeneratingProgram] = useState(false);
  
  // Use auth hook at component level
  const { saveReport, saveBenchmark, isAuthenticated, user } = useAuth();

  useEffect(() => {
    console.log('🔄 AssessmentReport useEffect triggered');
    console.log('playerData:', playerData);
    if (playerData) {
      console.log('✅ Generating report data...');
      generateReportData();
      if (showComparison && previousAssessments.length > 0) {
        generateComparisonData();
      }
    }
  }, [playerData, previousAssessments, showComparison]);

  const generateReportData = () => {
    console.log('📊 Starting generateReportData...');
    const ageCategory = getAgeCategory(playerData.age);
    const standards = YOUTH_HANDBOOK_STANDARDS[ageCategory];
    
    // Calculate category scores
    const physicalScore = calculateCategoryScore('physical', playerData, standards);
    const technicalScore = calculateCategoryScore('technical', playerData, standards);
    const tacticalScore = calculateCategoryScore('tactical', playerData, standards);
    const psychologicalScore = calculateCategoryScore('psychological', playerData, standards);
    
    console.log('📈 Category scores:', { physical: physicalScore, technical: technicalScore, tactical: tacticalScore, psychological: psychologicalScore });
    
    // Calculate overall score
    const overallScore = calculateOverallScore(playerData);
    
    // Determine performance level
    const performanceLevel = getPerformanceLevel(overallScore);
    
    // Identify strengths and weaknesses
    const analysis = analyzePerformance(playerData, standards);
    
    // Calculate program duration with category gaps
    const programDuration = calculateProgramDuration(analysis, performanceLevel, playerData);
    console.log('📅 Program duration calculated:', programDuration);
    console.log('🎯 Category gaps:', programDuration.categoryGaps);
    
    const report = {
      playerInfo: {
        name: playerData.player_name,
        age: playerData.age,
        position: playerData.position,
        ageCategory: ageCategory,
        assessmentDate: new Date().toLocaleDateString(),
        assessmentTime: new Date().toLocaleTimeString()
      },
      scores: {
        overall: Math.round(overallScore),
        physical: Math.round(physicalScore),
        technical: Math.round(technicalScore),
        tactical: Math.round(tacticalScore),
        psychological: Math.round(psychologicalScore)
      },
      performanceLevel,
      analysis,
      recommendations: generateRecommendations(analysis, performanceLevel, playerData),
      programDuration: programDuration,
      nextAssessmentDate: getNextAssessmentDate(),
      rawMetrics: extractRawMetrics(playerData)
    };

    console.log('✅ Report data generated:', report);
    setReportData(report);
  };

  const calculateCategoryScore = (category, data, standards) => {
    const categoryMetrics = {
      physical: ['sprint_30m', 'yo_yo_test', 'vo2_max', 'vertical_jump', 'body_fat'],
      technical: ['ball_control', 'passing_accuracy', 'dribbling_success', 'shooting_accuracy', 'defensive_duels'],
      tactical: ['game_intelligence', 'positioning', 'decision_making'],
      psychological: ['coachability', 'mental_toughness']
    };

    const metrics = categoryMetrics[category];
    let totalScore = 0;
    let validMetrics = 0;

    metrics.forEach(metric => {
      const value = data[metric];
      if (value !== undefined && value !== null && value !== '') {
        const performance = evaluatePerformance(parseFloat(value), metric, data.age);
        const score = getPerformanceScore(performance);
        totalScore += score;
        validMetrics++;
      }
    });

    // Calculate average score and convert to percentage (0-100 scale)
    // Score range: 1-5, so we need: (avgScore / 5) * 100
    const avgScore = validMetrics > 0 ? totalScore / validMetrics : 0;
    const percentage = (avgScore / 5) * 100;
    return Math.round(percentage);
  };

  const getPerformanceScore = (performance) => {
    const scores = {
      excellent: 5,
      good: 4,
      average: 3,
      'below average': 2,
      poor: 1
    };
    return scores[performance] || 3; // Default to average if unknown
  };

  const getPerformanceLevel = (overallScore) => {
    if (overallScore >= 85) return { level: 'Elite', color: 'text-purple-600', bgColor: 'bg-purple-50' };
    if (overallScore >= 75) return { level: 'Advanced', color: 'text-blue-600', bgColor: 'bg-blue-50' };
    if (overallScore >= 65) return { level: 'Intermediate', color: 'text-green-600', bgColor: 'bg-green-50' };
    if (overallScore >= 50) return { level: 'Developing', color: 'text-yellow-600', bgColor: 'bg-yellow-50' };
    return { level: 'Beginner', color: 'text-red-600', bgColor: 'bg-red-50' };
  };

  const analyzePerformance = (data, standards) => {
    const strengths = [];
    const weaknesses = [];
    const improvements = [];

    // Analyze each metric
    const allMetrics = {
      'Sprint Speed (30m)': { value: data.sprint_30m, key: 'sprint_30m', unit: 's', lowerIsBetter: true },
      'Endurance (Yo-Yo)': { value: data.yo_yo_test, key: 'yo_yo_test', unit: 'm', lowerIsBetter: false },
      'VO2 Max': { value: data.vo2_max, key: 'vo2_max', unit: 'ml/kg/min', lowerIsBetter: false },
      'Vertical Jump': { value: data.vertical_jump, key: 'vertical_jump', unit: 'cm', lowerIsBetter: false },
      'Body Fat': { value: data.body_fat, key: 'body_fat', unit: '%', lowerIsBetter: true },
      'Ball Control': { value: data.ball_control, key: 'ball_control', unit: '/5', lowerIsBetter: false },
      'Passing Accuracy': { value: data.passing_accuracy, key: 'passing_accuracy', unit: '%', lowerIsBetter: false },
      'Game Intelligence': { value: data.game_intelligence, key: 'game_intelligence', unit: '/5', lowerIsBetter: false },
      'Mental Toughness': { value: data.mental_toughness, key: 'mental_toughness', unit: '/5', lowerIsBetter: false }
    };

    Object.entries(allMetrics).forEach(([name, metric]) => {
      if (metric.value !== undefined && metric.value !== null && metric.value !== '') {
        const performance = evaluatePerformance(parseFloat(metric.value), metric.key, data.age);
        
        if (performance === 'excellent') {
          strengths.push(`${name}: ${metric.value}${metric.unit} (Excellent)`);
        } else if (performance === 'poor') {
          weaknesses.push(`${name}: ${metric.value}${metric.unit} (Needs Improvement)`);
        }
      }
    });

    return { strengths, weaknesses, improvements };
  };

  const generateRecommendations = (analysis, performanceLevel, playerData) => {
    const recommendations = [];
    
    // Dynamic recommendations based on actual weaknesses

    // Based on performance level
    if (performanceLevel.level === 'Elite') {
      recommendations.push('Focus on maintaining peak performance and mental preparation for competitions');
      recommendations.push('Consider advanced tactical training and leadership development');
    } else if (performanceLevel.level === 'Advanced') {
      recommendations.push('Work on consistency in high-pressure situations');
      recommendations.push('Focus on specialized position-specific skills');
    } else if (performanceLevel.level === 'Intermediate') {
      recommendations.push('Increase training intensity and focus on technical refinement');
      recommendations.push('Develop tactical understanding through match analysis');
    } else {
      recommendations.push('Focus on fundamental skills development and fitness base');
      recommendations.push('Increase training frequency and consistency');
    }

    // Based on weaknesses
    if (analysis.weaknesses.length > 0) {
      analysis.weaknesses.forEach(weakness => {
        if (weakness.includes('Sprint Speed')) {
          recommendations.push('Implement speed training: 30m sprints, acceleration drills');
        }
        if (weakness.includes('Endurance')) {
          recommendations.push('Increase cardiovascular training: interval running, yo-yo test practice');
        }
        if (weakness.includes('Ball Control')) {
          recommendations.push('Daily ball work: cone weaving, first touch drills');
        }
        if (weakness.includes('Mental Toughness')) {
          recommendations.push('Mental training: visualization, pressure situation practice');
        }
      });
    }

    return recommendations.slice(0, 5); // Limit to top 5 recommendations
  };

  const calculateProgramDuration = (analysis, performanceLevel, playerData) => {
    // Calculate gaps from excellence for each category
    const categoryGaps = {
      physical: calculateCategoryGap('physical', playerData),
      technical: calculateCategoryGap('technical', playerData),
      tactical: calculateCategoryGap('tactical', playerData),
      psychological: calculateCategoryGap('psychological', playerData)
    };

    // Average gap percentage
    const avgGap = (categoryGaps.physical + categoryGaps.technical + categoryGaps.tactical + categoryGaps.psychological) / 4;
    
    // Determine program length based on gap
    let totalWeeks = 8; // minimum
    if (avgGap > 40) totalWeeks = 16;
    else if (avgGap > 25) totalWeeks = 12;
    else if (avgGap > 15) totalWeeks = 10;

    // Define phases
    const phases = [];
    
    if (avgGap > 30) {
      // Need foundation phase for significant gaps
      phases.push({
        name: 'Foundation Phase',
        weeks: Math.ceil(totalWeeks * 0.35),
        focus: ['Physical conditioning', 'Basic technique', 'Movement patterns'],
        objectives: 'Build fitness base and correct fundamental movements'
      });
    }

    phases.push({
      name: 'Development Phase',
      weeks: Math.ceil(totalWeeks * (avgGap > 30 ? 0.40 : 0.50)),
      focus: ['Skill refinement', 'Tactical training', 'Progressive overload'],
      objectives: 'Improve weak areas and integrate skills'
    });

    phases.push({
      name: 'Peak Performance Phase',
      weeks: Math.floor(totalWeeks * (avgGap > 30 ? 0.25 : 0.50)),
      focus: ['Match scenarios', 'High intensity', 'Competition prep'],
      objectives: 'Maximize performance and game readiness'
    });

    // Calculate training days for different frequencies
    const trainingOptions = [
      {
        daysPerWeek: 3,
        totalDays: totalWeeks * 3,
        schedule: 'Mon/Wed/Fri or Tue/Thu/Sat',
        intensity: 'Moderate - Good for beginners',
        phases: phases.map(p => ({ ...p, trainingDays: p.weeks * 3 }))
      },
      {
        daysPerWeek: 4,
        totalDays: totalWeeks * 4,
        schedule: 'Mon/Tue/Thu/Sat',
        intensity: 'High - Recommended for development',
        phases: phases.map(p => ({ ...p, trainingDays: p.weeks * 4 }))
      },
      {
        daysPerWeek: 5,
        totalDays: totalWeeks * 5,
        schedule: 'Mon-Fri',
        intensity: 'Maximum - For elite progression',
        phases: phases.map(p => ({ ...p, trainingDays: p.weeks * 5 }))
      }
    ];

    // Recommended option based on current level
    let recommendedOption = 1; // 4 days default
    if (performanceLevel.score < 40) recommendedOption = 0; // 3 days for beginners
    else if (performanceLevel.score >= 70) recommendedOption = 2; // 5 days for advanced

    return {
      totalWeeks,
      averageGap: Math.round(avgGap),
      categoryGaps,
      phases,
      trainingOptions,
      recommendedOption,
      targetLevel: getNextPerformanceLevel(performanceLevel.score)
    };
  };

  const calculateCategoryGap = (category, playerData) => {
    const ageCategory = getAgeCategory(playerData.age);
    const standards = YOUTH_HANDBOOK_STANDARDS[ageCategory];
    
    const metrics = {
      physical: ['sprint_30m', 'yo_yo_test', 'vo2_max', 'vertical_jump', 'body_fat'],
      technical: ['ball_control', 'passing_accuracy', 'dribbling_success', 'shooting_accuracy', 'defensive_duels'],
      tactical: ['game_intelligence', 'positioning', 'decision_making'],
      psychological: ['coachability', 'mental_toughness']
    };
    
    const categoryMetrics = metrics[category];
    let totalGap = 0;
    let validMetrics = 0;
    
    categoryMetrics.forEach(metric => {
      const value = playerData[metric];
      if (value !== undefined && value !== null) {
        const performance = evaluatePerformance(value, metric, playerData.age);
        const performanceScore = getPerformanceScore(performance);
        const gap = 5 - performanceScore; // Gap from excellence (5)
        totalGap += gap;
        validMetrics++;
      }
    });
    
    const avgGap = validMetrics > 0 ? totalGap / validMetrics : 0;
    return (avgGap / 5) * 100; // Convert to percentage
  };

  const getNextPerformanceLevel = (currentScore) => {
    if (currentScore < 40) return 'Intermediate Level';
    if (currentScore < 60) return 'Advanced Level';
    if (currentScore < 80) return 'Elite Level';
    return 'Professional Level';
  };

  const extractRawMetrics = (data) => {
    return {
      physical: {
        'Sprint 30m': `${data.sprint_30m}s`,
        'Yo-Yo Test': `${data.yo_yo_test}m`,
        'VO2 Max': `${data.vo2_max} ml/kg/min`,
        'Vertical Jump': `${data.vertical_jump}cm`,
        'Body Fat': `${data.body_fat}%`
      },
      technical: {
        'Ball Control': `${data.ball_control}/5`,
        'Passing Accuracy': `${data.passing_accuracy}%`,
        'Dribbling Success': `${data.dribbling_success}%`,
        'Shooting Accuracy': `${data.shooting_accuracy}%`,
        'Defensive Duels': `${data.defensive_duels}%`
      },
      tactical: {
        'Game Intelligence': `${data.game_intelligence}/5`,
        'Positioning': `${data.positioning}/5`,
        'Decision Making': `${data.decision_making}/5`
      },
      psychological: {
        'Coachability': `${data.coachability}/5`,
        'Mental Toughness': `${data.mental_toughness}/5`
      }
    };
  };

  const generateComparisonData = () => {
    if (previousAssessments.length === 0) return;

    const latest = previousAssessments[0];
    const comparison = {
      improvements: [],
      declines: [],
      maintained: []
    };

    // Compare key metrics
    const compareMetrics = [
      { key: 'sprint_30m', name: 'Sprint Speed', unit: 's', lowerIsBetter: true },
      { key: 'yo_yo_test', name: 'Endurance', unit: 'm', lowerIsBetter: false },
      { key: 'vo2_max', name: 'VO2 Max', unit: 'ml/kg/min', lowerIsBetter: false },
      { key: 'ball_control', name: 'Ball Control', unit: '/5', lowerIsBetter: false },
      { key: 'passing_accuracy', name: 'Passing', unit: '%', lowerIsBetter: false }
    ];

    compareMetrics.forEach(metric => {
      const currentValue = parseFloat(playerData[metric.key]);
      const previousValue = parseFloat(latest[metric.key]);

      if (!isNaN(currentValue) && !isNaN(previousValue)) {
        const difference = currentValue - previousValue;
        const percentChange = Math.abs((difference / previousValue) * 100);

        let changeType = 'maintained';
        if (percentChange > 2) { // Only consider significant changes
          if (metric.lowerIsBetter) {
            changeType = difference < 0 ? 'improvements' : 'declines';
          } else {
            changeType = difference > 0 ? 'improvements' : 'declines';
          }
        }

        comparison[changeType].push({
          name: metric.name,
          current: currentValue,
          previous: previousValue,
          change: difference,
          percentChange: percentChange.toFixed(1),
          unit: metric.unit
        });
      }
    });

    setComparisonData(comparison);
  };

  const getNextAssessmentDate = () => {
    const nextDate = new Date();
    nextDate.setDate(nextDate.getDate() + 28); // 4 weeks
    return nextDate.toLocaleDateString();
  };

  const printReport = () => {
    console.log('🖨️ Print button clicked');
    try {
      window.print();
      console.log('✅ Print dialog opened');
    } catch (error) {
      console.error('❌ Print error:', error);
      alert('Failed to open print dialog: ' + error.message);
    }
  };

  const downloadReport = () => {
    console.log('📥 Download button clicked');
    console.log('reportData:', reportData);
    // Create a formatted text version for download
    if (!reportData) {
      console.error('❌ No report data available');
      alert('No report data available to download');
      return;
    }

    const reportText = generateTextReport(reportData, comparisonData);
    const blob = new Blob([reportText], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${reportData.playerInfo.name}_Assessment_Report_${reportData.playerInfo.assessmentDate.replace(/\//g, '-')}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  const saveToProfile = async () => {
    console.log('💾 Save to Profile button clicked');
    console.log('reportData:', reportData);
    console.log('playerData:', playerData);
    console.log('isAuthenticated:', isAuthenticated);
    console.log('user:', user);
    
    if (!reportData || !playerData) {
      console.error('❌ Missing report or player data');
      alert('Missing report or player data. Please try again.');
      return;
    }

    try {
      if (!isAuthenticated) {
        console.error('❌ User not authenticated');
        alert('Please login to save reports to your profile');
        return;
      }

      const saveData = {
        player_name: reportData.playerInfo.name,
        assessment_id: playerData.id || 'unknown',
        report_data: {
          playerData,
          previousAssessments,
          reportData,
          comparisonData
        },
        report_type: isStartupReport ? 'startup' : 'milestone',
        title: `Assessment Report - ${reportData.playerInfo.name} (${reportData.playerInfo.assessmentDate})`,
        notes: `Overall Score: ${reportData.scores.overall}/100 - ${reportData.performanceLevel.level}`
      };

      console.log('📤 Sending save request:', saveData);
      const result = await saveReport(saveData);
      console.log('📥 Save result:', result);
      
      if (result.success) {
        console.log('✅ Report saved successfully');
        alert('✅ Report saved to your profile successfully!');
      } else {
        console.error('❌ Save failed:', result.error);
        alert('Failed to save report: ' + result.error);
      }
    } catch (error) {
      console.error('❌ Error saving report:', error);
      console.error('Error details:', error.response?.data);
      alert('Failed to save report. Please try again. Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const saveBenchmarkToProfile = async () => {
    console.log('🎯 Save as Benchmark button clicked');
    console.log('reportData:', reportData);
    console.log('playerData:', playerData);
    console.log('isAuthenticated:', isAuthenticated);
    console.log('user:', user);
    
    if (!reportData || !playerData) {
      console.error('❌ Missing report or player data');
      alert('Missing report or player data. Please try again.');
      return;
    }

    try {
      if (!isAuthenticated || !user) {
        console.error('❌ User not authenticated');
        alert('Please login to save benchmarks to your profile');
        return;
      }

      const benchmarkData = {
        player_name: reportData.playerInfo.name,
        assessment_id: playerData.id || 'unknown',
        age: playerData.age,
        position: playerData.position,
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
        // Calculated metrics
        overall_score: reportData.scores.overall,
        performance_level: reportData.performanceLevel.level,
        benchmark_type: 'regular',
        notes: `Assessment benchmark - ${reportData.playerInfo.assessmentDate}`
      };

      console.log('📤 Sending benchmark request:', benchmarkData);
      const result = await saveBenchmark(benchmarkData);
      console.log('📥 Benchmark result:', result);
      
      if (result.success) {
        const benchmark = result.benchmark;
        console.log('✅ Benchmark saved:', benchmark);
        if (benchmark.is_baseline) {
          alert('✅ Baseline benchmark saved successfully! This is your first benchmark and will be used as a reference for future progress tracking.');
        } else {
          alert('✅ Benchmark saved successfully! You can view your progress in the Saved Reports section.');
        }
      } else {
        console.error('❌ Save failed:', result.error);
        alert('Failed to save benchmark: ' + result.error);
      }
    } catch (error) {
      console.error('❌ Error saving benchmark:', error);
      console.error('Error details:', error.response?.data);
      alert('Failed to save benchmark. Please try again. Error: ' + (error.response?.data?.detail || error.message));
    }
  };

  const generateProgram = async (trainingFrequency) => {
    if (!reportData || !playerData) return;

    try {
      setIsGeneratingProgram(true);
      
      // Extract weakness names as strings
      const weaknessNames = reportData.analysis.weaknesses
        .slice(0, 3)
        .map(w => w.area || w.metric || 'general improvement');
      
      // Build program objectives as array of strings
      const objectives = [
        `Improve ${reportData.performanceLevel.level} to ${reportData.programDuration.targetLevel}`,
        `Focus on ${weaknessNames.join(', ')}`,
        'Build comprehensive soccer skills',
        'Achieve peak performance'
      ];
      
      const programData = {
        player_id: playerData.player_name,
        program_name: `${playerData.player_name}'s ${trainingFrequency}-Day Training Program`,
        total_duration_weeks: reportData.programDuration.totalWeeks,
        program_objectives: objectives,
        assessment_interval_weeks: 4,
        training_frequency: trainingFrequency // 3, 4, or 5 days per week
      };
      
      console.log('✅ Generating program with data:', JSON.stringify(programData, null, 2));
      
      const response = await axios.post(`${API}/periodized-programs`, programData);
      
      console.log('✅ Program generated successfully:', response.data);
      
      alert(`✅ Training program generated successfully!\n\n📅 ${trainingFrequency} days per week\n⏱️ ${reportData.programDuration.totalWeeks} weeks total\n\n➡️ Go to the Training Programs tab to view your personalized program.`);
      
    } catch (error) {
      console.error('❌ Error generating program:', error);
      const errorDetail = error.response?.data?.detail;
      let errorMessage = 'Failed to generate program.';
      
      if (typeof errorDetail === 'string') {
        errorMessage = errorDetail;
      } else if (Array.isArray(errorDetail)) {
        errorMessage = errorDetail.map(e => `${e.loc?.join('.')}: ${e.msg}`).join('\n');
      } else if (error.message) {
        errorMessage = error.message;
      }
      
      alert(`❌ ${errorMessage}\n\nPlease try again or contact support.`);
    } finally {
      setIsGeneratingProgram(false);
    }
  };

  const generateTextReport = (report, comparison) => {
    let text = `
SOCCER PLAYER ASSESSMENT REPORT
${isStartupReport ? '*** PROGRAM STARTUP REPORT ***' : '*** MILESTONE ASSESSMENT ***'}
===============================================

PLAYER INFORMATION:
- Name: ${report.playerInfo.name}
- Age: ${report.playerInfo.age} years (${report.playerInfo.ageCategory} category)
- Position: ${report.playerInfo.position}
- Assessment Date: ${report.playerInfo.assessmentDate}
- Assessment Time: ${report.playerInfo.assessmentTime}

OVERALL PERFORMANCE SUMMARY:
- Overall Score: ${report.scores.overall}/100
- Performance Level: ${report.performanceLevel.level}
- Physical Score: ${report.scores.physical}/100
- Technical Score: ${report.scores.technical}/100
- Tactical Score: ${report.scores.tactical}/100
- Psychological Score: ${report.scores.psychological}/100

DETAILED METRICS:
`;

    // Add detailed metrics
    Object.entries(report.rawMetrics).forEach(([category, metrics]) => {
      text += `\n${category.toUpperCase()}:\n`;
      Object.entries(metrics).forEach(([metric, value]) => {
        text += `  - ${metric}: ${value}\n`;
      });
    });

    // Add strengths and weaknesses
    if (report.analysis.strengths.length > 0) {
      text += `\nSTRENGTHS:\n`;
      report.analysis.strengths.forEach(strength => {
        text += `  ✓ ${strength}\n`;
      });
    }

    if (report.analysis.weaknesses.length > 0) {
      text += `\nAREAS FOR IMPROVEMENT:\n`;
      report.analysis.weaknesses.forEach(weakness => {
        text += `  ! ${weakness}\n`;
      });
    }

    // Add comparison data
    if (comparison) {
      text += `\nPROGRESS COMPARISON:\n`;
      
      if (comparison.improvements.length > 0) {
        text += `\nIMPROVEMENTS:\n`;
        comparison.improvements.forEach(item => {
          text += `  ↑ ${item.name}: ${item.previous}${item.unit} → ${item.current}${item.unit} (+${item.percentChange}%)\n`;
        });
      }

      if (comparison.declines.length > 0) {
        text += `\nAREAS NEEDING ATTENTION:\n`;
        comparison.declines.forEach(item => {
          text += `  ↓ ${item.name}: ${item.previous}${item.unit} → ${item.current}${item.unit} (-${item.percentChange}%)\n`;
        });
      }
    }

    // Add recommendations
    text += `\nRECOMMendations:\n`;
    report.recommendations.forEach((rec, index) => {
      text += `  ${index + 1}. ${rec}\n`;
    });

    text += `\nNEXT ASSESSMENT SCHEDULED: ${report.nextAssessmentDate}\n`;
    text += `\nReport generated by Yo-Yo Elite Soccer Player AI Coach\n`;
    text += `===============================================\n`;

    return text;
  };

  if (!reportData) {
    return <div>Loading assessment report...</div>;
  }

  return (
    <div className="assessment-report max-w-4xl mx-auto space-y-6 print:space-y-4">
      {/* Report Header */}
      <Card className="professional-card print:shadow-none">
        <CardHeader className="text-center bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-t-lg">
          <div className="flex items-center justify-center gap-3 mb-2">
            <Trophy className="w-8 h-8" />
            <CardTitle className="text-2xl font-bold">
              {isStartupReport ? 'PROGRAM STARTUP REPORT' : 'MILESTONE ASSESSMENT REPORT'}
            </CardTitle>
          </div>
          <div className="text-blue-100">
            Soccer Player Performance Analysis
          </div>
        </CardHeader>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <User className="w-5 h-5 text-blue-600" />
                <div>
                  <div className="font-semibold text-lg">{reportData.playerInfo.name}</div>
                  <div className="text-sm text-gray-600">
                    {reportData.playerInfo.age} years • {reportData.playerInfo.position} • {reportData.playerInfo.ageCategory}
                  </div>
                </div>
              </div>
              <div className="flex items-center gap-2">
                <Calendar className="w-5 h-5 text-green-600" />
                <div>
                  <div className="font-medium">Assessment Date</div>
                  <div className="text-sm text-gray-600">
                    {reportData.playerInfo.assessmentDate} at {reportData.playerInfo.assessmentTime}
                  </div>
                </div>
              </div>
            </div>
            
            <div className="text-center">
              <div className={`inline-flex items-center gap-2 px-4 py-2 rounded-full ${reportData.performanceLevel.bgColor}`}>
                <Award className={`w-5 h-5 ${reportData.performanceLevel.color}`} />
                <span className={`font-bold text-lg ${reportData.performanceLevel.color}`}>
                  {reportData.performanceLevel.level}
                </span>
              </div>
              <div className="mt-2 text-3xl font-bold text-blue-600">
                {reportData.scores.overall}/100
              </div>
              <div className="text-sm text-gray-600">Overall Score</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Action Buttons */}
      <div className="flex gap-3 print:hidden">
        <Button onClick={printReport} className="flex-1">
          <Printer className="w-4 h-4 mr-2" />
          Print Report
        </Button>
        <Button onClick={downloadReport} variant="outline" className="flex-1">
          <Download className="w-4 h-4 mr-2" />
          Download
        </Button>
        <Button onClick={saveToProfile} variant="outline" className="flex-1 bg-green-50 text-green-700 hover:bg-green-100">
          <Bookmark className="w-4 h-4 mr-2" />
          Save to Profile
        </Button>
        <Button onClick={saveBenchmarkToProfile} variant="outline" className="flex-1 bg-blue-50 text-blue-700 hover:bg-blue-100">
          <Target className="w-4 h-4 mr-2" />
          Save as Benchmark
        </Button>
      </div>

      {/* Performance Scores */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <BarChart3 className="w-5 h-5" />
            Performance Breakdown
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-red-50 rounded-lg border border-red-200">
              <Activity className="w-8 h-8 mx-auto text-red-600 mb-2" />
              <div className="text-2xl font-bold text-red-800">{reportData.scores.physical}</div>
              <div className="text-sm text-red-700">Physical (20%)</div>
              <Progress value={reportData.scores.physical} className="mt-2 h-2" />
            </div>
            <div className="text-center p-4 bg-blue-50 rounded-lg border border-blue-200">
              <Target className="w-8 h-8 mx-auto text-blue-600 mb-2" />
              <div className="text-2xl font-bold text-blue-800">{reportData.scores.technical}</div>
              <div className="text-sm text-blue-700">Technical (40%)</div>
              <Progress value={reportData.scores.technical} className="mt-2 h-2" />
            </div>
            <div className="text-center p-4 bg-green-50 rounded-lg border border-green-200">
              <Eye className="w-8 h-8 mx-auto text-green-600 mb-2" />
              <div className="text-2xl font-bold text-green-800">{reportData.scores.tactical}</div>
              <div className="text-sm text-green-700">Tactical (30%)</div>
              <Progress value={reportData.scores.tactical} className="mt-2 h-2" />
            </div>
            <div className="text-center p-4 bg-purple-50 rounded-lg border border-purple-200">
              <Brain className="w-8 h-8 mx-auto text-purple-600 mb-2" />
              <div className="text-2xl font-bold text-purple-800">{reportData.scores.psychological}</div>
              <div className="text-sm text-purple-700">Mental (10%)</div>
              <Progress value={reportData.scores.psychological} className="mt-2 h-2" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Progress Comparison */}
      {comparisonData && (
        <Card className="professional-card">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <TrendingUp className="w-5 h-5" />
              Progress Comparison
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {comparisonData.improvements.length > 0 && (
                <div>
                  <h4 className="font-semibold text-green-600 mb-3 flex items-center gap-2">
                    <TrendingUp className="w-4 h-4" />
                    Improvements
                  </h4>
                  <div className="space-y-2">
                    {comparisonData.improvements.map((item, index) => (
                      <div key={index} className="p-3 bg-green-50 border border-green-200 rounded-lg">
                        <div className="font-medium">{item.name}</div>
                        <div className="text-sm text-green-700">
                          {item.previous}{item.unit} → {item.current}{item.unit}
                        </div>
                        <Badge className="bg-green-100 text-green-800 text-xs">
                          +{item.percentChange}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {comparisonData.declines.length > 0 && (
                <div>
                  <h4 className="font-semibold text-red-600 mb-3 flex items-center gap-2">
                    <TrendingDown className="w-4 h-4" />
                    Needs Attention
                  </h4>
                  <div className="space-y-2">
                    {comparisonData.declines.map((item, index) => (
                      <div key={index} className="p-3 bg-red-50 border border-red-200 rounded-lg">
                        <div className="font-medium">{item.name}</div>
                        <div className="text-sm text-red-700">
                          {item.previous}{item.unit} → {item.current}{item.unit}
                        </div>
                        <Badge className="bg-red-100 text-red-800 text-xs">
                          -{item.percentChange}%
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {comparisonData.maintained.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-600 mb-3 flex items-center gap-2">
                    <Minus className="w-4 h-4" />
                    Maintained
                  </h4>
                  <div className="space-y-2">
                    {comparisonData.maintained.map((item, index) => (
                      <div key={index} className="p-3 bg-gray-50 border border-gray-200 rounded-lg">
                        <div className="font-medium">{item.name}</div>
                        <div className="text-sm text-gray-700">
                          {item.current}{item.unit}
                        </div>
                        <Badge className="bg-gray-100 text-gray-800 text-xs">
                          Stable
                        </Badge>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Detailed Analysis */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {reportData.analysis.strengths.length > 0 && (
          <Card className="professional-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-green-600">
                <Trophy className="w-5 h-5" />
                Key Strengths
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {reportData.analysis.strengths.map((strength, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full mt-2 flex-shrink-0"></div>
                    <div className="text-sm">{strength}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}

        {reportData.analysis.weaknesses.length > 0 && (
          <Card className="professional-card">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-orange-600">
                <Target className="w-5 h-5" />
                Areas for Improvement
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                {reportData.analysis.weaknesses.map((weakness, index) => (
                  <div key={index} className="flex items-start gap-2">
                    <div className="w-2 h-2 bg-orange-500 rounded-full mt-2 flex-shrink-0"></div>
                    <div className="text-sm">{weakness}</div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Recommendations */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Zap className="w-5 h-5" />
            Training Recommendations
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {reportData.recommendations.map((recommendation, index) => (
              <div key={index} className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                <div className="w-6 h-6 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-bold flex-shrink-0">
                  {index + 1}
                </div>
                <div className="text-sm">{recommendation}</div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Suggested Program Duration */}
      {reportData.programDuration && (
        <Card className="professional-card border-2 border-purple-200 bg-gradient-to-br from-purple-50 to-blue-50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-purple-600" />
              Suggested Training Program Duration
            </CardTitle>
            <p className="text-sm text-gray-600 mt-2">
              Personalized program timeline to reach {reportData.programDuration.targetLevel} based on current performance gaps
            </p>
          </CardHeader>
          <CardContent className="space-y-6">
            {/* Overview */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                <div className="text-3xl font-bold text-purple-600">{reportData.programDuration.totalWeeks}</div>
                <div className="text-sm text-gray-600">Total Weeks</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                <div className="text-3xl font-bold text-blue-600">{reportData.programDuration.phases.length}</div>
                <div className="text-sm text-gray-600">Training Phases</div>
              </div>
              <div className="text-center p-4 bg-white rounded-lg shadow-sm">
                <div className="text-3xl font-bold text-orange-600">{reportData.programDuration.averageGap}%</div>
                <div className="text-sm text-gray-600">Performance Gap</div>
              </div>
            </div>

            {/* Training Phases */}
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <Award className="w-4 h-4" />
                Training Phases Breakdown
              </h4>
              <div className="space-y-3">
                {reportData.programDuration.phases.map((phase, idx) => (
                  <div key={idx} className="bg-white p-4 rounded-lg shadow-sm border-l-4 border-l-purple-500">
                    <div className="flex justify-between items-start mb-2">
                      <div>
                        <h5 className="font-bold text-lg">{phase.name}</h5>
                        <p className="text-sm text-gray-600">{phase.objectives}</p>
                      </div>
                      <Badge className="bg-purple-100 text-purple-800">
                        {phase.weeks} weeks
                      </Badge>
                    </div>
                    <div className="flex gap-2 flex-wrap mt-2">
                      {phase.focus.map((item, i) => (
                        <Badge key={i} variant="outline" className="text-xs">
                          {item}
                        </Badge>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Training Frequency Options */}
            <div>
              <h4 className="font-semibold mb-3 flex items-center gap-2">
                <Clock className="w-4 h-4" />
                Training Frequency Options (Select to Generate Program)
              </h4>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {reportData.programDuration.trainingOptions.map((option, idx) => (
                  <div 
                    key={idx} 
                    onClick={() => setSelectedTrainingFrequency(option.daysPerWeek)}
                    className={`p-4 rounded-lg border-2 cursor-pointer transition-all hover:shadow-lg ${
                      selectedTrainingFrequency === option.daysPerWeek
                        ? 'border-blue-600 bg-blue-50 shadow-lg transform scale-105'
                        : idx === reportData.programDuration.recommendedOption 
                        ? 'border-green-500 bg-green-50' 
                        : 'border-gray-200 bg-white hover:border-blue-300'
                    }`}
                  >
                    <div className="flex justify-between items-start mb-2">
                      {idx === reportData.programDuration.recommendedOption && (
                        <Badge className="bg-green-600">Recommended</Badge>
                      )}
                      {selectedTrainingFrequency === option.daysPerWeek && (
                        <Badge className="bg-blue-600 ml-auto">Selected ✓</Badge>
                      )}
                    </div>
                    <div className="text-2xl font-bold text-center mb-2">
                      {option.daysPerWeek} Days/Week
                    </div>
                    <div className="text-sm text-center text-gray-600 mb-3">
                      {option.schedule}
                    </div>
                    <div className="text-xs text-center mb-3 px-2 py-1 bg-blue-100 text-blue-800 rounded">
                      {option.intensity}
                    </div>
                    <div className="border-t pt-3 space-y-2">
                      <div className="text-sm">
                        <strong>Total Training Days:</strong> {option.totalDays}
                      </div>
                      {option.phases.map((p, i) => (
                        <div key={i} className="text-xs text-gray-600">
                          {p.name}: {p.trainingDays} days
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
              
              {/* Generate Program Button */}
              {selectedTrainingFrequency && (
                <div className="mt-6 p-4 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-lg">
                  <div className="flex items-center justify-between">
                    <div>
                      <h5 className="font-bold text-lg mb-1">Ready to Start Your Training?</h5>
                      <p className="text-sm text-blue-100">
                        You've selected {selectedTrainingFrequency} days per week training. 
                        Click to generate your personalized {reportData.programDuration.totalWeeks}-week program!
                      </p>
                    </div>
                    <Button 
                      onClick={() => generateProgram(selectedTrainingFrequency)}
                      disabled={isGeneratingProgram}
                      className="bg-white text-blue-600 hover:bg-blue-50 font-bold px-6 py-3 ml-4"
                    >
                      {isGeneratingProgram ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                          Generating...
                        </>
                      ) : (
                        <>
                          <Target className="w-5 h-5 mr-2" />
                          Generate My Program
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              )}
            </div>

            {/* Category Gaps */}
            <div className="bg-white p-4 rounded-lg">
              <h4 className="font-semibold mb-3">Performance Gaps by Category</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div className="text-center">
                  <div className="text-xl font-bold text-red-600">
                    {Math.round(reportData.programDuration.categoryGaps.physical)}%
                  </div>
                  <div className="text-xs text-gray-600">Physical</div>
                  <Progress value={100 - reportData.programDuration.categoryGaps.physical} className="h-2 mt-1" />
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-blue-600">
                    {Math.round(reportData.programDuration.categoryGaps.technical)}%
                  </div>
                  <div className="text-xs text-gray-600">Technical</div>
                  <Progress value={100 - reportData.programDuration.categoryGaps.technical} className="h-2 mt-1" />
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-green-600">
                    {Math.round(reportData.programDuration.categoryGaps.tactical)}%
                  </div>
                  <div className="text-xs text-gray-600">Tactical</div>
                  <Progress value={100 - reportData.programDuration.categoryGaps.tactical} className="h-2 mt-1" />
                </div>
                <div className="text-center">
                  <div className="text-xl font-bold text-purple-600">
                    {Math.round(reportData.programDuration.categoryGaps.psychological)}%
                  </div>
                  <div className="text-xs text-gray-600">Mental</div>
                  <Progress value={100 - reportData.programDuration.categoryGaps.psychological} className="h-2 mt-1" />
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Next Steps */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Clock className="w-5 h-5" />
            Next Steps
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h4 className="font-semibold mb-2">Immediate Actions:</h4>
              <ul className="space-y-1 text-sm">
                <li>• Begin personalized training program</li>
                <li>• Focus on identified weaknesses</li>
                <li>• Track daily progress</li>
                <li>• Maintain strength areas</li>
              </ul>
            </div>
            <div>
              <h4 className="font-semibold mb-2">Next Assessment:</h4>
              <div className="p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
                <div className="font-medium text-yellow-800">Scheduled Date:</div>
                <div className="text-yellow-700">{reportData.nextAssessmentDate}</div>
                <div className="text-sm text-yellow-600 mt-1">
                  Track progress over the next 4 weeks
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Footer */}
      <div className="text-center text-sm text-gray-500 border-t pt-4">
        <div>Report generated by Yo-Yo Elite Soccer Player AI Coach</div>
        <div>Professional Player Development System</div>
      </div>
    </div>
  );
};

export default AssessmentReport;