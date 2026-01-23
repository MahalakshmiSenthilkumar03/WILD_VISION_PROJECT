import React, { useState, useEffect } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Circle, Polyline, Polygon, useMap } from 'react-leaflet';
import {
    ArrowLeft, Settings, PawPrint, AlertTriangle, Signal, Clock,
    Camera, Target, Bell, Info, MapPin
} from 'lucide-react';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import './AnimalTracking.css';

// Fix Leaflet Default Icon
import icon from 'leaflet/dist/images/marker-icon.png';
import iconShadow from 'leaflet/dist/images/marker-shadow.png';

let DefaultIcon = L.icon({
    iconUrl: icon,
    shadowUrl: iconShadow,
    iconSize: [25, 41],
    iconAnchor: [12, 41]
});
L.Marker.prototype.options.icon = DefaultIcon;

// --- Custom Icons ---

const createAnimalIcon = (isSelected) => new L.DivIcon({
    className: 'custom-anim-icon',
    html: `<div class="anim-marker-wrap ${isSelected ? 'selected' : ''}">
           <div class="anim-pulse"></div>
           <div class="anim-center" style="background-color: ${isSelected ? '#FF5722' : '#2196F3'}; border-color: ${isSelected ? '#FFCCBC' : 'white'};">
             <svg width="16" height="16" viewBox="0 0 512 512" style="fill:white;">
               <path d="M256 224c-79.41 0-144 64.59-144 144s64.59 144 144 144 144-64.59 144-144-64.59-144-144-144zm0-96c35.35 0 64-28.65 64-64s-28.65-64-64-64-64 28.65-64 64 28.65 64 64 64zm-128 32c35.35 0 64-28.65 64-64S163.35 32 128 32 64 60.65 64 96s28.65 64 64 64zm256 0c35.35 0 64-28.65 64-64s-28.65-64-64-64-64 28.65-64 64 28.65 64 64 64z"/>
             </svg>
           </div>
         </div>`,
    iconSize: [40, 40],
    iconAnchor: [20, 20]
});

