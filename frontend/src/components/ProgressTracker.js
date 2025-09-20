import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Target, TrendingUp, Calendar, Award, ArrowRight, Clock, Zap, Timer } from 'lucide-react';

const ProgressTracker = ({ playerData, targetGoals }) => {
  if (!playerData) return null;

  // Calculate progress percentages and timeframes
  const calculateProgress = (current, target, metric) => {
    const lowerIsBetter = ['sprint_30m', 'body_fat'];
    
    if (lowerIsBetter.includes(metric)) {
      // For metrics where lower is better (time, body fat)
      const maxStart = target * 1.5; // Assume starting point 50% worse than target
      const progress = Math.max(0, Math.min(100, ((maxStart - current) / (maxStart - target)) * 100));
      return {
        percentage: progress,
        remaining: Math.max(0, current - target),
        improving: true
      };
    } else {
      // For metrics where higher is better
      const progress = Math.max(0, Math.min(100, (current / target) * 100));
      return {
        percentage: progress,
        remaining: Math.max(0, target - current),
        improving: current >= target
      };
    }
  };

  // Sample target goals based on age category and current performance
  const getTargetGoals = () => {
    const age = playerData.age;
    const ageCategory = age >= 17 ? 'elite' : age >= 15 ? '15-16' : '12-14';
    
    // Elite target goals
    const targets = {
      'sprint_30m': 3.9,
      'yo_yo_test': 2200,
      'vo2_max': 62,
      'vertical_jump': 65,
      'body_fat': 8,
      'passing_accuracy': 90,
      'shooting_accuracy': 80,
      'ball_control': 5
    };

    return targets;
  };

  const targets = targetGoals || getTargetGoals();
  
  // Key metrics to track
  const keyMetrics = [
    { key: 'sprint_30m', label: '30m Sprint', unit: 's', icon: Zap },
    { key: 'yo_yo_test', label: 'Yo-Yo Test', unit: 'm', icon: TrendingUp },
    { key: 'vo2_max', label: 'VO2 Max', unit: 'ml/kg/min', icon: Target },
    { key: 'passing_accuracy', label: 'Passing Accuracy', unit: '%', icon: Award },
    { key: 'shooting_accuracy', label: 'Shooting Accuracy', unit: '%', icon: Target },
    { key: 'ball_control', label: 'Ball Control', unit: '/5', icon: Award }
  ];

  // Calculate estimated timeframes
  const getTimeframe = (progressPercentage) => {
    if (progressPercentage >= 90) return '2-4 weeks';
    if (progressPercentage >= 70) return '6-8 weeks';
    if (progressPercentage >= 50) return '10-12 weeks';
    if (progressPercentage >= 30) return '16-20 weeks';
    return '24+ weeks';
  };

  return (
    <div className="space-y-6">
      {/* Overall Progress Overview */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-3">
            <Target className="w-6 h-6 text-[--primary-blue]" />
            Performance Progress Tracking
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {keyMetrics.map((metric) => {
              const current = playerData[metric.key];
              const target = targets[metric.key];
              
              if (!current || !target) return null;

              const progress = calculateProgress(current, target, metric.key);
              const timeframe = getTimeframe(progress.percentage);
              
              return (
                <div key={metric.key} className="professional-card p-5">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <metric.icon className="w-5 h-5 text-[--primary-blue]" />
                      <span className="font-semibold text-lg">{metric.label}</span>
                    </div>
                    <span className={`badge-${progress.improving && progress.percentage > 70 ? 'good' : progress.percentage > 50 ? 'average' : 'poor'}`}>
                      {progress.percentage.toFixed(0)}%
                    </span>
                  </div>
                  
                  {/* Progress Bar */}
                  <div className="mb-4">
                    <div className="progress-container mb-2">
                      <div 
                        className="progress-bar"
                        style={{ width: `${progress.percentage}%` }}
                      />
                    </div>
                    <div className="flex justify-between text-sm text-[--text-muted]">
                      <span>0</span>
                      <span>{progress.percentage.toFixed(0)}%</span>
                      <span>100%</span>
                    </div>
                  </div>

                  {/* Current vs Target */}
                  <div className="grid grid-cols-2 gap-4 mb-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[--primary-blue]">
                        {current}{metric.unit}
                      </div>
                      <div className="text-sm text-[--text-muted]">Current</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-[--secondary-gold]">
                        {target}{metric.unit}
                      </div>
                      <div className="text-sm text-[--text-muted]">Target</div>
                    </div>
                  </div>

                  {/* Improvement Needed */}
                  <div className="flex items-center justify-between text-sm pt-4 border-t border-[--border-color]">
                    <span className="text-[--text-secondary]">
                      Gap: {progress.remaining.toFixed(1)}{metric.unit}
                    </span>
                    <div className="flex items-center text-[--secondary-gold]">
                      <Clock className="w-4 h-4 mr-1" />
                      {timeframe}
                    </div>
                  </div>
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      {/* Weekly Training Focus */}
      <Card className="professional-card">
        <CardHeader>
          <CardTitle className="text-xl flex items-center gap-3">
            <Calendar className="w-5 h-5 text-[--primary-blue]" />
            Weekly Training Focus
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-6">
            {/* Priority Areas */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="professional-card p-5 border-l-4 border-l-[--error]">
                <h4 className="font-semibold text-lg mb-3 text-[--error]">🎯 Priority This Week</h4>
                <div className="space-y-3">
                  {keyMetrics
                    .filter(metric => {
                      const current = playerData[metric.key];
                      const target = targets[metric.key];
                      if (!current || !target) return false;
                      const progress = calculateProgress(current, target, metric.key);
                      return progress.percentage < 70;
                    })
                    .slice(0, 2)
                    .map(metric => (
                      <div key={metric.key} className="flex items-center justify-between p-3 bg-[--light-bg] rounded-lg">
                        <span className="font-medium">{metric.label}</span>
                        <ArrowRight className="w-4 h-4 text-[--error]" />
                      </div>
                    ))
                  }
                </div>
              </div>

              <div className="professional-card p-5 border-l-4 border-l-[--success]">
                <h4 className="font-semibold text-lg mb-3 text-[--success]">⚡ Maintain Excellence</h4>
                <div className="space-y-3">
                  {keyMetrics
                    .filter(metric => {
                      const current = playerData[metric.key];
                      const target = targets[metric.key];
                      if (!current || !target) return false;
                      const progress = calculateProgress(current, target, metric.key);
                      return progress.percentage >= 85;
                    })
                    .slice(0, 2)
                    .map(metric => (
                      <div key={metric.key} className="flex items-center justify-between p-3 bg-[--light-bg] rounded-lg">
                        <span className="font-medium">{metric.label}</span>
                        <Award className="w-4 h-4 text-[--success]" />
                      </div>
                    ))
                  }
                </div>
              </div>
            </div>

            {/* Progress Timeline */}
            <div className="professional-card p-5 border-l-4 border-l-[--primary-blue]">
              <h4 className="font-semibold text-lg mb-4 text-[--primary-blue]">📅 4-Week Development Plan</h4>
              <div className="space-y-4">
                {[1, 2, 3, 4].map(week => (
                  <div key={week} className="flex items-center gap-4">
                    <div className="progress-ring w-12 h-12 text-sm">
                      {week}
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-lg mb-1">
                        Week {week}: {
                          week === 1 ? 'Foundation Building' :
                          week === 2 ? 'Skill Enhancement' :
                          week === 3 ? 'Performance Optimization' :
                          'Assessment & Planning'
                        }
                      </div>
                      <div className="text-[--text-muted] text-sm">
                        {week === 1 ? 'Focus on fundamental techniques and conditioning base' :
                         week === 2 ? 'Advanced skill development and tactical understanding' :
                         week === 3 ? 'High-intensity training and competitive preparation' :
                         'Performance evaluation and goal setting for next cycle'}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default ProgressTracker;