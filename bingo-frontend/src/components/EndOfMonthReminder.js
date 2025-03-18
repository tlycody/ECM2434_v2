// ============================
// End of Month Reminder Component
// ============================

import React, { useState, useEffect } from 'react';
import './EndOfMonthReminder.css';

const EndOfMonthReminder = ({ onClose, onViewPatterns }) => {
  const [daysLeft, setDaysLeft] = useState(3);
  const [closing, setClosing] = useState(false);

  // Calculate days left in the month
  useEffect(() => {
    const calculateDaysLeft = () => {
      const now = new Date();
      const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
      return lastDay - now.getDate();
    };

    setDaysLeft(calculateDaysLeft());
  }, []);

  // Handle close with animation
  const handleClose = () => {
    setClosing(true);
    setTimeout(() => {
      if (onClose) onClose();
    }, 500); // Match the CSS animation duration
  };

  // Handle view patterns button
  const handleViewPatterns = () => {
    if (onViewPatterns) onViewPatterns();
    handleClose();
  };

  // Skip reminder if more than 3 days left
  if (daysLeft > 3) return null;

  return (
    <div className={`eom-reminder-container ${closing ? 'eom-closing' : ''}`}>
      <div className="eom-reminder-icon">📆</div>
      <div className="eom-reminder-content">
        <h3 className="eom-reminder-title">
          {daysLeft === 0 ? 'Last Day of the Month!' : `${daysLeft} Day${daysLeft > 1 ? 's' : ''} Left!`}
        </h3>
        <p className="eom-reminder-text">
          {daysLeft === 0
            ? "Today is the last day to complete your bingo patterns for this month's challenge!"
            : `Only ${daysLeft} day${daysLeft > 1 ? 's' : ''} left to complete your bingo patterns for this month's challenge!`
          }
        </p>
        <div className="eom-reminder-progress">
          <div className="eom-progress-container">
            <div className="eom-progress-bar" style={{ width: `${Math.max(5, 100 - (daysLeft * 33.3))}%` }}></div>
          </div>
          <div className="eom-days-counter">{daysLeft} {daysLeft === 1 ? 'day' : 'days'} remaining</div>
        </div>
        <div className="eom-reminder-buttons">
          <button className="eom-patterns-button" onClick={handleViewPatterns}>
            View My Patterns
          </button>
          <button className="eom-close-button" onClick={handleClose}>
            Dismiss
          </button>
        </div>
      </div>
      <button className="eom-reminder-x" onClick={handleClose}>&times;</button>
    </div>
  );
};

export default EndOfMonthReminder;