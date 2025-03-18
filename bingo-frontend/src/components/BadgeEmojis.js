// ============================
// Badge Emojis Component
// ============================

import React from 'react';
import './BadgeEmojis.css';

// This component renders animated badge emoji for various achievements
const BadgeEmojis = ({ type, size = 'medium', animate = true, className = '' }) => {
  // Map badge types to emojis and colors
  const getBadgeStyles = () => {
    const styles = {
      // Pattern badges
      'H': {
        emoji: '➖',
        label: 'Horizontal Hero',
        color: '#4CAF50',
        description: 'Complete all tasks in a horizontal row'
      },
      'V': {
        emoji: '⏐',
        label: 'Vertical Victory',
        color: '#2196F3',
        description: 'Complete all tasks in a vertical column'
      },
      'X': {
        emoji: '✖️',
        label: 'Diagonal Master',
        color: '#9C27B0',
        description: 'Complete tasks diagonally across the board'
      },
      'O': {
        emoji: '⭕',
        label: 'Outer Circle Champion',
        color: '#FF9800',
        description: 'Complete all tasks on the outer edge'
      },

      // Rank badges
      'beginner': {
        emoji: '🌱',
        label: 'Beginner',
        color: '#4CAF50',
        description: 'Just getting started on your sustainability journey'
      },
      'intermediate': {
        emoji: '🌿',
        label: 'Intermediate',
        color: '#00BCD4',
        description: 'Making good progress on your sustainability goals'
      },
      'expert': {
        emoji: '🌳',
        label: 'Expert',
        color: '#673AB7',
        description: 'A sustainability champion who leads by example'
      },

      // Task milestone badges
      'first_task': {
        emoji: '🌱',
        label: 'First Steps',
        color: '#4CAF50',
        description: 'Complete your first sustainability task'
      },
      'five_tasks': {
        emoji: '🍃',
        label: 'Growing Impact',
        color: '#8BC34A',
        description: 'Complete five sustainability tasks'
      },
      'all_tasks': {
        emoji: '🌍',
        label: 'Sustainability Champion',
        color: '#009688',
        description: 'Complete all sustainability tasks'
      },

      // Default badge
      'default': {
        emoji: '🏆',
        label: 'Achievement',
        color: '#8E44AD',
        description: 'A sustainability achievement'
      }
    };

    return styles[type] || styles['default'];
  };

  const badgeStyle = getBadgeStyles();

  // Determine size class
  const sizeClass = `badge-size-${size}`;

  // Determine animation class
  const animationClass = animate ? 'badge-animated' : '';

  return (
    <div
      className={`badge-emoji-container ${sizeClass} ${animationClass} ${className}`}
      style={{ '--badge-color': badgeStyle.color }}
      title={badgeStyle.label}
    >
      <div className="badge-emoji-icon">{badgeStyle.emoji}</div>
      {size === 'large' && (
        <div className="badge-emoji-details">
          <div className="badge-emoji-label">{badgeStyle.label}</div>
          <div className="badge-emoji-description">{badgeStyle.description}</div>
        </div>
      )}
    </div>
  );
};

export default BadgeEmojis;