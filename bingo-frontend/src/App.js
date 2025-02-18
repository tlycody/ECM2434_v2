import React from 'react';
import { BrowserRouter as Router, Route, Routes, Navigate } from 'react-router-dom';
import BingoBoard from './components/BingoBoard';
import Leaderboard from './components/Leaderboard';
import Login from './components/Login';
import Register from './components/Register';

const PrivateRoute = ({ children }) => {
  return localStorage.getItem('token') ? children : <Navigate to="/login" />;
};

function App() {
  return (
    <Router>
      <div className="container">
        <h1>Bingo Game</h1>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/" element={<PrivateRoute><BingoBoard /></PrivateRoute>} />
          <Route path="/leaderboard" element={<PrivateRoute><Leaderboard /></PrivateRoute>} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
