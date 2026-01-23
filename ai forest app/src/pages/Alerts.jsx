import React from 'react';
import AlertItem from '../components/AlertItem';
import './Alerts.css';

const Alerts = () => {
    const alertsData = [
        {
            id: 1,
            type: 'Intrusion',
            title: 'Unauthorized Entry Detected',
            location: 'Sector 4, North Gate',
            time: '10:23 AM',
            status: 'New',
            confidence: 92,
        },
        {
            id: 2,
            type: 'Poaching',
            title: 'Potential Poaching Activity',
            location: 'Sector 2, River Bank',
            time: '09:15 AM',
            status: 'In Progress',
            confidence: 88,
        },
        {
            id: 3,
            type: 'Animal',
            title: 'Elephant Herd Movement',
            location: 'Sector 1, Buffer Zone',
            time: '08:45 AM',
            status: 'Resolved',
            confidence: 95,
        },
        {
            id: 4,
            type: 'Intrusion',
            title: 'Vehicle Detected off-road',
            location: 'Sector 3',
            time: 'Yesterday, 11:30 PM',
            status: 'Resolved',
            confidence: 99,
        },
    ];

    return (
        <div>
            <div className="alerts-header">
                <div className="header-text">
                    <h1>Alerts & Incidents</h1>
                    <p>Real-time threat detection log</p>
                </div>
                <div className="header-actions">
                    <button className="btn-filter">Filter</button>
                    <button className="btn-export">Export Report</button>
                </div>
            </div>

            <div className="alerts-list">
                {alertsData.map(alert => (
                    <AlertItem
                        key={alert.id}
                        {...alert}
                    />
                ))}
            </div>
        </div>
    );
};

export default Alerts;
