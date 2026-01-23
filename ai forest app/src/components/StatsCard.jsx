import React from 'react';
import clsx from 'clsx';
import './StatsCard.css';

const StatsCard = ({ title, value, icon: Icon, trend, trendValue, status, subtext, color = 'primary' }) => {
    return (
        <div className="card stats-card">
            <div className="stats-header">
                <div className={clsx('stats-icon', `bg-${color}`)}>
                    <Icon size={24} color="white" />
                </div>
                {status && (
                    <span className={clsx('status-badge', status.toLowerCase())}>
                        {status}
                    </span>
                )}
            </div>

            <div className="stats-content">
                <h3 className="stats-value">{value}</h3>
                <p className="stats-title">{title}</p>
            </div>

            <div className="stats-footer">
                {trend && (
                    <span className={clsx('trend', trend === 'up' ? 'positive' : 'negative')}>
                        {trend === 'up' ? '↑' : '↓'} {trendValue}
                    </span>
                )}
                {subtext && <span className="stats-subtext">{subtext}</span>}
            </div>
        </div>
    );
};

export default StatsCard;
