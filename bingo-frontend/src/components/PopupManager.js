// ============================
// Popup Manager Component
// ============================

import React, { useState, useEffect, useCallback } from 'react';
import Popup from './Popup';

const PopupManager = () => {
  const [popups, setPopups] = useState([]);
  const [activePopup, setActivePopup] = useState(null);

  // Process popup queue when active popup changes
  useEffect(() => {
    if (!activePopup && popups.length > 0) {
      // Set the first popup in the queue as active
      setActivePopup(popups[0]);
      // Remove it from the queue
      setPopups(prevPopups => prevPopups.slice(1));
    }
  }, [activePopup, popups]);

  // Function to add a new popup to the queue
  const addPopup = useCallback((options) => {
    const id = Date.now();
    const popupData = { id, ...options };

    // If no active popup, set this one as active immediately
    if (!activePopup) {
      setActivePopup(popupData);
    } else {
      // Otherwise add to queue
      setPopups(prev => [...prev, popupData]);
    }

    return id;
  }, [activePopup]);

  // Function to close the active popup
  const closeActivePopup = useCallback(() => {
    setActivePopup(null);
  }, []);

  // Create global event listeners for adding popups
  useEffect(() => {
    // Add popup event
    const handleAddPopup = (event) => {
      addPopup(event.detail);
    };

    // Listen for custom events to add popups
    window.addEventListener('addPopup', handleAddPopup);

    return () => {
      window.removeEventListener('addPopup', handleAddPopup);
    };
  }, [addPopup]);

  // Helper function to dispatch popups from anywhere
  useEffect(() => {
    // Make the function globally available
    window.showPopup = (options) => {
      const event = new CustomEvent('addPopup', { detail: options });
      window.dispatchEvent(event);
    };

    return () => {
      delete window.showPopup;
    };
  }, []);

  return (
    <>
      {activePopup && (
        <Popup
          title={activePopup.title}
          content={activePopup.content}
          type={activePopup.type || 'info'}
          showClose={activePopup.showClose !== false}
          showCancel={activePopup.showCancel || false}
          confirmText={activePopup.confirmText || 'OK'}
          cancelText={activePopup.cancelText || 'Cancel'}
          onConfirm={() => {
            if (activePopup.onConfirm) activePopup.onConfirm();
            closeActivePopup();
          }}
          onCancel={() => {
            if (activePopup.onCancel) activePopup.onCancel();
            closeActivePopup();
          }}
          onClose={closeActivePopup}
          autoClose={activePopup.autoClose || false}
          autoCloseTime={activePopup.autoCloseTime || 5000}
        />
      )}
    </>
  );
};

export default PopupManager;