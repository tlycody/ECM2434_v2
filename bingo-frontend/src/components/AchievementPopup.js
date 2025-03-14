// ============================
// Achievement Popup Component
// ============================

import React, { useEffect } from 'react';
import './AchievementPopup.css';

const AchievementPopup = ({
  title = 'Achievement Unlocked!',
  achievement,
  points = 0,
  onClose,
  autoClose = true,
  autoCloseTime = 6000
}) => {
  // Auto-close after specified time
  useEffect(() => {
    if (autoClose) {
      const timer = setTimeout(() => {
        if (onClose) onClose();
      }, autoCloseTime);

      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseTime, onClose]);

  return (
    <div className="achievement-popup-overlay">
      <div className="achievement-popup">
        <div className="achievement-header">
          <div className="achievement-trophy">🏆</div>
          <h2 className="achievement-title">{title}</h2>
          <button className="achievement-close" onClick={onClose}>&times;</button>
        </div>

        <div className="achievement-content">
          <div className="achievement-name">
            {achievement}
          </div>

          {points > 0 && (
            <div className="achievement-points">
              +{points} Bonus Points!
            </div>
          )}

          <div className="achievement-animation">
            <div className="confetti-container">
              <div className="confetti"></div>
              <div className="confetti"></div>
              <div className="confetti"></div>
              <div className="confetti"></div>
              <div className="confetti"></div>
              <div className="confetti"></div>
              <div className="confetti"></div>
              <div className="confetti"></div>
              <div className="confetti"></div>
              <div className="confetti"></div>
            </div>
          </div>

          <button className="achievement-button" onClick={onClose}>
            Awesome!
          </button>
        </div>
      </div>
    </div>
  );
};

export default AchievementPopup;