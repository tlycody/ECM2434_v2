// ============================
// Pattern Visualizer Component
// ============================

import React, { useState, useEffect } from 'react';
import './PatternVisualizer.css';

const PatternVisualizer = ({
  userTasks,
  tasks,
  visible = false,
  onClose,
  highlightPattern = null
}) => {
  const [patternProgress, setPatternProgress] = useState([]);
  const [activePattern, setActivePattern] = useState(null);
  const [animation, setAnimation] = useState(false);

  // Define all possible bingo patterns
  const patterns = [
    {
      id: 'h1',
      name: 'Horizontal Line (Top)',
      type: 'H',
      cells: [0, 1, 2],
      points: 50,
      icon: '➖'
    },
    {
      id: 'h2',
      name: 'Horizontal Line (Middle)',
      type: 'H',
      cells: [3, 4, 5],
      points: 50,
      icon: '➖'
    },
    {
      id: 'h3',
      name: 'Horizontal Line (Bottom)',
      type: 'H',
      cells: [6, 7, 8],
      points: 50,
      icon: '➖'
    },
    {
      id: 'v1',
      name: 'Vertical Line (Left)',
      type: 'V',
      cells: [0, 3, 6],
      points: 50,
      icon: '⏐'
    },
    {
      id: 'v2',
      name: 'Vertical Line (Middle)',
      type: 'V',
      cells: [1, 4, 7],
      points: 50,
      icon: '⏐'
    },
    {
      id: 'v3',
      name: 'Vertical Line (Right)',
      type: 'V',
      cells: [2, 5, 8],
      points: 50,
      icon: '⏐'
    },
    {
      id: 'd1',
      name: 'Diagonal (Top-Left to Bottom-Right)',
      type: 'X',
      cells: [0, 4, 8],
      points: 75,
      icon: '✖️'
    },
    {
      id: 'd2',
      name: 'Diagonal (Top-Right to Bottom-Left)',
      type: 'X',
      cells: [2, 4, 6],
      points: 75,
      icon: '✖️'
    },
    {
      id: 'outer',
      name: 'Outer Frame',
      type: 'O',
      cells: [0, 1, 2, 3, 5, 6, 7, 8],
      points: 100,
      icon: '⭕'
    },
    {
      id: 'full',
      name: 'Full Board',
      type: 'F',
      cells: [0, 1, 2, 3, 4, 5, 6, 7, 8],
      points: 200,
      icon: '🌍'
    }
  ];

  // Calculate pattern progress when user tasks change
  useEffect(() => {
    if (!userTasks || !tasks || tasks.length === 0) return;

    // Get completed task IDs
    const completedTaskIds = userTasks
      .filter(task => task.completed)
      .map(task => task.task_id);

    // Map task IDs to their indices in the grid (0-8)
    const taskIndices = {};
    tasks.forEach((task, index) => {
      taskIndices[task.id] = index;
    });

    // Calculate completion percentage for each pattern
    const progressData = patterns.map(pattern => {
      // Count completed cells in this pattern
      const completedCells = pattern.cells.filter(cellIndex => {
        const taskId = tasks[cellIndex]?.id;
        return taskId && completedTaskIds.includes(taskId);
      });

      // Calculate percentage
      const percentage = Math.round((completedCells.length / pattern.cells.length) * 100);

      // Determine if pattern is complete
      const isComplete = percentage === 100;

      return {
        ...pattern,
        completedCells: completedCells.length,
        totalCells: pattern.cells.length,
        percentage,
        isComplete
      };
    });

    setPatternProgress(progressData);

    // If a specific pattern should be highlighted
    if (highlightPattern) {
      const pattern = progressData.find(p => p.type === highlightPattern);
      if (pattern) {
        setActivePattern(pattern.id);
        setAnimation(true);
      }
    }
  }, [userTasks, tasks, highlightPattern]);

  // Toggle the active pattern
  const togglePattern = (patternId) => {
    setActivePattern(activePattern === patternId ? null : patternId);
    setAnimation(true);
  };

  // Get cell class based on task status and pattern selection
  const getCellClass = (index) => {
    if (!tasks || tasks.length === 0) return '';

    const taskId = tasks[index]?.id;
    if (!taskId) return '';

    // Check if this task is completed
    const isCompleted = userTasks?.some(ut => ut.task_id === taskId && ut.completed);

    // Check if this cell is part of the active pattern
    const isHighlighted = activePattern &&
      patterns.find(p => p.id === activePattern)?.cells.includes(index);

    let classes = isCompleted ? 'completed' : '';
    if (isHighlighted) classes += ' highlighted';

    return classes;
  };

  if (!visible) return null;

  return (
    <div className="pattern-overlay">
      <div className="pattern-container">
        <div className="pattern-header">
          <h2>Bingo Pattern Progress</h2>
          <button className="pattern-close" onClick={onClose}>&times;</button>
        </div>

        <div className="pattern-content">
          <div className="pattern-grid">
            {[0, 1, 2, 3, 4, 5, 6, 7, 8].map(index => (
              <div
                key={index}
                className={`pattern-cell ${getCellClass(index)}`}
              >
                {tasks[index] && (
                  <div className="cell-content">
                    <div className="cell-indicator">
                      {userTasks?.some(ut => ut.task_id === tasks[index].id && ut.completed) ?
                        '✓' : ''}
                    </div>
                  </div>
                )}
              </div>
            ))}

            {/* Pattern overlay animations */}
            {activePattern && (
              <div className={`pattern-overlay-animation ${animation ? 'animate' : ''}`}>
                {patterns.find(p => p.id === activePattern)?.cells.map(cellIndex => (
                  <div
                    key={`overlay-${cellIndex}`}
                    className={`overlay-cell cell-${cellIndex}`}
                    onAnimationEnd={() => setAnimation(false)}
                  ></div>
                ))}
              </div>
            )}
          </div>

          <div className="pattern-list">
            <h3>Your Progress</h3>
            <div className="pattern-progress-list">
              {patternProgress.map(pattern => (
                <div
                  key={pattern.id}
                  className={`pattern-progress-item ${pattern.isComplete ? 'complete' : ''} ${activePattern === pattern.id ? 'active' : ''}`}
                  onClick={() => togglePattern(pattern.id)}
                >
                  <div className="pattern-icon">{pattern.icon}</div>
                  <div className="pattern-info">
                    <div className="pattern-name">{pattern.name}</div>
                    <div className="pattern-stats">
                      <span>{pattern.completedCells}/{pattern.totalCells} tasks</span>
                      <span className="pattern-points">+{pattern.points} pts</span>
                    </div>
                    <div className="progress-bar">
                      <div
                        className="progress-fill"
                        style={{ width: `${pattern.percentage}%` }}
                      ></div>
                    </div>
                  </div>
                  {pattern.isComplete && (
                    <div className="pattern-complete-badge">
                      Complete!
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PatternVisualizer;