const createCameraIcon = (status) => new L.DivIcon({
    className: 'custom-camera-icon',
    html: `<div style="background-color: ${status === 'active' ? '#333' : '#757575'}; width: 24px; height: 24px; border-radius: 4px; display: flex; align-items: center; justify-content: center; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"><span style="color:white; font-size:12px;">📷</span></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12]
});

// --- Constants & Data ---

const INITIAL_CENTER = [26.0173, 76.5026]; // Ranthambore Base

const CAMERAS = [
    { id: 'CAM-01', pos: [26.015, 76.500], status: 'active', location: 'North Ridge' },
    { id: 'CAM-02', pos: [26.022, 76.508], status: 'active', location: 'Waterhole East' },
    { id: 'CAM-03', pos: [26.010, 76.512], status: 'inactive', location: 'Village Periphery' },
    { id: 'CAM-04', pos: [26.019, 76.495], status: 'active', location: 'West Valley' },
];

const VILLAGE_BUFFER_ZONE = [
    [26.008, 76.515],
    [26.008, 76.508],
    [26.012, 76.505],
    [26.015, 76.510],
    [26.012, 76.518]
];

const ANIMALS = [
    {
        id: 'A-101',
        type: 'Tiger',
        pos: [26.0173, 76.5026],
        detectedBy: 'CAM-01',
        time: '2m ago',
        confidence: 96,
        risk: 'High',
        path: [[26.0173, 76.5026], [26.0195, 76.5055], [26.0210, 76.5015]],
        visionCone: [
            [26.0173, 76.5026],
            [26.0195, 76.5055],
            [26.0210, 76.5015]
        ]
    },
    {
        id: 'A-102',
        type: 'Elephant Herd',
        pos: [26.012, 76.510],
        detectedBy: 'CAM-03',
        time: '15m ago',
        confidence: 88,
        risk: 'Medium',
        path: null, // No clear path predicted yet
        visionCone: null
    },
    {
        id: 'A-103',
        type: 'Leopard',
        pos: [26.023, 76.498],
        detectedBy: 'CAM-04',
        time: '5m ago',
        confidence: 91,
        risk: 'High',
        path: null,
        visionCone: null
    }

];

// --- Components ---

const FlyToLocation = ({ trigger }) => {
    const map = useMap();
    useEffect(() => {
        if (trigger) {
            map.flyTo(trigger.pos, 16, { duration: 1.5 });
        }
    }, [trigger, map]);
    return null;
};

const AnimalTracking = () => {
    const [showRange, setShowRange] = useState(true);
    const [showPath, setShowPath] = useState(true);
    const [showRiskZones, setShowRiskZones] = useState(true);
    const [selectedEntity, setSelectedEntity] = useState(ANIMALS[0]); // Default select first animal
    const [focusTrigger, setFocusTrigger] = useState(null);

    // Trigger focus when selection changes (if explicit focus requested)
    // Or purely select on click. 

    const handleEntityClick = (entity) => {
        setSelectedEntity(entity);
        setFocusTrigger({ pos: entity.pos, t: Date.now() });
    };

    const handleFocus = () => {
        if (selectedEntity) {
            setFocusTrigger({ pos: selectedEntity.pos, t: Date.now() });
        }
    };

    const handleCreateAlert = () => {
        alert(`🚨 Alert Created for ${selectedEntity.id || 'Selected Entity'}!`);
    };

    return (
        <div className="tracking-page">
            {/* 1. Header */}
            <header className="page-header">
                <div className="flex items-center gap-4">
                    <button className="icon-btn-plain"><ArrowLeft size={24} /></button>
                    <div className="flex flex-col">
                        <h1 className="text-xl font-bold text-gray-800">Animal Tracking</h1>
                        <span className="text-xs text-gray-500">Sector 4 • Ranthambore Buffer</span>
                    </div>
                </div>
                <button className="icon-btn-plain"><Settings size={24} /></button>
            </header>

            {/* 2. Status Bar */}
            <div className="status-bar">
                <div className="status-item">
                    <div className="icon-box blue"><PawPrint size={18} /></div>
                    <div>
                        <span className="block text-xs text-gray-500">Active Animals</span>
                        <span className="block font-bold text-sm">{ANIMALS.length}&nbsp; Detected</span>
                    </div>
                </div>
                <div className="status-item">
                    <div className="icon-box red"><AlertTriangle size={18} /></div>
                    <div>
                        <span className="block text-xs text-gray-500">Risk Level</span>
                        <span className="block font-bold text-sm text-red-600">High (2 Critical)</span>
                    </div>
                </div>
                <div className="status-item">
                    <div className="icon-box green"><Signal size={18} /></div>
                    <div>
                        <span className="block text-xs text-gray-500">Network</span>
                        <span className="block font-bold text-sm">4/4 Cameras</span>
                    </div>
                </div>
                <div className="status-item">
                    <div className="icon-box gray"><Clock size={18} /></div>
                    <div>
                        <span className="block text-xs text-gray-500">Last Update</span>
                        <span className="block font-bold text-sm">Live</span>
                    </div>
                </div>
            </div>

            {/* 3. Map Section */}
            <div className="map-section">
                <MapContainer center={INITIAL_CENTER} zoom={14} style={{ height: '100%', width: '100%' }}>
                    <TileLayer attribution='&copy; OpenStreetMap' url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />

                    <FlyToLocation trigger={focusTrigger} />

                    {/* Village Buffer Zone (Red) */}
                    {showRiskZones && (
                        <Polygon
                            positions={VILLAGE_BUFFER_ZONE}
                            pathOptions={{ fillColor: '#EF5350', color: '#B71C1C', weight: 2, fillOpacity: 0.25, dashArray: '5, 5' }}
                        >
                            <Popup>Village Buffer Zone (Restricted)</Popup>
                        </Polygon>
                    )}

                    {/* Render Cameras with Radii */}
                    {CAMERAS.map(cam => (
                        <React.Fragment key={cam.id}>
                            {/* Camera Detection Radius - Green Circle */}
                            {showRange && (
                                <Circle
                                    center={cam.pos}
                                    radius={400}
                                    pathOptions={{
                                        color: '#2E7D32',       // Darker Green Border
                                        fillColor: '#4CAF50',   // Green Fill
                                        fillOpacity: 0.1,       // Very light fill
                                        weight: 1,              // Thin border
                                        dashArray: '5, 5'       // Tech feel
                                    }}
                                />
                            )}

                            <Marker
                                position={cam.pos}
                                icon={createCameraIcon(cam.status)}
                                eventHandlers={{ click: () => handleEntityClick(cam) }}
                            >
                                <Popup>{cam.id} - {cam.location}</Popup>
                            </Marker>
                        </React.Fragment>
                    ))}

                    {/* Render Animals */}
                    {ANIMALS.map(anim => (
                        <React.Fragment key={anim.id}>
                            <Marker
                                position={anim.pos}
                                icon={createAnimalIcon(selectedEntity?.id === anim.id)}
                                eventHandlers={{ click: () => handleEntityClick(anim) }}
                            >
                                <Popup>{anim.type} (ID: {anim.id})</Popup>
                            </Marker>

                            {/* Animal Specific Overlays */}
                            {anim.visionCone && showPath && (
                                <Polygon
                                    positions={anim.visionCone}
                                    pathOptions={{ fillColor: '#2196F3', color: 'transparent', fillOpacity: 0.4 }}
                                />
                            )}
                        </React.Fragment>
                    ))}
                </MapContainer>

                {/* Legend / Toggles */}
                <div className="map-toggles">
                    <button className={`toggle-btn ${showRange ? 'active-green' : ''}`} onClick={() => setShowRange(!showRange)}>
                        ✅ Detection Radius
                    </button>

                    <button className={`toggle-btn ${showPath ? 'active-blue' : ''}`} onClick={() => setShowPath(!showPath)}>
                        👁️ Vision Cone
                    </button>

                    <button className={`toggle-btn ${showRiskZones ? 'active-red' : ''}`} onClick={() => setShowRiskZones(!showRiskZones)}>
                        🛑 Village Buffer
                    </button>
                </div>
            </div>

            {/* 4. Bottom Panel (Dynamic Details) */}
            <div className="bottom-panel-grid">
                {/* Detail Card 1: Source */}
                <div className="info-card card">
                    <div className="flex justify-between items-center mb-2">
                        <span className="text-xs text-gray-500 uppercase font-bold">Source</span>
                        <Camera size={16} className="text-gray-400" />
                    </div>
                    <div className="text-lg font-bold text-gray-800">
                        {selectedEntity?.detectedBy || selectedEntity?.id || 'Unknown'}
                    </div>
                    <div className="text-sm text-gray-500 mt-1">
                        {selectedEntity?.location || 'Lat: ' + selectedEntity?.pos?.[0].toFixed(3)}
                    </div>
                </div>

                {/* Detail Card 2: Intelligence */}
                <div className="ai-card card">
                    <div className="flex justify-between items-start mb-2">
                        <span className="ai-badge">
                            {selectedEntity?.confidence ? `AI Confidence: ${selectedEntity.confidence}%` : 'Status'}
                        </span>
                        <Info size={16} className="text-blue-500" />
                    </div>
                    <div className="prediction-list text-sm font-medium text-blue-900 mt-2">
                        {selectedEntity?.type ? (
                            <>
                                Type: {selectedEntity.type} <br />
                                Risk: {selectedEntity.risk} <br />
                                Time: {selectedEntity.time}
                            </>
                        ) : (
                            "Select an animal for prediction."
                        )}
                    </div>
                </div>

                {/* Action Buttons */}
                <div className="action-buttons">
                    <button className="btn-action focus" onClick={handleFocus}>
                        <Target size={20} />
                        Focus Map
                    </button>
                    <button className="btn-action alert" onClick={handleCreateAlert}>
                        <Bell size={20} />
                        Create Alert
                    </button>
                </div>
            </div>
        </div>
    );
};

export default AnimalTracking;
