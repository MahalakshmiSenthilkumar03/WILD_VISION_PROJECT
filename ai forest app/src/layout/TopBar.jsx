import React from 'react';
import { Menu, Bell, User } from 'lucide-react';
import './Layout.css';

const TopBar = ({ toggleSidebar }) => {
    return (
        <header className="top-bar">
            <div className="top-bar-left">
                <button className="menu-btn" onClick={toggleSidebar}>
                    <Menu size={24} />
                </button>
                <h2 className="page-title">Dashboard</h2>
            </div>

            <div className="top-bar-right">
                <button className="icon-btn">
                    <Bell size={20} />
                    <span className="badge-dot"></span>
                </button>

                <div className="user-profile">
                    <div className="user-info">
                        <p className="user-name">Ranger Alex</p>
                        <p className="user-role">Sector 4 Admin</p>
                    </div>
                    <div className="avatar">
                        <User size={20} />
                    </div>
                </div>
            </div>
        </header>
    );
};

export default TopBar;
