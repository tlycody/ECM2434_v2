// NotificationManager.js - Fixed Version

import React, { useState, useEffect, useCallback } from 'react';

import Notification from './Notification';

// Extend the window object to include custom properties
window.showNotification = window.showNotification || function(type, message, duration, action, icon) {};
window.showTaskCompletion = window.showTaskCompletion || function(taskName, points) {};
window.showPatternCompletion = window.showPatternCompletion || function(patternType, points) {};
window.showProgressUpdate = window.showProgressUpdate || function(completed, total) {};

const NotificationManager = () => {
  const [notifications, setNotifications] = useState([]);

  // Function to get shown notifications from localStorage
  const getShownNotifications = useCallback(() => {
    try {
      const stored = localStorage.getItem('shown_notifications');
      return stored ? JSON.parse(stored) : {};
    } catch (e) {
      console.error("Error reading notifications from storage:", e);
      return {};
    }
  }, []);


  // Function to mark a notification as shown
  const markNotificationAsShown = useCallback((key) => {
    try {
      const shown = getShownNotifications();
      shown[key] = Date.now();
      localStorage.setItem('shown_notifications', JSON.stringify(shown));
    } catch (e) {
      console.error("Error saving notification to storage:", e);
    }
  }, [getShownNotifications]);

  // Function to check if a notification was shown recently
  const wasNotificationShownRecently = useCallback((key, timeWindowMs = 60000) => { // 1 minute default
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
  }, [getShownNotifications]);

  // Function to add a new notification with duplicate prevention
  const addNotification = useCallback((type, message, duration = 4000, action = null, icon = null) => {
    // Create a unique key for this notification
    const notificationKey = `${type}-${message}`;

    if (wasNotificationShownRecently(notificationKey)) {
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
  }, [markNotificationAsShown, wasNotificationShownRecently]);

  // Function to remove a notification
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // Set up event listeners for notifications
  useEffect(() => {
    // Clean up any existing event listeners
    const handleAddNotification = (event) => {
      const { type, message, duration, action, icon } = event.detail;
      addNotification(type, message, duration, action, icon);
    };

    const handleTaskCompletion = (event) => {
      const { taskName, points } = event.detail;

      // Create a unique key for this notification
      const notificationKey = `task-${taskName}-${points}`;

      // Skip if already shown recently
      if (wasNotificationShownRecently(notificationKey)) {
        return;
      }

      // Add notification
      addNotification(
        'task-complete',
        `Completed: ${taskName} (+${points} points)`,
        5000,
        { label: 'View Profile', onClick: () => window.location.href = '/userprofile' }
      );
    };

    const handlePatternCompletion = (event) => {
      const { patternType, points } = event.detail;

      // Get pattern notification key from localStorage
      const shownPatterns = localStorage.getItem('shown_pattern_notifications');
      const parsedPatterns = shownPatterns ? JSON.parse(shownPatterns) : [];

      // Skip if this pattern is in our shown patterns list
      if (parsedPatterns.includes(patternType)) {
        console.log(`Pattern ${patternType} notification already shown, skipping`);
        return;
      }

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

    // Progress notifications - skip for now, they're causing too many duplicates
    const handleProgressUpdate = (event) => {
      // Don't create progress notifications at all
      return;
    };

    // Add event listeners
    window.addEventListener('addNotification', handleAddNotification);
    window.addEventListener('taskCompletion', handleTaskCompletion);
    window.addEventListener('patternCompletion', handlePatternCompletion);
    window.addEventListener('progressUpdate', handleProgressUpdate);

    // Set up global notification functions
    window.showNotification = (type, message, duration, action, icon) => {
      // Skip progress notifications entirely
      if (type === 'progress') return;

      // Create unique key
      const notificationKey = `${type}-${message}`;

      // Skip if shown recently (within 10 seconds)
      if (wasNotificationShownRecently(notificationKey, 10000)) {
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
    };

    // Clean up
    return () => {
      window.removeEventListener('addNotification', handleAddNotification);
      window.removeEventListener('taskCompletion', handleTaskCompletion);
      window.removeEventListener('patternCompletion', handlePatternCompletion);
      window.removeEventListener('progressUpdate', handleProgressUpdate);

      delete window.showNotification;
      delete window.showTaskCompletion;
      delete window.showPatternCompletion;
      delete window.showProgressUpdate;
    };
  }, [addNotification, wasNotificationShownRecently]);

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