// ============================
// Final Bingo Board Component
// ============================

import React, { useEffect, useState, useCallback, useRef } from 'react';
import axios from 'axios';
import './bingoboard.css';
import { useNavigate } from 'react-router-dom';
import NotificationManager from './NotificationManager';
import PopupManager from './PopupManager';
import AchievementPopup from './AchievementPopup';
import PatternVisualizer from './PatternVisualizer';
import EndOfMonthReminder from './EndOfMonthReminder';

// Define the API URL (fallback to localhost if not set in environment variables)
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// For storing already shown pattern notifications across sessions/renders
// We can use localStorage to make sure these persist even if the component remounts
const getShownPatternNotifications = () => {
  try {
    const stored = localStorage.getItem('shown_pattern_notifications');
    return stored ? JSON.parse(stored) : [];
  } catch (e) {
    console.error("Error reading pattern notifications from storage:", e);
    return [];
  }
};

const saveShownPatternNotification = (patternType) => {
  try {
    const current = getShownPatternNotifications();
    if (!current.includes(patternType)) {
      current.push(patternType);
      localStorage.setItem('shown_pattern_notifications', JSON.stringify(current));
    }
  } catch (e) {
    console.error("Error saving pattern notification to storage:", e);
  }
};

const BingoBoard = () => {
  // State variables for managing tasks, loading status, and error messages
  const [tasks, setTasks] = useState([]);
  const [userTasks, setUserTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // State variables for rejection feedback
  const [showRejectionFeedback, setShowRejectionFeedback] = useState(false);
  const [rejectionFeedback, setRejectionFeedback] = useState("");
  const [selectedRejectedTaskId, setSelectedRejectedTaskId] = useState(null);

  // State for achievement popup
  const [showAchievementPopup, setShowAchievementPopup] = useState(false);
  const [achievementDetails, setAchievementDetails] = useState({
    title: '',
    achievement: '',
    points: 0,
    badgeEmoji: '🏆'
  });

  // State for pattern visualizer
  const [showPatternVisualizer, setShowPatternVisualizer] = useState(false);
  const [highlightPattern, setHighlightPattern] = useState(null);

  // State for tracking task animations
  const [animatedTaskId, setAnimatedTaskId] = useState(null);

  // State for tracking patterns
  const [completedPatterns, setCompletedPatterns] = useState([]);

  // New state to track which pattern popups have been displayed
  const [displayedPatternPopups, setDisplayedPatternPopups] = useState([]);

  // State for end-of-month reminder
  const [showEndOfMonthReminder, setShowEndOfMonthReminder] = useState(false);

  // Ref to track if notifications have been shown
  const hasShownWelcomeNotification = useRef(false);
  const hasShownProgressNotification = useRef(false);
  const hasShownEndOfMonthReminder = useRef(false);

  const navigate = useNavigate(); // Hook for programmatic navigation

  // Initialize displayedPatternPopups from localStorage on component mount
  useEffect(() => {
    setDisplayedPatternPopups(getShownPatternNotifications());
  }, []);

  // ============================
  // Check End of Month Status
  // ============================

  const checkEndOfMonth = useCallback(() => {
    const now = new Date();
    const lastDay = new Date(now.getFullYear(), now.getMonth() + 1, 0).getDate();
    const daysLeft = lastDay - now.getDate();

    // Show reminder when 3 days or fewer left in month
    if (daysLeft <= 3 && daysLeft > 0 && !showEndOfMonthReminder && !hasShownEndOfMonthReminder.current) {
      setShowEndOfMonthReminder(true);
      hasShownEndOfMonthReminder.current = true;

      // Wait a bit before showing end-of-month notification
      setTimeout(() => {
        if (window.showNotification) {
          window.showNotification(
            'end-of-month',
            `Only ${daysLeft} day${daysLeft > 1 ? 's' : ''} left this month! Complete your bingo patterns for extra points.`,
            8000,
            { label: 'View Patterns', onClick: () => setShowPatternVisualizer(true) }
          );
        }
      }, 5000);
    }
  }, [showEndOfMonthReminder, setShowPatternVisualizer]);

  // ============================
  // Show Progress Notification
  // ============================

  const showProgressNotification = useCallback((userTasksData) => {
    // Only show progress if tasks are loaded and notification hasn't been shown yet
    if (!tasks || tasks.length === 0 || hasShownProgressNotification.current) return;

    // Mark notification as shown
    hasShownProgressNotification.current = true;

    const completedTasks = userTasksData.filter(task => task.completed).length;
    const pendingTasks = userTasksData.filter(task => task.status === 'pending').length;

    // Make sure we have total tasks before calculating percentage
    const totalTasks = tasks.length;

    if (totalTasks > 0 && window.showProgressUpdate) {
      window.showProgressUpdate(completedTasks, totalTasks);
    } else if (window.showNotification) {
      // Fallback with safe percentage calculation
      const safePercentage = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0;

      window.showNotification(
        'progress',
        `Your progress: ${completedTasks}/${totalTasks} tasks${totalTasks > 0 ? ` (${safePercentage}%)` : ''}`,
        6000,
        { label: 'View Progress', onClick: () => setShowPatternVisualizer(true) }
      );
    }
  }, [tasks, setShowPatternVisualizer]);

  // ============================
  // Fetch Tasks and User Tasks on Component Mount
  // ============================

  useEffect(() => {
    // Get auth token
    const token = localStorage.getItem('accessToken');

    if (!token) {
      navigate('/login');
      return;
    }

    // Set up headers
    const headers = {
      Authorization: `Bearer ${token}`
    };

    // Fetch all tasks
    axios.get(`${API_URL}/api/tasks/`)
      .then(response => {
        console.log('Tasks fetched:', response.data);
        setTasks(response.data);

        // After tasks are fetched, get user's task status
        return axios.get(`${API_URL}/api/check-auth/`, { headers });
      })
      .then(authResponse => {
        // Confirm we're authenticated
        console.log('Auth check:', authResponse.data);

        // Get all user tasks to check status (pending or completed)
        return axios.get(`${API_URL}/api/profile/`, { headers });
      })
      .then(profileResponse => {
        // Extract user tasks from profile if available
        if (profileResponse.data && profileResponse.data.user_tasks) {
          console.log('User tasks fetched:', profileResponse.data.user_tasks);
          setUserTasks(profileResponse.data.user_tasks);

          // Check for completed patterns after setting user tasks
          setTimeout(() => {
            checkForCompletedPatterns(profileResponse.data.user_tasks);
          }, 500);
        }
        setLoading(false);

        // Show welcome notification (only once)
        if (window.showNotification && !hasShownWelcomeNotification.current) {
          hasShownWelcomeNotification.current = true;
          window.showNotification('info', 'Welcome to Sustainability Bingo! Complete tasks to earn points and unlock achievements.');
        }

        // Schedule a reminder to show progress after 3 seconds
        // This delay helps ensure all data is loaded and prevents division by zero
        if (!hasShownProgressNotification.current) {
          setTimeout(() => {
            if (profileResponse.data && profileResponse.data.user_tasks && tasks.length > 0) {
              showProgressNotification(profileResponse.data.user_tasks);
            }
          }, 3000);
        }

        // Check if we need to show end-of-month reminder
        checkEndOfMonth();
      })
      .catch(error => {
        console.error("Error fetching data:", error);
        setError("Failed to load tasks. Please try again or log in.");
        setLoading(false);

        // Show error notification
        if (window.showNotification) {
          window.showNotification('error', 'Failed to load tasks. Please try again or log in.');
        }
      });

    // Clean up function to reset notification flags on unmount
    return () => {
      hasShownWelcomeNotification.current = false;
      hasShownProgressNotification.current = false;
      hasShownEndOfMonthReminder.current = false;
    };
  }, [navigate, checkEndOfMonth, showProgressNotification]);

  // ============================
  // Check for Completed Patterns - FIXED with persistent storage
  // ============================

  const checkForCompletedPatterns = useCallback((userTasksData) => {
    // Skip if no tasks or data loaded yet
    if (!tasks || tasks.length === 0 || !userTasksData || userTasksData.length === 0) return;

    // Get completed task IDs
    const completedTaskIds = userTasksData
      .filter(task => task.completed)
      .map(task => task.task_id);

    // Define patterns to check (these indices match the 3x3 grid layout)
    const patterns = [
      // Horizontal rows
      { type: 'H', name: 'Horizontal Bingo', cells: [0, 1, 2], points: 50 },
      { type: 'H', name: 'Horizontal Bingo', cells: [3, 4, 5], points: 50 },
      { type: 'H', name: 'Horizontal Bingo', cells: [6, 7, 8], points: 50 },
      // Vertical columns
      { type: 'V', name: 'Vertical Bingo', cells: [0, 3, 6], points: 50 },
      { type: 'V', name: 'Vertical Bingo', cells: [1, 4, 7], points: 50 },
      { type: 'V', name: 'Vertical Bingo', cells: [2, 5, 8], points: 50 },
      // Diagonals
      { type: 'X', name: 'Diagonal Bingo', cells: [0, 4, 8], points: 75 },
      { type: 'X', name: 'Diagonal Bingo', cells: [2, 4, 6], points: 75 },
      // Outside frame (O)
      { type: 'O', name: 'Outside Frame', cells: [0, 1, 2, 3, 5, 6, 7, 8], points: 100 }
    ];

    // Map task IDs to their indices in the grid (0-8)
    const taskIndices = {};
    tasks.forEach((task, index) => {
      taskIndices[task.id] = index;
    });

    // Keep track of newly detected patterns
    const newlyDetectedPatterns = [];

    // Check each pattern for completion
    patterns.forEach(pattern => {
      // Check if all cells in pattern are completed
      const isComplete = pattern.cells.every(cellIndex => {
        if (cellIndex >= tasks.length) return false;
        const taskId = tasks[cellIndex]?.id;
        return taskId && completedTaskIds.includes(taskId);
      });

      // If pattern is complete and not already tracked
      if (isComplete && !completedPatterns.includes(pattern.type)) {
        // Add to newly detected patterns
        newlyDetectedPatterns.push(pattern.type);

        // Only if we haven't shown a popup for this pattern yet in this session
        if (!displayedPatternPopups.includes(pattern.type)) {
          // Schedule popup after a short delay
          setTimeout(() => {
            setAchievementDetails({
              title: 'Pattern Complete!',
              achievement: pattern.name,
              points: pattern.points,
              badgeEmoji: pattern.type === 'H' ? '➖' :
                          pattern.type === 'V' ? '⏐' :
                          pattern.type === 'X' ? '✖️' :
                          pattern.type === 'O' ? '⭕' : '🏆'
            });
            setShowAchievementPopup(true);

            // Highlight the pattern in visualizer
            setHighlightPattern(pattern.type);

            // Mark this pattern as having shown a popup (in state and localStorage)
            setDisplayedPatternPopups(prev => {
              const updated = [...prev, pattern.type];
              saveShownPatternNotification(pattern.type);
              return updated;
            });
          }, 1000);
        }

        // Send pattern completion event only if we haven't shown a notification for this pattern
        if (window.showPatternCompletion && !displayedPatternPopups.includes(pattern.type)) {
          window.showPatternCompletion(pattern.type, pattern.points);
        }
      }
    });

    // Update completed patterns state if we found new ones
    if (newlyDetectedPatterns.length > 0) {
      setCompletedPatterns(prev => [...prev, ...newlyDetectedPatterns]);
      return [newlyDetectedPatterns, true];
    }

    return [[], false];
  }, [tasks, completedPatterns, displayedPatternPopups]);

  // ============================
  // Get Task Status Helper
  // ============================

  const getTaskStatus = useCallback((taskId) => {
    // Find the user task with matching task ID
    const userTask = userTasks.find(ut => ut.task_id === taskId);

    if (!userTask) return 'not_started';
    if (userTask.completed) return 'completed';
    if (userTask.status === 'pending') return 'pending';
    if (userTask.status === 'rejected') return 'rejected';

    return 'not_started';
  }, [userTasks]);

  // ============================
  // Get Task Rejection Reason
  // ============================

  const getTaskRejectionReason = useCallback((taskId) => {
    // Find the user task with matching task ID
    const userTask = userTasks.find(ut => ut.task_id === taskId);

    if (!userTask || userTask.status !== 'rejected') return null;
    return userTask.rejection_reason || "Task was rejected by game keeper";
  }, [userTasks]);

  // ============================
  // Handle Task Click (Enhanced for Rejection Feedback)
  // ============================

  const handleTaskClick = async (task) => {
    if (!task) return;

    // Animate task card
    setAnimatedTaskId(task.id);
    // Clear animation after 1 second
    setTimeout(() => setAnimatedTaskId(null), 1000);

    // Check if task is already completed or pending
    const status = getTaskStatus(task.id);

    // If task is rejected, show the rejection feedback
    if (status === 'rejected') {
      const reason = getTaskRejectionReason(task.id);
      setRejectionFeedback(reason);
      setSelectedRejectedTaskId(task.id);
      setShowRejectionFeedback(true);
      return; // Don't proceed with task submission
    }

    if (status === 'completed' || status === 'pending') {
      console.log(`Task ${task.id} is already ${status}`);

      // Show notification based on task status
      if (window.showNotification) {
        if (status === 'completed') {
          window.showNotification('info', 'You\'ve already completed this task!');
        } else {
          window.showNotification('info', 'This task is awaiting approval from a GameKeeper.');
        }
      }
      return; // Don't allow re-submission
    }

    // If task requires an upload, navigate to the upload page
    if (task.requires_upload) {
      localStorage.setItem("selectedChoice", task.description);
      localStorage.setItem("selectedTaskId", task.id.toString());
      navigate("/upload");
    }
    // If task requires a scan, navigate to the scan page
    else if (task.requires_scan) {
      localStorage.setItem("selectedChoice", task.description);
      localStorage.setItem("selectedTaskId", task.id.toString());
      navigate("/scan");
    }
    // Otherwise, mark the task as completed via API
    else {
      try {
        // Show popup for confirmation
        if (window.showPopup) {
          window.showPopup({
            title: 'Complete Task',
            content: `Are you sure you want to complete the task: "${task.description}"?`,
            type: 'info',
            showCancel: true,
            confirmText: 'Complete Task',
            cancelText: 'Cancel',
            onConfirm: async () => {
              try {
                const token = localStorage.getItem('accessToken');
                const response = await axios.post(
                  `${API_URL}/api/complete_task/`,
                  { task_id: task.id },
                  { headers: { Authorization: `Bearer ${token}` } }
                );

                if (response.status === 200) {
                  // Update user tasks with new pending task
                  const newUserTasks = [
                    ...userTasks,
                    {
                      task_id: task.id,
                      status: 'pending',
                      completed: false
                    }
                  ];

                  setUserTasks(newUserTasks);

                  // Show task completion notification
                  if (window.showTaskCompletion) {
                    window.showTaskCompletion(task.description, task.points);
                  } else if (window.showNotification) {
                    window.showNotification(
                      'task-complete',
                      `Task submitted successfully! Awaiting GameKeeper approval. (${task.points} points)`,
                      5000,
                      { label: 'View Progress', onClick: () => setShowPatternVisualizer(true) }
                    );
                  }

                  // Check for achievements
                  checkForAchievements(newUserTasks);
                }
              } catch (error) {
                console.error("Error completing task:", error);

                // Show error notification
                if (window.showNotification) {
                  window.showNotification('error', 'Failed to complete task. Please try again.');
                }
              }
            }
          });
        } else {
          // Fallback if popup manager isn't available
          const token = localStorage.getItem('accessToken');
          const response = await axios.post(
            `${API_URL}/api/complete_task/`,
            { task_id: task.id },
            { headers: { Authorization: `Bearer ${token}` } }
          );

          if (response.status === 200) {
            // Update user tasks with new pending task
            setUserTasks(prevUserTasks => [
              ...prevUserTasks,
              {
                task_id: task.id,
                status: 'pending',
                completed: false
              }
            ]);
          }
        }
      } catch (error) {
        console.error("Error completing task:", error);

        // Show error notification
        if (window.showNotification) {
          window.showNotification('error', 'Failed to complete task. Please try again.');
        }
      }
    }
  };

  // ============================
  // Close Rejection Feedback Modal
  // ============================

  const closeRejectionFeedback = () => {
    setShowRejectionFeedback(false);
    setRejectionFeedback("");
    setSelectedRejectedTaskId(null);
  };

  // ============================
  // Handle Task Retry after Rejection
  // ============================

  const handleRetryTask = () => {
    if (!selectedRejectedTaskId) return;

    // Find the task
    const task = tasks.find(t => t.id === selectedRejectedTaskId);

    if (!task) return;

    // Close the rejection feedback modal
    closeRejectionFeedback();

    // Set flag to indicate we're resubmitting a rejected task
    localStorage.setItem("isResubmission", "true");

    // Show notification
    if (window.showNotification) {
      window.showNotification('info', 'Let\'s try this task again!', 3000);
    }

    // Redirect to upload or scan page if needed
    if (task.requires_upload) {
      localStorage.setItem("selectedChoice", task.description);
      localStorage.setItem("selectedTaskId", task.id.toString());
      navigate("/upload");
    }
    else if (task.requires_scan) {
      localStorage.setItem("selectedChoice", task.description);
      localStorage.setItem("selectedTaskId", task.id.toString());
      navigate("/scan");
    } else {
      // For tasks that don't require upload/scan, directly resubmit
      handleDirectResubmission(task.id);
    }
  };

  // Handle direct resubmission for simple tasks
  const handleDirectResubmission = async (taskId) => {
    try {
      const token = localStorage.getItem('accessToken');

      if (!token) {
        setError("You must be logged in to submit tasks");
        return;
      }

      // Submit the task with resubmission flag
      const response = await axios.post(
        `${API_URL}/api/complete_task/`,
        {
          task_id: taskId,
          is_resubmission: true
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.status === 200) {
        // Update the task status in the local state to "pending"
        setUserTasks(prevUserTasks => {
          const updatedTasks = prevUserTasks.map(task => {
            if (task.task_id === taskId) {
              return {
                ...task,
                status: 'pending',
                rejection_reason: null
              };
            }
            return task;
          });
          return updatedTasks;
        });

        // Show success notification with animation
        setAnimatedTaskId(taskId);
        setTimeout(() => setAnimatedTaskId(null), 1000);

        if (window.showNotification) {
          window.showNotification('task-complete', 'Task resubmitted successfully! Awaiting approval.');
        }

        // Fetch fresh data from the server to ensure everything is in sync
        const token = localStorage.getItem('accessToken');
        const headers = { Authorization: `Bearer ${token}` };
        const profileResponse = await axios.get(`${API_URL}/api/profile/`, { headers });

        if (profileResponse.data && profileResponse.data.user_tasks) {
          setUserTasks(profileResponse.data.user_tasks);
        }
      }
    } catch (error) {
      console.error("Error resubmitting task:", error);
      setError("Failed to resubmit task. Please try again.");

      // Show error notification
      if (window.showNotification) {
        window.showNotification('error', 'Failed to resubmit task. Please try again.');
      }
    }
  };

  // ============================
  // Check for Achievements (Enhanced)
  // ============================

  const checkForAchievements = (currentUserTasks) => {
    // Count completed and pending tasks
    const completedTasks = currentUserTasks.filter(task => task.completed).length;
    const pendingTasks = currentUserTasks.filter(task => task.status === 'pending').length;
    const totalTasks = completedTasks + pendingTasks;

    // Different achievements based on progress
    if (totalTasks === 1) {
      // First task achievement
      setTimeout(() => {
        setAchievementDetails({
          title: 'First Steps!',
          achievement: 'Complete your first sustainability task',
          points: 5,
          badgeEmoji: '🌱'
        });
        setShowAchievementPopup(true);
      }, 1000);
    }
    else if (totalTasks === 3) {
      // Three tasks achievement
      setTimeout(() => {
        setAchievementDetails({
          title: 'Getting Started!',
          achievement: 'Complete three sustainability tasks',
          points: 15,
          badgeEmoji: '🍃'
        });
        setShowAchievementPopup(true);
      }, 1000);
    }
    else if (totalTasks === 5) {
      // Halfway achievement
      setTimeout(() => {
        setAchievementDetails({
          title: 'Halfway There!',
          achievement: 'Complete 5 sustainability tasks',
          points: 20,
          badgeEmoji: '🌿'
        });
        setShowAchievementPopup(true);

        // Also show pattern visualizer to encourage pattern completion
        setTimeout(() => {
          setShowPatternVisualizer(true);
        }, 2000);
      }, 1000);
    }
    else if (tasks.length > 0 && totalTasks === tasks.length) {
      // All tasks complete achievement
      setTimeout(() => {
        setAchievementDetails({
          title: 'Sustainability Champion!',
          achievement: 'Complete all tasks on the board',
          points: 100,
          badgeEmoji: '🌍'
        });
        setShowAchievementPopup(true);
      }, 1000);
    }

    // Check for patterns when the user has enough tasks completed or pending
    if (totalTasks >= 3) {
      checkForCompletedPatterns(currentUserTasks);
    }
  };

  // ============================
  // Get CSS Class Based on Task Status
  // ============================

  const getTaskStatusClass = (taskId) => {
    let classes = [];

    // Basic status class
    const status = getTaskStatus(taskId);
    if (status !== 'not_started') {
      classes.push(status);
    }

    // Animation class for the clicked task
    if (animatedTaskId === taskId) {
      classes.push('animated');
    }

    return classes.join(' ');
  };

  // ============================
  // Render Bingo Board UI
  // ============================

  return (
    <div className="bingo-container">
      {/* Bingo Header */}
      <h1 className="bingo-header">Sustainability Bingo</h1>

      {/* Display loading message or error message if applicable */}
      {loading ? (
        <div className="loading-container">
          <div className="loading-spinner"></div>
          <p>Loading your sustainability tasks...</p>
        </div>
      ) : error ? (
        <p className="error-message">{error}</p>
      ) : (
        <div className="bingo-board">
          {/* Render tasks dynamically if available */}
          {tasks.length > 0 ? tasks.map((task) => (
            <div
              key={task.id}
              className={`bingo-cell ${getTaskStatusClass(task.id)}`}
              onClick={() => handleTaskClick(task)}
            >
              <div className='cell-content'>
                {/* Task Points */}
                <div className='points'><strong>{task.points} Points</strong></div>
                {/* Task Description */}
                <div className='description'>{task.description}</div>
                {/* Icons for upload or scan-required tasks */}
                {task.requires_upload && <div className='upload-indicator'>📷</div>}
                {task.requires_scan && <div className='scan-indicator'>🤳🏻</div>}
                {/* Status indicator */}
                {getTaskStatus(task.id) === 'pending' &&
                  <div className='status-indicator'>Awaiting approval</div>}
                {getTaskStatus(task.id) === 'rejected' &&
                  <div className='status-indicator rejected'>Rejected</div>}
                {getTaskStatus(task.id) === 'completed' &&
                  <div className='status-indicator completed'>Completed!</div>}
              </div>
            </div>
          )) : <p>No tasks available.</p>}
        </div>
      )}

      {/* Legend for task statuses */}
      <div className="status-legend">
        <div className="legend-item">
          <span className="legend-color not-started"></span>
          <span>Not Started</span>
        </div>
        <div className="legend-item">
          <span className="legend-color pending"></span>
          <span>Pending Approval</span>
        </div>
        <div className="legend-item">
          <span className="legend-color completed"></span>
          <span>Completed</span>
        </div>
        <div className="legend-item">
          <span className="legend-color rejected"></span>
          <span>Rejected</span>
        </div>
      </div>

      {/* Navigation and Action Bar */}
      <div className="action-bar">
        <button onClick={() => navigate('/userprofile')} className="nav-button">
          View Profile
        </button>
        <button onClick={() => setShowPatternVisualizer(true)} className="pattern-button">
          View Patterns
        </button>
      </div>

      {/* Rejection Feedback Modal */}
      {showRejectionFeedback && (
        <div className="rejection-feedback-overlay" onClick={closeRejectionFeedback}>
          <div className="rejection-feedback-content" onClick={e => e.stopPropagation()}>
            <span className="close-button" onClick={closeRejectionFeedback}>&times;</span>
            <h3>Task Rejected</h3>
            <p>Your submission was rejected by the game keeper for the following reason:</p>
            <div className="rejection-reason">
              {rejectionFeedback || "No reason provided"}
            </div>

            <div className="rejection-actions">
              <button className="retry-button" onClick={handleRetryTask}>
                Try Again
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Achievement Popup - FIXED */}
      {showAchievementPopup && (
        <AchievementPopup
          title={achievementDetails.title}
          achievement={achievementDetails.achievement}
          points={achievementDetails.points}
          badgeEmoji={achievementDetails.badgeEmoji}
          onClose={() => {
            setShowAchievementPopup(false);
            // Don't reset displayedPatternPopups - we want to remember which ones we've shown
          }}
        />
      )}

      {/* Pattern Visualizer */}
      <PatternVisualizer
        userTasks={userTasks}
        tasks={tasks}
        visible={showPatternVisualizer}
        onClose={() => {
          setShowPatternVisualizer(false);
          setHighlightPattern(null);
        }}
        highlightPattern={highlightPattern}
      />

      {/* End of Month Reminder */}
      {showEndOfMonthReminder && (
        <EndOfMonthReminder
          onClose={() => setShowEndOfMonthReminder(false)}
          onViewPatterns={() => setShowPatternVisualizer(true)}
        />
      )}

      {/* Notification and Popup Managers */}
      <NotificationManager />
      <PopupManager />
    </div>
  );
};

export default BingoBoard;