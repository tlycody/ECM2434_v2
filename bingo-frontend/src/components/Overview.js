// ============================
// Overview Component
// ============================

import React from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Overview.css';


const Overview = () => {
  const navigate = useNavigate(); // React Router navigation hook

  return (
    <div className="overview-container">
      {/* Title */}
      <h2>Bingo Game Overview</h2>

      {/* Game Description Section */}
      <div className="overview-section">
        <h3>Overview</h3>
        <p>
          This is a simple and engaging bingo-style game with eco-friendly tasks. Each task on the bingo board falls into one of 
          two categories: upload an image/video or scan a QR code.
        </p>
      </div>

      {/* How to Play Section */}
      <div className="overview-section">
        <h3>How to Play</h3>
        <ol className="instructions-list">
          <li>
            <span className="instruction-title">Create an account</span>
            <p>Register or login to get your personalized Bingo board</p>
          </li>
          <li>
            <span className="instruction-title">Complete tasks</span>
            <p> Select a Task - Read the tasks on the bingo board and click on one to begin.</p>
            <p> Follow Instructions - Carefully read the task details before proceeding. </p>
            <p> Submit Proof - Upload your image/video or scan the QR code as required. </p>
            <p> Wait for Confirmation - Your submission will be reviewed. Once approved, you'll receive a stamp. </p>
            <p> Form Bingo Patterns - Keep completing tasks to create bingo patterns. </p>
          </li>
          <li>
            <span className="instruction-title">Bonus points</span>
            <p> Earn points for each completed task. </p>
            <p> <Link to="/patterns" className="pattern-link"> Unique bingo patterns</Link> grant bonus points. </p>
            <p> Track your progress and points on the leaderboard.</p>
          </li>
        </ol>
      </div>

            {/* Sustainability Badges Section */}
            <div className="sustainability-badges">
        <h3>Sustainability Badges</h3>
        {badges.length > 0 ? (
          <div className="badges-grid">
            {badges.map(badge => (
              <div key={badge.id} className="badge-item">
                <div className="badge-emoji">{getBadgeEmoji(badge.type)}</div>
                <div className="badge-info">
                  <h4>{badge.name}</h4>
                  <p className="badge-points">+{badge.bonus_points} points</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="badge-hints">
            <p>Complete patterns on your bingo board to earn badges!</p>
            <div className="hint-icons">
              <span className="hint-item">♻️ Ozone Defender</span>
              <span className="hint-item">❌ Xtra Green</span>
              <span className="hint-item">🌈 Healthy Hero</span>
              <span className="hint-item">🌱 Green Champion</span>
            </div>
          </div>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="navigation-buttons">
        <button onClick={() => navigate('/')} className="action-button">Back to Home</button>
      </div>
    </div>
  );
};

export default Overview;