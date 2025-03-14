// ============================
// Notification Component
// ============================

import React, { useState, useEffect } from 'react';
import './Notification.css';

const Notification = ({ type, message, duration = 4000, onClose }) => {
  const [isVisible, setIsVisible] = useState(true);

  // Automatically hide the notification after duration
  useEffect(() => {
    const timer = setTimeout(() => {
      setIsVisible(false);
      if (onClose) setTimeout(onClose, 300); // Allow animation to complete before removing
    }, duration);

    return () => clearTimeout(timer);
  }, [duration, onClose]);

  // Handle manual close
  const handleClose = () => {
    setIsVisible(false);
    if (onClose) setTimeout(onClose, 300);
  };

  return (
    <div className={`notification ${type} ${isVisible ? 'visible' : 'hidden'}`}>
      <div className="notification-icon">
        {type === 'success' && '✅'}
        {type === 'error' && '❌'}
        {type === 'info' && 'ℹ️'}
        {type === 'warning' && '⚠️'}
        {type === 'achievement' && '🏆'}
      </div>
      <div className="notification-content">
        {message}
      </div>
      <button className="notification-close" onClick={handleClose}>
        &times;
      </button>
    </div>
  );
};

export default Notification;