import React from 'react';

export const KPICard = ({ title, value, subtitle, icon: Icon, trend, trendType = 'neutral' }) => {
  const getTrendColor = () => {
    if (trendType === 'positive') return 'text-success';
    if (trendType === 'negative') return 'text-danger';
    return 'text-dark-textMuted';
  };

  return (
    <div className="bg-dark-card border border-dark-border rounded-xl p-6 transition-all duration-300 hover:border-dark-accent hover:shadow-glow group">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium text-dark-textMuted group-hover:text-dark-accent transition-colors duration-300">
          {title}
        </span>
        {Icon && (
          <div className="p-2 bg-dark-bg border border-dark-border rounded-lg text-dark-accent group-hover:bg-dark-accent group-hover:text-white transition-all duration-300">
            <Icon size={20} />
          </div>
        )}
      </div>
      <div className="mt-4">
        <h3 className="text-3xl font-bold tracking-tight text-dark-text">
          {value}
        </h3>
        <div className="flex items-center mt-2 space-x-2 text-xs">
          {trend && (
            <span className={`font-semibold ${getTrendColor()}`}>
              {trend}
            </span>
          )}
          <span className="text-dark-textMuted">{subtitle}</span>
        </div>
      </div>
    </div>
  );
};

export default KPICard;
