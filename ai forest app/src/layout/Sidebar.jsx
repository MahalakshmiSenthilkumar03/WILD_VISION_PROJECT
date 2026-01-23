import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, AlertTriangle, Video, Map, Shield } from 'lucide-react';
import './Layout.css';

const Sidebar = ({ isOpen }) => {
    const navItems = [
        { path: '/', label: 'Overview', icon: <LayoutDashboard size={20} /> },
        { path: '/alerts', label: 'Alerts & Incidents', icon: <AlertTriangle size={20} /> },
        { path: '/live', label: 'Live Monitoring', icon: <Video size={20} /> },
        { path: '/tracking', label: 'Animal Tracking', icon: <Map size={20} /> },
    ];

    return (
        <aside className={`sidebar ${isOpen ? 'open' : ''}`}>
            <div className="sidebar-header">
                <div className="sidebar-brand-icon">
                    <Shield size={24} color="#FFF" />
                </div>
                <div className="brand-text">
                    <h1>ForestShield</h1>
                    <p>Ranger Command</p>
                </div>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                    >
                        {item.icon}
                        <span>{item.label}</span>
                    </NavLink>
                ))}
            </nav>

            <div className="sidebar-footer">
                <div className="status-card">
                    <h4 className="text-white text-sm font-semibold mb-1" style={{ fontSize: '0.85rem' }}>System Status</h4>
                    <div className="status-indicator">
                        <div className="dot"></div>
                        <span>Online & Secure</span>
                    </div>
                </div>
            </div>
        </aside>
    );
};

export default Sidebar;
