import React from 'react';
import { Routes, Route } from 'react-router-dom';
import Home from './components/Home';
import Profile from './components/Profile';
import Login from './components/Login';
import Register from './components/Register';
import Leaderboard from './components/Leaderboard';
import BingoBoard from './components/BingoBoard';

const App = () => {
  return (
    <div>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/profile" element={<Profile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/leaderboard" element={<Leaderboard />} />
        <Route path="/bingo" element={<BingoBoard />} />
      </Routes>
    </div>
  );
};

export default App;
