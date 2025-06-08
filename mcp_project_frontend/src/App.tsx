import React from 'react';
import { Routes, Route } from 'react-router-dom';
import HelpPage from './pages/HelpPage';
import DashboardPage from './pages/DashboardPage';

const App = () => (
  <Routes>
    <Route path="/dashboard" element={<DashboardPage />} />
    <Route path="/help" element={<HelpPage />} />
    {/* ...other routes... */}
  </Routes>
);

export default App; 