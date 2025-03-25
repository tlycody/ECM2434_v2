// Popup Component

import React, { useEffect, useState, useCallback } from 'react';
import './Popup.css';

const Popup = ({
  title,
  content,
  type = 'info',
  showClose = true,
  showCancel = false,
  confirmText = 'Confirm',
  cancelText = 'Cancel',
  onConfirm,
  onCancel,
  onClose,
  autoClose = false,
  autoCloseTime = 5000
}) => {
  const [isVisible, setIsVisible] = useState(false);

  // Handle close animation
  const handleClose = useCallback(() => {
    setIsVisible(false);
    setTimeout(() => {
      if (onClose) onClose();
    }, 300); 
  }, [onClose]);

  // Animation timing
  useEffect(() => {
    setIsVisible(true);

    // Set up auto-close if enabled
    if (autoClose && autoCloseTime > 0) {
      const timer = setTimeout(() => {
        handleClose();
      }, autoCloseTime);

      return () => clearTimeout(timer);
    }
  }, [autoClose, autoCloseTime, handleClose]);

  // Handle confirm action
  const handleConfirm = () => {
    if (onConfirm) onConfirm();
    handleClose();
  };

  // Handle cancel action
  const handleCancel = () => {
    if (onCancel) onCancel();
    handleClose();
  };

  // Stop propagation to prevent closing when clicking the popup content
  const handleContentClick = (e) => {
    e.stopPropagation();
  };

  return (
    <div className={`popup-overlay ${isVisible ? 'visible' : 'hidden'}`} onClick={handleClose}>
      <div className={`popup-content ${type} ${isVisible ? 'visible' : 'hidden'}`} onClick={handleContentClick}>
        {/* Popup Header */}
        <div className="popup-header">
          <div className="popup-title">{title}</div>
          {showClose && (
            <button className="popup-close" onClick={handleClose}>&times;</button>
          )}
        </div>

        {/* Popup Body */}
        <div className="popup-body">
          {/* Support both string content and React elements */}
          {typeof content === 'string' ? <p>{content}</p> : content}
        </div>

        {/* Popup Footer with Action Buttons */}
        <div className="popup-footer">
          {showCancel && (
            <button className="popup-button cancel" onClick={handleCancel}>
              {cancelText}
            </button>
          )}
          <button className="popup-button confirm" onClick={handleConfirm}>
            {confirmText}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Popup;