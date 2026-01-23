import React, { useState, useEffect } from 'react';
import { AlertTriangle, Camera, PawPrint, ShieldCheck, Activity } from 'lucide-react';
import { PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import StatsCard from '../components/StatsCard'; // Ensure component exists
import axios from 'axios';
import './Dashboard.css';

const Dashboard = () => {
    // Stats State
    const [stats, setStats] = useState({
        totalDetections: 0,
        animalCount: 0,
        humanCount: 0,
        weaponCount: 0,
        poachingAlerts: 0
    });

    // Fetch Stats
    useEffect(() => {
        const fetchStats = async () => {
            try {
                const res = await axios.get('http://localhost:5001/api/forest/stats');
                if (res.data) {
                    setStats(res.data);
                }
            } catch (err) {
                console.error("Error fetching stats:", err);
            }
        };

        fetchStats();
        const interval = setInterval(fetchStats, 2000);
        return () => clearInterval(interval);
    }, []);

    // Derived Data for Chart
    const threatData = [
        { name: 'Human', value: stats.humanCount || 0, color: '#D32F2F' },
        { name: 'Poaching', value: stats.poachingAlerts || 0, color: '#FB8C00' },
        { name: 'Weapon', value: stats.weaponCount || 0, color: '#FDD835' },
        { name: 'Animal', value: stats.animalCount || 0, color: '#0288D1' },
    ];

    // Filter out zero values for better chart look (optional, but good for UI)
    const activeThreatData = threatData.filter(d => d.value > 0);
    // If empty, show a placeholder segment
    const chartData = activeThreatData.length > 0 ? activeThreatData : [{ name: 'No Activity', value: 1, color: '#ccc' }];


    return (
        <div className="dashboard-container">
            {/* Welcome Section */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Dashboard Overview</h1>
                <p className="text-gray-500">Real-time forest surveillance summary</p>
            </div>

            {/* Stats Grid */}
            <div className="stats-grid">
                <StatsCard
                    title="Poaching Alerts"
                    value={stats.poachingAlerts.toString()}
                    icon={AlertTriangle}
                    color={stats.poachingAlerts > 0 ? "alert" : "primary"}
                    trend="up"
                    trendValue="Live"
                    subtext="Critical Incidents"
                />
                <StatsCard
                    title="Active Cameras"
                    value="1 Active"
                    icon={Camera}
                    color="primary"
                    status="Online"
                    subtext="WILD_VISION Connected"
                />
                <StatsCard
                    title="Detected Animals"
                    value={stats.animalCount.toString()}
                    icon={PawPrint}
                    color="info"
                    subtext="Total Count"
                />
                <StatsCard
                    title="Poaching Risk"
                    value={stats.poachingAlerts > 0 ? "HIGH" : "LOW"}
                    icon={ShieldCheck}
                    color={stats.poachingAlerts > 0 ? "warning" : "success"}
                    status="Sector 4"
                    trend="flat"
                    trendValue="Monitoring"
                />
            </div>

            {/* Analytics Section */}
            <div className="analytics-grid">
                {/* Threat Distribution Chart */}
                <div className="card glass-panel chart-card">
                    <div className="card-header">
                        <h3>Detection Distribution</h3>
                    </div>
                    <div className="chart-container">
                        <ResponsiveContainer width="100%" height={300}>
                            <PieChart>
                                <Pie
                                    data={chartData}
                                    cx="50%"
                                    cy="50%"
                                    innerRadius={60}
                                    outerRadius={100}
                                    paddingAngle={5}
                                    dataKey="value"
                                >
                                    {chartData.map((entry, index) => (
                                        <Cell key={`cell-${index}`} fill={entry.color} />
                                    ))}
                                </Pie>
                                <Tooltip />
                                <Legend verticalAlign="bottom" height={36} />
                            </PieChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Operational Status Panel */}
                <div className="card glass-panel status-panel">
                    <div className="card-header">
                        <h3>Operational Status</h3>
                    </div>

                    <div className="ranger-status">
                        <h4 className="section-title">Active Rangers</h4>
                        <div className="status-row">
                            <span className="label">On Patrol</span>
                            <div className="bar-container">
                                <div className="bar" style={{ width: '80%', background: '#4CAF50' }}></div>
                            </div>
                            <span className="value">12</span>
                        </div>
                        <div className="status-row">
                            <span className="label">Responding</span>
                            <div className="bar-container">
                                <div className="bar" style={{ width: '30%', background: '#FFA726' }}></div>
                            </div>
                            <span className="value">4</span>
                        </div>
                        <div className="status-row">
                            <span className="label">Idle</span>
                            <div className="bar-container">
                                <div className="bar" style={{ width: '10%', background: '#BDBDBD' }}></div>
                            </div>
                            <span className="value">2</span>
                        </div>
                    </div>

                    <div className="system-health mt-6">
                        <h4 className="section-title">System Health</h4>
                        <div className="health-circle">
                            <Activity size={32} className="text-primary" />
                            <span className="health-value">98%</span>
                            <span className="health-label">Operational</span>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default Dashboard;
