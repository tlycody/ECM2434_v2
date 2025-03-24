// Notification Component - Enhanced

import React, { useState, useEffect } from 'react';
import './Notification.css';

const Notification = ({
  type,
  message,
  duration = 4000,
  onClose,
  action,
  icon 
}) => {
  const [isVisible, setIsVisible] = useState(true);
  const [progress, setProgress] = useState(100);
  const [intervalId, setIntervalId] = useState(null);

  // Icons based on notification type
  const getIcon = () => {
    if (icon) return icon;

    switch (type) {
      case 'success':
      case 'task-complete':
        return '✅';
      case 'error':
        return '❌';
      case 'info':
        return 'ℹ️';
      case 'warning':
      case 'reminder':
        return '⚠️';
      case 'achievement':
      case 'pattern-complete':
        return '🏆';
      case 'progress':
        return '📊';
      case 'end-of-month':
        return '📆';
      default:
        return '📢';
    }
  };

  // Automatically hide the notification after duration
  useEffect(() => {
    // Start progress bar
    if (duration > 0) {
      const startTime = Date.now();
      const id = setInterval(() => {
        const elapsedTime = Date.now() - startTime;
        const remainingPercentage = 100 - (elapsedTime / duration * 100);

        if (remainingPercentage <= 0) {
          clearInterval(id);
          setIsVisible(false);
          if (onClose) setTimeout(onClose, 400); 
        } else {
          setProgress(remainingPercentage);
        }
      }, 16); 

      setIntervalId(id);

      return () => clearInterval(id);
    }
  }, [duration, onClose]);

  // Handle manual close
  const handleClose = () => {
    if (intervalId) clearInterval(intervalId);
    setIsVisible(false);
    if (onClose) setTimeout(onClose, 400);
  };

  // Handle action button click
  const handleAction = () => {
    if (action && action.onClick) {
      action.onClick();
    }
    handleClose();
  };

  return (
    <div className={`notification ${type} ${isVisible ? 'visible' : 'hidden'}`}>
      <div className="notification-icon">
        {getIcon()}
      </div>
      <div className="notification-content">
        {message}
      </div>

      {action && (
        <button
          className="notification-action"
          onClick={handleAction}
        >
          {action.label}
        </button>
      )}

      <button className="notification-close" onClick={handleClose}>
        &times;
      </button>

      {duration > 0 && (
        <div className="notification-progress">
          <div
            className="notification-progress-bar"
            style={{
              width: `${progress}%`,
              backgroundColor: type === 'task-complete' ? '#4CAF50' :
                              type === 'pattern-complete' ? '#8E44AD' :
                              type === 'reminder' ? '#FF5722' : null
            }}
          ></div>
        </div>
      )}
    </div>
  );
};

export default Notification;