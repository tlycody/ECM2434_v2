// ============================
// DRASTIC FIX for NotificationManager.js
// ============================

// Replace your entire NotificationManager.js with this version
// This completely rewrites notification handling to prevent duplicates

import React, { useState, useEffect, useCallback, useRef } from 'react';
import Notification from './Notification';

const NotificationManager = () => {
  const [notifications, setNotifications] = useState([]);
  const [intervalIds, setIntervalIds] = useState({});

  // Important: Store already shown notifications in session storage
  // This persists even if component re-renders
  const getShownNotifications = () => {
    try {
      const stored = sessionStorage.getItem('shown_notifications');
      return stored ? JSON.parse(stored) : {};
    } catch (e) {
      console.error("Error reading session storage:", e);
      return {};
    }
  };

  const markNotificationAsShown = (key) => {
    try {
      const shown = getShownNotifications();
      shown[key] = Date.now();
      sessionStorage.setItem('shown_notifications', JSON.stringify(shown));
    } catch (e) {
      console.error("Error writing to session storage:", e);
    }
  };

  const wasNotificationShownRecently = (key, timeWindowMs = 5000) => {
    try {
      const shown = getShownNotifications();
      const timestamp = shown[key];

      if (!timestamp) return false;

      // Check if notification was shown in the last X milliseconds
      return (Date.now() - timestamp) < timeWindowMs;
    } catch (e) {
      console.error("Error checking notification history:", e);
      return false;
    }
  };

  // Function to add a new notification with strong duplicate prevention
  const addNotification = useCallback((type, message, duration = 4000, action = null, icon = null) => {
    // Create a unique key for this notification
    const notificationKey = `${type}-${message}`;

    // STRONG duplicate prevention - check if we've shown this recently
    if (wasNotificationShownRecently(notificationKey, 10000)) {
      console.log("Preventing duplicate notification:", message);
      return null;
    }

    // Mark this notification as shown
    markNotificationAsShown(notificationKey);

    // Add to state
    const id = Date.now();
    setNotifications(prev => {
      // Also check the current state for this exact notification
      if (prev.some(n => n.type === type && n.message === message)) {
        return prev; // Don't add duplicate
      }
      return [...prev.slice(-2), { id, type, message, duration, action, icon }];
    });

    return id;
  }, []);

  // Function to remove a notification
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // Clear all event listeners on component mount
  useEffect(() => {
    // Clean up any existing event listeners to prevent duplicates
    const events = [
      'addNotification',
      'taskCompletion',
      'patternCompletion',
      'progressUpdate'
    ];

    // Create empty handler functions to replace existing ones
    const emptyHandler = () => {};

    events.forEach(eventName => {
      // First remove any existing handlers
      window.removeEventListener(eventName, emptyHandler);
    });

    // Now set up our handlers with stronger duplicate prevention
    const handleAddNotification = (event) => {
      const { type, message, duration, action, icon } = event.detail;
      addNotification(type, message, duration, action, icon);
    };

    const handleTaskCompletion = (event) => {
      const { taskName, points } = event.detail;

      // Create a unique key for this notification
      const notificationKey = `task-${taskName}-${points}`;

      // Skip if already shown recently
      if (wasNotificationShownRecently(notificationKey, 10000)) {
        return;
      }

      // Mark as shown and add notification
      markNotificationAsShown(notificationKey);
      addNotification(
        'task-complete',
        `Completed: ${taskName} (+${points} points)`,
        5000,
        { label: 'View Profile', onClick: () => window.location.href = '/userprofile' }
      );
    };

    const handlePatternCompletion = (event) => {
      const { patternType, points } = event.detail;

      // Create a unique key
      const notificationKey = `pattern-${patternType}`;

      // Skip if shown recently
      if (wasNotificationShownRecently(notificationKey, 10000)) {
        return;
      }

      markNotificationAsShown(notificationKey);

      // Get emoji
      let emoji;
      switch (patternType) {
        case 'H': emoji = '➖'; break;
        case 'V': emoji = '⏐'; break;
        case 'X': emoji = '✖️'; break;
        case 'O': emoji = '⭕'; break;
        default: emoji = '🎯';
      }

      addNotification(
        'pattern-complete',
        `Pattern complete: ${patternType} (+${points} bonus points)`,
        6000,
        { label: 'View Patterns', onClick: () => window.location.href = '/patterns' },
        emoji
      );
    };

    const handleProgressUpdate = (event) => {
      const { completed, total } = event.detail;

      // CRITICAL: Skip progress notifications entirely - they cause most problems
      return;

      // Alternatively, implement with strong duplicate prevention
      /*
      // Create a unique key
      const notificationKey = `progress-${completed}-${total}`;

      // Skip if shown in the last minute
      if (wasNotificationShownRecently(notificationKey, 60000)) {
        return;
      }

      markNotificationAsShown(notificationKey);

      // Only process if total > 0
      if (total > 0) {
        const percentage = Math.round((completed / total) * 100);
        addNotification(
          'progress',
          `Your progress: ${completed}/${total} tasks (${percentage}%)`,
          5000
        );
      }
      */
    };

    // Add event listeners with our handlers
    window.addEventListener('addNotification', handleAddNotification);
    window.addEventListener('taskCompletion', handleTaskCompletion);
    window.addEventListener('patternCompletion', handlePatternCompletion);
    window.addEventListener('progressUpdate', handleProgressUpdate);

    // Clean up all handlers when component unmounts
    return () => {
      window.removeEventListener('addNotification', handleAddNotification);
      window.removeEventListener('taskCompletion', handleTaskCompletion);
      window.removeEventListener('patternCompletion', handlePatternCompletion);
      window.removeEventListener('progressUpdate', handleProgressUpdate);

      // Also clear any intervals
      Object.values(intervalIds).forEach(clearInterval);
    };
  }, [addNotification, intervalIds]);

  // Set up global handlers
  useEffect(() => {
    window.showNotification = (type, message, duration, action, icon) => {
      // Skip progress notifications entirely
      if (type === 'progress') return;

      // Create unique key
      const notificationKey = `${type}-${message}`;

      // Skip if shown recently
      if (wasNotificationShownRecently(notificationKey, 5000)) {
        return;
      }

      // Dispatch event
      const event = new CustomEvent('addNotification', {
        detail: { type, message, duration, action, icon }
      });
      window.dispatchEvent(event);
    };

    window.showTaskCompletion = (taskName, points) => {
      const event = new CustomEvent('taskCompletion', {
        detail: { taskName, points }
      });
      window.dispatchEvent(event);
    };

    window.showPatternCompletion = (patternType, points) => {
      const event = new CustomEvent('patternCompletion', {
        detail: { patternType, points }
      });
      window.dispatchEvent(event);
    };

    window.showProgressUpdate = (completed, total) => {
      // Skip progress notifications entirely
      return;

      /*
      // Original code:
      const event = new CustomEvent('progressUpdate', {
        detail: { completed, total }
      });
      window.dispatchEvent(event);
      */
    };

    return () => {
      delete window.showNotification;
      delete window.showTaskCompletion;
      delete window.showPatternCompletion;
      delete window.showProgressUpdate;
    };
  }, []);

  return (
    <div className="notification-container">
      {notifications.map(notification => (
        <Notification
          key={notification.id}
          type={notification.type}
          message={notification.message}
          duration={notification.duration}
          action={notification.action}
          icon={notification.icon}
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
};

export default NotificationManager;