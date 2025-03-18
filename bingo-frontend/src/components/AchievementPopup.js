// ============================
// Achievement Popup Component - Enhanced
// ============================

import React, { useEffect, useState } from 'react';
import './AchievementPopup.css';

const AchievementPopup = ({
  title = 'Achievement Unlocked!',
  achievement,
  points = 0,
  badgeEmoji = '🏆',
  onClose,
  autoClose = true,
  autoCloseTime = 6000
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [starbursts, setStarbursts] = useState([]);
  const [confetti, setConfetti] = useState([]);

  // Auto-close after specified time
  useEffect(() => {
    if (autoClose) {
      const timer = setTimeout(() => {
        setIsVisible(false);
        setTimeout(() => {
          if (onClose) onClose();
        }, 500); // Give time for exit animation
      }, autoCloseTime);

      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseTime, onClose]);

  // Generate starburst effects
  useEffect(() => {
    const burst = [];
    for (let i = 0; i < 5; i++) {
      burst.push({
        id: i,
        left: Math.random() * 100 + '%',
        top: Math.random() * 100 + '%',
        delay: Math.random() * 1 + 's'
      });
    }
    setStarbursts(burst);

    // Generate confetti with different shapes
    const shapes = ['square', 'circle', 'triangle'];
    const colors = ['#8E44AD', '#3498db', '#e74c3c', '#f1c40f', '#2ecc71', '#e67e22', '#1abc9c'];
    const confettiPieces = [];

    for (let i = 0; i < 30; i++) {
      confettiPieces.push({
        id: i,
        left: Math.random() * 100 + '%',
        top: '-5%',
        delay: Math.random() * 1 + 's',
        duration: 3 + Math.random() * 2 + 's',
        shape: shapes[Math.floor(Math.random() * shapes.length)],
        color: colors[Math.floor(Math.random() * colors.length)],
        size: 5 + Math.random() * 10
      });
    }

    setConfetti(confettiPieces);
  }, []);

  // Handle animation end and close
  const handleClose = () => {
    setIsVisible(false);
    setTimeout(() => {
      if (onClose) onClose();
    }, 500);
  };

  return (
    <div className={`achievement-popup-overlay ${isVisible ? 'visible' : 'hidden'}`}>
      <div className={`achievement-popup ${isVisible ? 'visible' : 'hidden'}`}>
        <div className="achievement-header">
          <div className="achievement-trophy">{badgeEmoji}</div>
          <h2 className="achievement-title">{title}</h2>
          <button className="achievement-close" onClick={handleClose}>&times;</button>
        </div>

        <div className="achievement-content">
          <div className="achievement-badge">
            <div className="badge-icon">
              {badgeEmoji}
              <div className="badge-glow"></div>
            </div>
          </div>

          <div className="achievement-name rainbow-text">
            {achievement}
          </div>

          {points > 0 && (
            <div className="achievement-points">
              +{points} Bonus Points!
            </div>
          )}

          <div className="achievement-animation">
            <div className="confetti-container">
              {confetti.map(c => (
                <div
                  key={c.id}
                  className={`confetti ${c.shape}`}
                  style={{
                    left: c.left,
                    top: c.top,
                    animationDelay: c.delay,
                    animationDuration: c.duration,
                    backgroundColor: c.shape !== 'triangle' ? c.color : 'transparent',
                    borderBottomColor: c.shape === 'triangle' ? c.color : 'transparent',
                    width: c.shape === 'triangle' ? 0 : c.size + 'px',
                    height: c.shape === 'triangle' ? 0 : c.size + 'px',
                    borderLeftWidth: c.shape === 'triangle' ? c.size/2 + 'px' : 0,
                    borderRightWidth: c.shape === 'triangle' ? c.size/2 + 'px' : 0,
                    borderBottomWidth: c.shape === 'triangle' ? c.size + 'px' : 0
                  }}
                ></div>
              ))}
            </div>
          </div>

          <button className="achievement-button" onClick={handleClose}>
            Awesome!
          </button>
        </div>

        {/* Starburst effect */}
        <div className="achievement-starburst">
          {starbursts.map(star => (
            <div
              key={star.id}
              className="starburst"
              style={{
                left: star.left,
                top: star.top,
                animationDelay: star.delay
              }}
            ></div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default AchievementPopup;