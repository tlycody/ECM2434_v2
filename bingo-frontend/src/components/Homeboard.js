// Homeboard Component

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom'; 
import axios from 'axios';
import './Homeboard.css';

const API_URL = "https://ecm2434-v3.onrender.com";

const Homeboard = () => {
  // State variables for leaderboard data, errors, and loading status
  const [players, setPlayers] = useState([]);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Fetch Leaderboard Data on Component Mount

  useEffect(() => {
    setLoading(true); 
    axios.get(`${API_URL}/api/leaderboard/`)
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
  }, []); // Runs only on mount (empty dependency array)

  // Render Leaderboard UI

  return (
    <div className="leaderboard-container">
      {/* Title */}
      <h2>🏆 Leaderboard</h2>

      {/* Loading and Error Handling */}
      {loading ? (
        <p>Loading leaderboard...</p>
      ) : error ? (
        <p className="error-message">{error}</p>
      ) : (
        <ul className="leaderboard-list">
          {/* Mapping over player data to display rankings */}
          {players.map((player, index) => (
            <li 
              key={index} 
              className={index % 2 === 0 ? "leaderboard-item even" : "leaderboard-item odd"}
            >
              <span className="rank">{index + 1}.</span>
              <span className="name">{player.user}</span>
              <span className="points">{player.points} pts</span>
            </li>
          ))}
        </ul>
      )}

      {/* Navigation Buttons */}
      <button onClick={() => navigate('/')}>Back to Home</button>
    </div>
  );
};

export default Homeboard;