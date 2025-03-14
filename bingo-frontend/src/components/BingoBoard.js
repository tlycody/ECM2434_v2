import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './bingoboard.css';
import { useNavigate } from 'react-router-dom';
import NotificationManager from './NotificationManager';
import PopupManager from './PopupManager';
import AchievementPopup from './AchievementPopup';

// Define the API URL (fallback to localhost if not set in environment variables)
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

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
  // New state for achievement popup
  const [showAchievementPopup, setShowAchievementPopup] = useState(false);
  const [achievementDetails, setAchievementDetails] = useState({
    title: '',
    achievement: '',
    points: 0
  });

  const navigate = useNavigate(); // Hook for programmatic navigation

  // ============================
  // Fetch Tasks and User Tasks from API on Component Mount
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
        }
        setLoading(false);

        // Show welcome notification
        if (window.showNotification) {
          window.showNotification('info', 'Welcome to Sustainability Bingo! Complete tasks to earn points and unlock achievements.');
        }
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
  }, [navigate]);

  // ============================
  // Get Task Status Helper
  // ============================

  const getTaskStatus = (taskId) => {
    // Find the user task with matching task ID
    const userTask = userTasks.find(ut => ut.task_id === taskId);

    if (!userTask) return 'not_started';
    if (userTask.completed) return 'completed';
    if (userTask.status === 'pending') return 'pending';
    if (userTask.status === 'rejected') return 'rejected';

    return 'not_started';
  };

  // ============================
  // Get Task Rejection Reason
  // ============================

  const getTaskRejectionReason = (taskId) => {
    // Find the user task with matching task ID
    const userTask = userTasks.find(ut => ut.task_id === taskId);

    if (!userTask || userTask.status !== 'rejected') return null;
    return userTask.rejection_reason || "Task was rejected by game keeper";
  };

  // ============================
  // Handle Task Click (Enhanced for Rejection Feedback)
  // ============================

  const handleTaskClick = async (task) => {
    if (!task) return;

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
                  setUserTasks(prevUserTasks => [
                    ...prevUserTasks,
                    {
                      task_id: task.id,
                      status: 'pending',
                      completed: false
                    }
                  ]);

                  // Show success notification
                  if (window.showNotification) {
                    window.showNotification('success', 'Task submitted successfully! Awaiting GameKeeper approval.');
                  }

                  // Check for patterns/achievements (mock - in real app, this would come from backend)
                  checkForAchievements();
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
      window.showNotification('info', 'Let\'s try this task again!');
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

        // Show success notification
        if (window.showNotification) {
          window.showNotification('success', 'Task resubmitted successfully! Awaiting approval.');
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
  // Check for Achievements (Mock)
  // ============================

  const checkForAchievements = () => {
    // Count completed and pending tasks
    const completedTasks = userTasks.filter(task => task.completed).length;
    const pendingTasks = userTasks.filter(task => task.status === 'pending').length;
    const totalTasks = completedTasks + pendingTasks + 1; // +1 for the task just submitted

    // Check if the user has completed their first task
    if (totalTasks === 1) {
      // Show achievement popup for first task
      setAchievementDetails({
        title: 'First Steps!',
        achievement: 'Complete your first sustainability task',
        points: 5
      });
      setShowAchievementPopup(true);
    }
    // Check if user has completed 3 tasks (one row in bingo)
    else if (totalTasks === 3) {
      // Check for possible bingo
      setTimeout(() => {
        setAchievementDetails({
          title: 'Bingo!',
          achievement: 'Complete a row of sustainability tasks',
          points: 30
        });
        setShowAchievementPopup(true);
      }, 1000); // Delay to allow task completion notification to show first
    }
    // Example for 5 tasks
    else if (totalTasks === 5) {
      setTimeout(() => {
        setAchievementDetails({
          title: 'Halfway There!',
          achievement: 'Complete 5 sustainability tasks',
          points: 20
        });
        setShowAchievementPopup(true);
      }, 1000);
    }
  };

  // ============================
  // Get CSS Class Based on Task Status
  // ============================

  const getTaskStatusClass = (taskId) => {
    const status = getTaskStatus(taskId);

    switch (status) {
      case 'completed':
        return 'completed';
      case 'pending':
        return 'pending';
      case 'rejected':
        return 'rejected';
      default:
        return '';
    }
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
        <p>Loading tasks...</p>
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

      {/* Navigation Bar */}
      <div className="navigation-bar">
        <button onClick={() => navigate('/userprofile')} className="nav-button">
          View Profile
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

      {/* Achievement Popup */}
      {showAchievementPopup && (
        <AchievementPopup
          title={achievementDetails.title}
          achievement={achievementDetails.achievement}
          points={achievementDetails.points}
          onClose={() => setShowAchievementPopup(false)}
        />
      )}

      {/* Notification and Popup Managers */}
      <NotificationManager />
      <PopupManager />
    </div>
  );
};

export default BingoBoard;