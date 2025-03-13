// ============================
// BingoBoard Component
// ============================

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './bingoboard.css';  
import { useNavigate } from 'react-router-dom';

// Define the API URL (fallback to localhost if not set in environment variables)
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const BingoBoard = () => {
  // State variables for managing tasks, loading status, and error messages
  const [tasks, setTasks] = useState([]);
  const [userTasks, setUserTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
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
      })
      .catch(error => {
        console.error("Error fetching data:", error);
        setError("Failed to load tasks. Please try again or log in.");
        setLoading(false);
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
  // Handle Task Click (Completion, Upload, or Scan)
  // ============================

  const handleTaskClick = async (task) => {
    if (!task) return;

    // Check if task is already completed or pending
    const status = getTaskStatus(task.id);
    if (status === 'completed' || status === 'pending') {
      console.log(`Task ${task.id} is already ${status}`);
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
      } catch (error) {
        console.error("Error completing task:", error);
      }
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
    </div>
  );
};

export default BingoBoard;