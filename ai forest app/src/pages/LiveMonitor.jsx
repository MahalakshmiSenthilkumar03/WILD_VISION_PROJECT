import React, { useState, useEffect } from 'react';
import { MapPin, Brain, Activity, AlertCircle } from 'lucide-react';
import axios from 'axios';
import './LiveMonitor.css';

const LiveMonitor = () => {
    const [selectedCam, setSelectedCam] = useState(1);
    const [monitorData, setMonitorData] = useState(null);

    // Fetch Monitor Data
    useEffect(() => {
        const fetchData = async () => {
            try {
                const res = await axios.get('http://localhost:5001/api/forest/monitor');
                setMonitorData(res.data);
            } catch (err) {
                console.error("Error fetching monitor data:", err);
            }
        };

        fetchData();
        const interval = setInterval(fetchData, 1000); // Update every second
        return () => clearInterval(interval);
    }, []);

    // Mock Cameras (Visual only for now)
    const cameras = [
        { id: 1, name: 'CAM-01', status: 'active', alert: monitorData?.alertLevel === 'CRITICAL' },
        { id: 2, name: 'CAM-02', status: 'active', alert: false },
        { id: 3, name: 'CAM-03', status: 'active', alert: false },
        { id: 4, name: 'CAM-04', status: 'warning', alert: false },
    ];

    return (
        <div className="live-monitor-container">
            {/* Left: Main Feed & Thumbnails */}
            <div className="monitor-main">
                <div className="main-feed-container">
                    <div className="feed-overlay">
                        <span className="cam-id-tag">CAM-01 | Sector 4 North</span>
                        <span className="live-badge">LIVE REC</span>
                    </div>

                    {/* Real Video Stream from Adapter */}
                    <div style={{ width: '100%', height: '100%', background: '#000', overflow: 'hidden' }}>
                        <img
                            src="http://localhost:5001/video_feed"
                            alt="Live Camera Feed"
                            style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                            onError={(e) => { e.target.style.display = 'none'; }}
                        />
                    </div>

                    {/* Bounding Boxes are now drawn by backend on the video stream, no need to render overlay boxes manually unless we want extra interactivity. 
                        The prompt said "Bounding boxes already drawn" in requirements of WILD_VISION.
                        So we can remove the manual hardcoded boxes.
                    */}
                </div>

                <div className="thumbnails-grid">
                    {cameras.map(cam => (
                        <div
                            key={cam.id}
                            className={`camera-thumb ${selectedCam === cam.id ? 'active' : ''} ${cam.alert ? 'alert' : ''}`}
                            onClick={() => setSelectedCam(cam.id)}
                        >
                            <div className="thumb-label">{cam.name}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Right: Intelligence Panel */}
            <div className="intelligence-panel card glass-panel">
                <div className="panel-header">
                    <h2 className="text-xl font-bold">Intelligence Hub</h2>
                    <div className="flex items-center gap-2 mt-2">
                        <MapPin size={16} className="text-gray-500" />
                        <span className="text-sm text-gray-500">Sector 4, Zone B</span>
                    </div>
                    <span className={`risk-badge ${monitorData?.alertLevel === 'CRITICAL' ? 'risk-high' : 'risk-low'}`}>
                        RISK LEVEL: {monitorData?.alertLevel || 'CONNECTING...'}
                    </span>
                </div>

                <div>
                    <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                        <Brain size={18} className="text-primary" />
                        AI Reasoning
                    </h3>
                    <div className="ai-reasoning-box">
                        <ul className="reasoning-list">
                            {monitorData?.aiReasoning && monitorData.aiReasoning.length > 0 ? (
                                monitorData.aiReasoning.map((reason, idx) => (
                                    <li key={idx}>
                                        <AlertCircle size={14} color={monitorData.alertLevel === 'CRITICAL' ? "red" : "green"} />
                                        {reason}
                                    </li>
                                ))
                            ) : (
                                <li><AlertCircle size={14} color="gray" /> Initializing analysis...</li>
                            )}
                        </ul>
                    </div>
                </div>

                <div>
                    <h3 className="text-sm font-bold text-gray-700 mb-3 flex items-center gap-2">
                        <Activity size={18} className="text-primary" />
                        Recent Detections
                    </h3>
                    <div className="detection-list">
                        {monitorData?.recentDetections && monitorData.recentDetections.length > 0 ? (
                            monitorData.recentDetections.map((det, idx) => (
                                <div className="detection-item" key={idx}>
                                    <span>{det.name} ({det.confidence}%)</span>
                                    <span className="text-gray-500 text-sm">{det.time}</span>
                                </div>
                            ))
                        ) : (
                            <div className="detection-item">
                                <span className="text-gray-500">No recent activity</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default LiveMonitor;
