// ============================
// Notification Manager Component
// ============================

import React, { useState, useEffect, useCallback } from 'react';
import Notification from './Notification';

const NotificationManager = () => {
  const [notifications, setNotifications] = useState([]);

  // Function to add a new notification
  const addNotification = useCallback((type, message, duration = 4000) => {
    const id = Date.now();
    setNotifications(prev => [...prev, { id, type, message, duration }]);
    return id;
  }, []);

  // Function to remove a notification
  const removeNotification = useCallback((id) => {
    setNotifications(prev => prev.filter(notification => notification.id !== id));
  }, []);

  // Create global event listeners for adding notifications
  useEffect(() => {
    // Add notification event
    const handleAddNotification = (event) => {
      const { type, message, duration } = event.detail;
      addNotification(type, message, duration);
    };

    // Listen for custom events to add notifications
    window.addEventListener('addNotification', handleAddNotification);

    return () => {
      window.removeEventListener('addNotification', handleAddNotification);
    };
  }, [addNotification]);

  // Helper function to dispatch notifications from anywhere
  useEffect(() => {
    // Make the function globally available
    window.showNotification = (type, message, duration) => {
      const event = new CustomEvent('addNotification', {
        detail: { type, message, duration }
      });
      window.dispatchEvent(event);
    };

    return () => {
      delete window.showNotification;
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
          onClose={() => removeNotification(notification.id)}
        />
      ))}
    </div>
  );
};

export default NotificationManager;