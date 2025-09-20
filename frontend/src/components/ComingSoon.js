import React from 'react';
import { Card, CardContent } from './ui/card';
import { Badge } from './ui/badge';

const ComingSoon = ({ 
  title, 
  description, 
  icon: Icon, 
  features = [], 
  estimatedRelease = "Coming Soon",
  priority = "high" 
}) => {
  const getPriorityColor = () => {
    switch (priority) {
      case 'high': return 'status-excellent';
      case 'medium': return 'status-good';
      case 'low': return 'status-average';
      default: return 'status-good';
    }
  };

  return (
    <Card className="coming-soon-card min-h-[400px] flex items-center justify-center relative overflow-hidden">
      {/* Background Pattern */}
      <div className="absolute inset-0 opacity-10">
        <div className="absolute top-4 left-4 w-20 h-20 border-2 border-royal-gold rounded-full animate-pulse" />
        <div className="absolute bottom-4 right-4 w-16 h-16 border-2 border-royal-blue rounded-full animate-pulse delay-1000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-32 h-32 border-2 border-royal-red rounded-full animate-pulse delay-500" />
      </div>

      <CardContent className="text-center space-y-6 relative z-10">
        {/* Icon */}
        <div className="coming-soon-icon">
          <Icon className="w-24 h-24 mx-auto text-royal-gold" />
        </div>

        {/* Title */}
        <div>
          <h2 className="text-3xl font-bold text-elite-white mb-2">{title}</h2>
          <p className="text-elite-white/70 text-lg max-w-md mx-auto">{description}</p>
        </div>

        {/* Priority Badge */}
        <Badge className={`${getPriorityColor()} px-4 py-2 text-sm font-bold`}>
          {estimatedRelease}
        </Badge>

        {/* Features Preview */}
        {features.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-royal-gold font-semibold">Upcoming Features:</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-2 max-w-lg mx-auto">
              {features.map((feature, index) => (
                <div key={index} className="flex items-center space-x-2 text-elite-white/80">
                  <div className="w-2 h-2 bg-royal-gold rounded-full animate-pulse" style={{ animationDelay: `${index * 200}ms` }} />
                  <span className="text-sm">{feature}</span>
                </div>
              ))}
            </div>
          </div>
        )}

        {/* Elite Progress Indicator */}
        <div className="mt-8">
          <div className="inline-flex items-center space-x-2 bg-elite-black-light/50 px-4 py-2 rounded-full border border-royal-gold/30">
            <div className="w-3 h-3 bg-royal-gold rounded-full animate-pulse" />
            <span className="text-elite-white/80 text-sm font-medium">In Development</span>
          </div>
        </div>

        {/* Royal Loading Animation */}
        <div className="w-full max-w-xs mx-auto">
          <div className="h-1 bg-elite-black-light rounded-full overflow-hidden">
            <div className="h-full royal-loading rounded-full" />
          </div>
        </div>
      </CardContent>
    </Card>
  );
};

export default ComingSoon;