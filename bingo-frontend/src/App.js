import React from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import Home from './components/Home';
import Userprofile from './components/Userprofile';
import Login from './components/Login';
import Register from './components/Register';
import Leaderboard from './components/Leaderboard';
import BingoBoard from './components/BingoBoard';
import Upload from './components/Upload';
import Scan from './components/Scan';
import PrivacyPolicy from './components/PrivacyPolicy'; 

const App = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/userprofile" element={<Userprofile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/privacy-policy" element={<PrivacyPolicy />} />
        <Route path="/bingo" element={<BingoBoard />} />
        <Route path="/upload" element={<Upload />} />
        <Route path="/scan" element={<Scan />} />
        <Route path="/developer-dashboard" element={
          localStorage.getItem('userProfile') === 'Developer' 
            ? <iframe src="/developer-front.html" style={{width: '100%', height: '100vh', border: 'none'}} />
            : <Navigate to="/login" />
        } />
      </Routes>
    </div>
  );
};

export default App;
