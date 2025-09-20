import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/card';
import { Badge } from './ui/badge';
import { Progress } from './ui/progress';
import { Target, TrendingUp, Calendar, Award, ArrowRight, Clock, Zap } from 'lucide-react';

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
    { key: 'sprint_30m', label: '30m Sprint', unit: 's', icon: Zap, color: 'text-royal-red' },
    { key: 'yo_yo_test', label: 'Yo-Yo Test', unit: 'm', icon: TrendingUp, color: 'text-royal-blue' },
    { key: 'vo2_max', label: 'VO2 Max', unit: 'ml/kg/min', icon: Target, color: 'text-royal-gold' },
    { key: 'passing_accuracy', label: 'Passing', unit: '%', icon: Award, color: 'text-royal-blue' },
    { key: 'shooting_accuracy', label: 'Shooting', unit: '%', icon: Target, color: 'text-royal-red' },
    { key: 'ball_control', label: 'Ball Control', unit: '/5', icon: Award, color: 'text-royal-gold' }
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
      <Card className="elite-card-gradient border-2 border-royal-gold/30">
        <CardHeader>
          <CardTitle className="text-royal-gold flex items-center text-2xl">
            <Target className="w-6 h-6 mr-3" />
            Elite Progress Tracking
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
                <div key={metric.key} className="performance-card p-4 rounded-lg">
                  <div className="flex items-center justify-between mb-3">
                    <div className="flex items-center">
                      <metric.icon className={`w-5 h-5 mr-2 ${metric.color}`} />
                      <span className="font-semibold text-elite-white">{metric.label}</span>
                    </div>
                    <Badge className={progress.improving ? 'status-good' : 'status-average'}>
                      {progress.percentage.toFixed(0)}%
                    </Badge>
                  </div>
                  
                  {/* Progress Ring */}
                  <div className="relative mb-4">
                    <div className="timeline-progress h-3 mb-2">
                      <div 
                        className="timeline-fill h-full"
                        style={{ width: `${progress.percentage}%` }}
                      />
                      <div 
                        className="timeline-marker"
                        style={{ left: `${progress.percentage}%` }}
                      />
                    </div>
                  </div>

                  {/* Current vs Target */}
                  <div className="grid grid-cols-2 gap-4 mb-3">
                    <div className="text-center">
                      <div className="text-2xl font-bold text-royal-gold">
                        {current}{metric.unit}
                      </div>
                      <div className="text-xs text-elite-white/70">Current</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-royal-blue">
                        {target}{metric.unit}
                      </div>
                      <div className="text-xs text-elite-white/70">Target</div>
                    </div>
                  </div>

                  {/* Improvement Needed */}
                  <div className="flex items-center justify-between text-sm">
                    <span className="text-elite-white/80">
                      Need: {progress.remaining.toFixed(1)}{metric.unit}
                    </span>
                    <div className="flex items-center text-royal-gold">
                      <Clock className="w-3 h-3 mr-1" />
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
      <Card className="elite-card-gradient border-2 border-royal-red/30">
        <CardHeader>
          <CardTitle className="text-royal-red flex items-center">
            <Calendar className="w-5 h-5 mr-2" />
            Weekly Training Focus
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {/* Priority Areas */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="bg-royal-red/20 p-4 rounded-lg border border-royal-red/30">
                <h4 className="font-bold text-royal-red mb-2">🎯 Priority This Week</h4>
                <div className="space-y-2">
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
                      <div key={metric.key} className="flex items-center justify-between">
                        <span className="text-elite-white">{metric.label}</span>
                        <ArrowRight className="w-4 h-4 text-royal-red" />
                      </div>
                    ))
                  }
                </div>
              </div>

              <div className="bg-royal-gold/20 p-4 rounded-lg border border-royal-gold/30">
                <h4 className="font-bold text-royal-gold mb-2">⚡ Maintain Excellence</h4>
                <div className="space-y-2">
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
                      <div key={metric.key} className="flex items-center justify-between">
                        <span className="text-elite-white">{metric.label}</span>
                        <Award className="w-4 h-4 text-royal-gold" />
                      </div>
                    ))
                  }
                </div>
              </div>
            </div>

            {/* Progress Timeline */}
            <div className="bg-royal-blue/20 p-4 rounded-lg border border-royal-blue/30">
              <h4 className="font-bold text-royal-blue mb-3">📅 4-Week Progress Plan</h4>
              <div className="space-y-3">
                {[1, 2, 3, 4].map(week => (
                  <div key={week} className="flex items-center space-x-4">
                    <div className="progress-indicator w-8 h-8 text-sm">
                      {week}
                    </div>
                    <div className="flex-1">
                      <div className="text-elite-white font-medium">
                        Week {week}: {
                          week === 1 ? 'Foundation Building' :
                          week === 2 ? 'Skill Enhancement' :
                          week === 3 ? 'Performance Push' :
                          'Assessment & Goals'
                        }
                      </div>
                      <div className="text-elite-white/70 text-sm">
                        {week === 1 ? 'Focus on basic techniques and conditioning' :
                         week === 2 ? 'Advanced drills and tactical awareness' :
                         week === 3 ? 'High-intensity training and competition prep' :
                         'Retest and set new targets'}
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