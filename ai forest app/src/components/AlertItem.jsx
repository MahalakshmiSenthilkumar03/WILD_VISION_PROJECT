import React from 'react';
import { AlertTriangle, ShieldAlert, BadgeAlert, MapPin, Clock } from 'lucide-react';
import clsx from 'clsx';
import './AlertItem.css';

const AlertItem = ({ type, title, location, time, status, confidence }) => {
    const getIcon = () => {
        switch (type) {
            case 'Intrusion': return <ShieldAlert size={24} />;
            case 'Poaching': return <BadgeAlert size={24} />;
            default: return <AlertTriangle size={24} />;
        }
    };

    const getStatusColor = (s) => {
        switch (s.toLowerCase()) {
            case 'new': return 'red';
            case 'in progress': return 'orange';
            case 'resolved': return 'green';
            default: return 'gray';
        }
    };

    const statusColor = getStatusColor(status);

    return (
        <div className="alert-item card">
            <div className={clsx('alert-icon-wrapper', `bg-${statusColor}-100`, `text-${statusColor}-600`)}>
                {getIcon()}
            </div>

            <div className="alert-details">
                <h4 className="alert-title">{title}</h4>
                <div className="alert-meta">
                    <span className="meta-tag"><MapPin size={14} /> {location}</span>
                    <span className="meta-tag"><Clock size={14} /> {time}</span>
                </div>
            </div>

            <div className="alert-status-section">
                <div className="confidence-score">
                    <span className="score-label">Confidence</span>
                    <span className="score-val">{confidence}%</span>
                </div>
                <span className={clsx('status-pill', `status-${statusColor}`)}>
                    {status}
                </span>
            </div>
        </div>
    );
};

export default AlertItem;
