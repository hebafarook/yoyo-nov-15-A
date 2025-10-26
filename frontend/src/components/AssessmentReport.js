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

const AssessmentReport = ({ playerData, previousAssessments = [], showComparison = true, isStartupReport = false }) => {
  const [reportData, setReportData] = useState(null);
  const [comparisonData, setComparisonData] = useState(null);

  useEffect(() => {
    if (playerData) {
      generateReportData();
      if (showComparison && previousAssessments.length > 0) {
        generateComparisonData();
      }
    }
  }, [playerData, previousAssessments]);

  const generateReportData = () => {
    const ageCategory = getAgeCategory(playerData.age);
    const standards = YOUTH_HANDBOOK_STANDARDS[ageCategory];
    
    // Calculate category scores
    const physicalScore = calculateCategoryScore('physical', playerData, standards);
    const technicalScore = calculateCategoryScore('technical', playerData, standards);
    const tacticalScore = calculateCategoryScore('tactical', playerData, standards);
    const psychologicalScore = calculateCategoryScore('psychological', playerData, standards);
    
    // Calculate overall score
    const overallScore = calculateOverallScore(playerData);
    
    // Determine performance level
    const performanceLevel = getPerformanceLevel(overallScore);
    
    // Identify strengths and weaknesses
    const analysis = analyzePerformance(playerData, standards);
    
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
      recommendations: generateRecommendations(analysis, performanceLevel),
      nextAssessmentDate: getNextAssessmentDate(),
      rawMetrics: extractRawMetrics(playerData)
    };

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

    return validMetrics > 0 ? (totalScore / validMetrics) * 20 : 0; // Convert to 100-point scale
  };

  const getPerformanceScore = (performance) => {
    const scores = {
      excellent: 5,
      good: 4,
      average: 3,
      poor: 2
    };
    return scores[performance] || 2;
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

  const generateRecommendations = (analysis, performanceLevel) => {
    const recommendations = [];

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
    window.print();
  };

  const downloadReport = () => {
    // Create a formatted text version for download
    if (!reportData) return;

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
    if (!reportData || !playerData) return;

    try {
      // Import useAuth hook
      const { useAuth } = await import('../contexts/AuthContext');
      const { saveReport, isAuthenticated } = useAuth();

      if (!isAuthenticated) {
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

      const result = await saveReport(saveData);
      if (result.success) {
        alert('Report saved to your profile successfully!');
      } else {
        alert('Failed to save report: ' + result.error);
      }
    } catch (error) {
      console.error('Error saving report:', error);
      alert('Failed to save report. Please try again.');
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
      <div className="flex gap-4 print:hidden">
        <Button onClick={printReport} className="flex-1">
          <Printer className="w-4 h-4 mr-2" />
          Print Report
        </Button>
        <Button onClick={downloadReport} variant="outline" className="flex-1">
          <Download className="w-4 h-4 mr-2" />
          Download Report
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