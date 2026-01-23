import React, { useState } from 'react';
import { Outlet } from 'react-router-dom';
import Sidebar from './Sidebar';
import TopBar from './TopBar';
import './Layout.css';

const MainLayout = () => {
    const [isSidebarOpen, setIsSidebarOpen] = useState(false);

    const toggleSidebar = () => {
        setIsSidebarOpen(!isSidebarOpen);
    };

    return (
        <div className="app-container">
            <Sidebar isOpen={isSidebarOpen} />

            <div className="main-content">
                <TopBar toggleSidebar={toggleSidebar} />

                <main className="content-wrapper">
                    <Outlet />
                </main>
            </div>
        </div>
    );
};

export default MainLayout;
