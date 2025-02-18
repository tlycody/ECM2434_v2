import React from 'react';
import { BrowserRouter as Router, Route, Routes } from 'react-router-dom';
import BingoBoard from './components/BingoBoard';
import Leaderboard from './components/Leaderboard';

function App() {
  return (
    <Router>
      <div className="container">
        <h1>Bingo Game</h1>
        <Routes>
          <Route path="/" element={<BingoBoard />} />
          <Route path="/leaderboard" element={<Leaderboard />} />
        </Routes>
      </div>
    </Router>
  );
}

export default App;
