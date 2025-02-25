// ============================
// Main Application Routing
// ============================

import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';

// Importing Application Components
import Home from './components/Home';
import Userprofile from './components/Userprofile';
import Login from './components/Login';
import Register from './components/Register';
import Leaderboard from './components/Leaderboard';
import BingoBoard from './components/BingoBoard';
import Upload from './components/Upload';
import Scan from './components/Scan';
import GameKeeper from './components/GameKeeper';
import PrivacyPolicy from './components/PrivacyPolicy'; 

const App = () => {
  return (
    <div>
      <Routes>
        {/* Home Route */}
        <Route path="/" element={<Home />} />

        {/* User Profile Page */}
        <Route path="/userprofile" element={<Userprofile />} />

        {/* Authentication Routes */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />

        {/* Game Features Routes */}
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        <Route path="/bingo" element={<BingoBoard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/gamekeeper" element={<GameKeeper />} />
        <Route path="/scan" element={<Scan />} />

        {/* Developer Dashboard - Restricted Access */}
        <Route 
          path="/developer-dashboard" 
          element={
            localStorage.getItem('userProfile') === 'Developer' 
              ? <iframe 
                  src="/developer-front.html" 
                  style={{ width: '100%', height: '100vh', border: 'none' }} 
                />
              : <Navigate to="/login" /> // Redirect to login if user is not a developer
          } 
        />
      </Routes>
    </div>
  );
};

export default App;
