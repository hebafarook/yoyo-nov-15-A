import React from 'react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';

const ComingSoon = ({ 
  title, 
  description, 
  icon: Icon, 
  features = [], 
  estimatedRelease = "Coming Soon",
  priority = "medium" 
}) => {
  const getPriorityColor = () => {
    switch (priority) {
      case 'high': return 'badge-excellent';
      case 'medium': return 'badge-good';
      case 'low': return 'badge-average';
      default: return 'badge-good';
    }
  };

  return (
    <Card className="coming-soon-card">
      <CardContent className="text-center space-y-6">
        {/* Icon */}
        <div className="coming-soon-icon">
          <Icon className="w-24 h-24 mx-auto" />
        </div>

        {/* Title */}
        <div>
          <h2 className="text-3xl font-bold mb-3">{title}</h2>
          <p className="text-lg text-[--text-muted] max-w-2xl mx-auto">{description}</p>
        </div>

        {/* Priority Badge */}
        <span className={`${getPriorityColor()} px-4 py-2 text-base font-semibold`}>
          {estimatedRelease}
        </span>

        {/* Features Preview */}
        {features.length > 0 && (
          <div className="space-y-4">
            <h3 className="text-xl font-semibold text-[--primary-blue]">Planned Features:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3 max-w-2xl mx-auto">
              {features.map((feature, index) => (
                <div key={index} className="flex items-center gap-3 text-[--text-secondary] p-3 professional-card">
                  <div className="w-2 h-2 bg-[--secondary-gold] rounded-full" />
                  <span className="text-sm font-medium">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Development Status */}
        <div className="mt-8">
          <div className="inline-flex items-center gap-2 bg-[--light-bg] px-4 py-2 rounded-lg border border-[--border-color]">
            <div className="w-3 h-3 bg-[--secondary-gold] rounded-full animate-pulse" />
            <span className="text-[--text-secondary] text-sm font-medium">In Active Development</span>
          </div>
        </div>

        {/* Progress Bar */}
        <div className="w-full max-w-md mx-auto">
          <div className="progress-container h-2">
            <div className="progress-bar w-1/3" />
          </div>
          <div className="flex justify-between mt-2 text-xs text-[--text-muted]">
            <span>Planned</span>
            <span>In Progress</span>
            <span>Ready</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ComingSoon;