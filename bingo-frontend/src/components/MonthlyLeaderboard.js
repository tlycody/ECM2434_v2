import React, { useState, useEffect } from 'react';

const MonthlyLeaderboard = () => {
  const [leaderboard, setLeaderboard] = useState([]);

  useEffect(() => {
    fetch('/api/monthly-leaderboard/')
      .then(response => response.json())
      .then(data => setLeaderboard(data.monthly_leaderboard))
      .catch(error => console.error('Error fetching leaderboard:', error));
  }, []);

  return (
    <div className="leaderboard-container">
      <h2>Monthly Leaderboard</h2>
      <table>
        <thead>
          <tr>
            <th>Rank</th>
            <th>Player</th>
            <th>Points</th>
          </tr>
        </thead>
        <tbody>
          {leaderboard.map((entry, index) => (
            <tr key={index}>
              <td>{index + 1}</td>
              <td>{entry.username}</td>
              <td>{entry.points}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MonthlyLeaderboard;

