import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom'; 
import axios from 'axios';
import './Leaderboard.css';
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Leaderboard = () => {
  const [players, setPlayers] = useState([]);
  const [error, setError] = useState(null);
  const navigate = useNavigate();
  const[loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    axios.get(`${API_URL}/leaderboard/`)
      .then(response => {
        console.log("Leaderboard fetched:", response.data);
        setPlayers(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching leaderboard:", error);
        setError("Failed to load leaderboard. Please try again.");
        setLoading(false);
      });
  }, []);

  return (
    <div className="leaderboard-container">
      <h2>🏆 Leaderboard</h2>
      {loading ? (
        <p>Loading leaderboard...</p>
      ) : error ? (
        <p className="error-message">{error}</p>
      ) : (
        <ul className="leaderboard-list">
          {players.map((player, index) => (
            <li key={index} className={index % 2 === 0 ? "leaderboard-item even" : "leaderboard-item odd"}>
              <span className="rank">{index + 1}.</span>
              <span className="name">{player.user}</span>
              <span className="points">{player.points} pts</span>
            </li>
          ))}
        </ul>
      )}
      <button onClick={() => navigate('/bingo')}>Back to Bingo</button>
    </div>
  );
};

export default Leaderboard;
