import React from 'react';

export default function GaugeChart({ value, max, label, unit = '', standardValue = null }) {
  // Calculate percentage for the gauge
  const percentage = (value / max) * 100;
  
  // Determine color based on performance
  let color = '#ef4444'; // red
  if (percentage >= 90) {
    color = '#22c55e'; // green
  } else if (percentage >= 70) {
    color = '#eab308'; // yellow
  }
  
  // For metrics where lower is better (like sprint times)
  const isLowerBetter = label.toLowerCase().includes('sprint') || label.toLowerCase().includes('time');
  
  if (isLowerBetter && standardValue) {
    // Reverse the color logic for lower-is-better metrics
    if (value <= standardValue * 0.9) {
      color = '#22c55e';
    } else if (value <= standardValue * 1.1) {
      color = '#eab308';
    } else {
      color = '#ef4444';
    }
  }
  
  // SVG gauge parameters
  const size = 140;
  const strokeWidth = 12;
  const center = size / 2;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  
  // Calculate arc for gauge (180 degrees = semicircle)
  const arcLength = circumference / 2;
  const progress = (percentage / 100) * arcLength;
  const offset = arcLength - progress;
  
  return (
    <div className="flex flex-col items-center">
      <svg width={size} height={size * 0.6} viewBox={`0 0 ${size} ${size * 0.6}`}>
        {/* Background arc */}
        <path
          d={`M ${strokeWidth/2} ${center} A ${radius} ${radius} 0 0 1 ${size - strokeWidth/2} ${center}`}
          fill="none"
          stroke="#e5e7eb"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Progress arc - green section */}
        <path
          d={`M ${strokeWidth/2} ${center} A ${radius} ${radius} 0 0 1 ${center - radius * 0.5} ${center - radius * 0.866}`}
          fill="none"
          stroke="#22c55e"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Progress arc - yellow section */}
        <path
          d={`M ${center - radius * 0.5} ${center - radius * 0.866} A ${radius} ${radius} 0 0 1 ${center + radius * 0.5} ${center - radius * 0.866}`}
          fill="none"
          stroke="#eab308"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Progress arc - red section */}
        <path
          d={`M ${center + radius * 0.5} ${center - radius * 0.866} A ${radius} ${radius} 0 0 1 ${size - strokeWidth/2} ${center}`}
          fill="none"
          stroke="#ef4444"
          strokeWidth={strokeWidth}
          strokeLinecap="round"
        />
        
        {/* Needle/pointer */}
        <g transform={`rotate(${-90 + (percentage / 100) * 180} ${center} ${center})`}>
          <line
            x1={center}
            y1={center}
            x2={center}
            y2={strokeWidth + 5}
            stroke="#1f2937"
            strokeWidth="3"
            strokeLinecap="round"
          />
          <circle cx={center} cy={center} r="6" fill="#1f2937" />
        </g>
        
        {/* Value text */}
        <text
          x={center}
          y={center + 15}
          textAnchor="middle"
          className="text-3xl font-bold"
          fill="#1f2937"
        >
          {value}{unit}
        </text>
        
        {/* Max value indicator */}
        {standardValue && (
          <text
            x={size - 10}
            y={center - 5}
            textAnchor="end"
            className="text-xs"
            fill="#6b7280"
          >
            {standardValue}
          </text>
        )}
      </svg>
      
      <div className="text-center mt-2">
        <div className="font-semibold text-sm">{label}</div>
        {standardValue && (
          <div className="text-xs text-gray-500 mt-1">
            {Math.round(percentage)}% of standard
          </div>
        )}
      </div>
    </div>
  );
}
