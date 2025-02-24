import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './Leaderboard.css';

const API_URL = process.env.REACT_APP_API_URL;

const Leaderboard = () => {
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    axios.get(`${API_URL}/leaderboard/`)
      .then(response => setPlayers(response.data))
      .catch(error => console.log(error));
  }, []);

  return (
    <div className="leaderboard-container">
      <h2 className="leaderboard-title">🏆 Leaderboard</h2>
      <ul className="leaderboard-list">
        {players.map((player, index) => (
          <li key={index} className={index % 2 === 0 ? "leaderboard-item even" : "leaderboard-item odd"}>
            <span className="rank">{index + 1}.</span>
            <span className="name">{player.user}</span>
            <span className="points">{player.points} pts</span>
          </li>
        ))}
      </ul>
    </div>
  );
};

export default Leaderboard;
