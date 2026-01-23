import React from 'react';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import MainLayout from './layout/MainLayout';
import Dashboard from './pages/Dashboard';
import Alerts from './pages/Alerts';
import LiveMonitor from './pages/LiveMonitor';
import AnimalTracking from './pages/AnimalTracking';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<Dashboard />} />
          <Route path="alerts" element={<Alerts />} />
          <Route path="live" element={<LiveMonitor />} />
          <Route path="tracking" element={<AnimalTracking />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
