// Pattern Visualizer Component

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
      id: 'x-pattern',
      name: 'X Pattern',
      type: 'X',
      cells: [0, 2, 4, 6, 8],
      points: 35,
      icon: '✖️'
    },
    {
      id: 'o-pattern',
      name: 'O Pattern',
      type: 'O',
      cells: [0, 1, 2, 3, 5, 6, 7, 8],
      points: 35,
      icon: '⭕'
    },
    {
      id: 'horiz1',
      name: 'Horizontal Line (Top)',
      type: 'HORIZ',
      cells: [0, 1, 2],
      points: 5,
      icon: '➖'
    },
    {
      id: 'horiz2',
      name: 'Horizontal Line (Middle)',
      type: 'HORIZ',
      cells: [3, 4, 5],
      points: 5,
      icon: '➖'
    },
    {
      id: 'horiz3',
      name: 'Horizontal Line (Bottom)',
      type: 'HORIZ',
      cells: [6, 7, 8],
      points: 5,
      icon: '➖'
    },
    {
      id: 'vert1',
      name: 'Vertical Line (Left)',
      type: 'VERT',
      cells: [0, 3, 6],
      points: 5,
      icon: '⏐'
    },
    {
      id: 'vert2',
      name: 'Vertical Line (Middle)',
      type: 'VERT',
      cells: [1, 4, 7],
      points: 5,
      icon: '⏐'
    },
    {
      id: 'vert3',
      name: 'Vertical Line (Right)',
      type: 'VERT',
      cells: [2, 5, 8],
      points: 5,
      icon: '⏐'
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
  }, [userTasks, tasks, highlightPattern, patterns]);

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
              {patternProgress
                .sort((a, b) => b.points - a.points) 
                .map(pattern => (
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