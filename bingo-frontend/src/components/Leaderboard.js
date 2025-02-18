import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const Leaderboard = () => {
  const [players, setPlayers] = useState([]);

  useEffect(() => {
    axios.get(`${API_URL}/leaderboard/`)
      .then(response => setPlayers(response.data))
      .catch(error => console.log(error));
  }, []);

  return (
    <div>
      <h2>Leaderboard</h2>
      <ul>
        {players.map((player, index) => (
          <li key={index}>{player.user} - {player.points} pts</li>
        ))}
      </ul>
    </div>
  );
};

export default Leaderboard;