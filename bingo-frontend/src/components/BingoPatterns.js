// ============================
// Bingo Patterns Component - Enhanced with Visualizations
// ============================

import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './BingoPatterns.css';

const BingoPatterns = () => {
  const navigate = useNavigate();
  const [activePattern, setActivePattern] = useState(null);

  // Pattern definitions with visual representations
  const patterns = [
    {
      id: 'horizontal',
      name: 'Horizontal Line (H)',
      description: 'Complete any horizontal line of tasks from left to right.',
      points: 50,
      type: 'H',
      cells: [
        [true, true, true],
        [false, false, false],
        [false, false, false]
      ]
    },
    {
      id: 'vertical',
      name: 'Vertical Line (V)',
      description: 'Complete any vertical line of tasks from top to bottom.',
      points: 50,
      type: 'V',
      cells: [
        [true, false, false],
        [true, false, false],
        [true, false, false]
      ]
    },
    {
      id: 'diagonal',
      name: 'Diagonal (X)',
      description: 'Complete either diagonal line across the board.',
      points: 75,
      type: 'X',
      cells: [
        [true, false, true],
        [false, true, false],
        [true, false, true]
      ]
    },
    {
      id: 'outside',
      name: 'Outside Frame (O)',
      description: 'Complete all tasks on the outside edge of the board.',
      points: 100,
      type: 'O',
      cells: [
        [true, true, true],
        [true, false, true],
        [true, true, true]
      ]
    },
    {
      id: 'full',
      name: 'Full Board',
      description: 'Complete all tasks on the board for maximum points!',
      points: 200,
      type: 'F',
      cells: [
        [true, true, true],
        [true, true, true],
        [true, true, true]
      ]
    }
  ];

  // Handle clicking on a pattern to show details
  const handlePatternClick = (pattern) => {
    setActivePattern(activePattern === pattern.id ? null : pattern.id);
  };

  return (
    <div className="patterns-container">
      <h1 className="patterns-header">Bingo Patterns</h1>

      <p className="patterns-intro">
        Complete tasks to form these patterns and earn bonus points! The more challenging the pattern, the more points you'll earn.
      </p>

      <div className="patterns-grid">
        {patterns.map((pattern) => (
          <div
            key={pattern.id}
            className={`pattern-card ${activePattern === pattern.id ? 'active' : ''}`}
            onClick={() => handlePatternClick(pattern)}
          >
            <div className="pattern-header">
              <h3 className="pattern-name">{pattern.name}</h3>
              <span className="pattern-points">+{pattern.points} pts</span>
            </div>

            <div className="pattern-visualization">
              {pattern.cells.map((row, rowIndex) => (
                <div key={rowIndex} className="pattern-row">
                  {row.map((cell, cellIndex) => (
                    <div
                      key={cellIndex}
                      className={`pattern-cell ${cell ? 'highlighted' : ''}`}
                    ></div>
                  ))}
                </div>
              ))}
            </div>

            {activePattern === pattern.id && (
              <div className="pattern-details">
                <p>{pattern.description}</p>
                <div className="pattern-badge">
                  {pattern.type === 'H' && '➖'}
                  {pattern.type === 'V' && '⏐'}
                  {pattern.type === 'X' && '✖️'}
                  {pattern.type === 'O' && '⭕'}
                  {pattern.type === 'F' && '🌍'}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <div className="patterns-back">
        <button className="back-button" onClick={() => navigate('/bingo')}>
          Back to Bingo Board
        </button>
      </div>
    </div>
  );
};

export default BingoPatterns;