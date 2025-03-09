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
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate(); // Hook for programmatic navigation

  // ============================
  // Fetch Tasks from API on Component Mount
  // ============================

  useEffect(() => {
    axios.get(`${API_URL}/api/tasks/`)
      .then(response => {
        console.log('Tasks fetched:', response.data);
        setTasks(response.data);
        setLoading(false);
      })
      .catch(error => {
        console.error("Error fetching tasks:", error);
        setError("Failed to load tasks. Please try again.");
        setLoading(false);
      });
  }, []);

  // ============================
  // Handle Task Click (Completion, Upload, or Scan)
  // ============================

  const handleTaskClick = async (task) => {
    if (!task) return;

    // If task requires an upload, navigate to the upload page
    if (task.requires_upload) {
      localStorage.setItem("selectedChoice", task.description);
      navigate("/upload");
    } 
    // If task requires a scan, navigate to the scan page
    else if (task.requires_scan) {
      localStorage.setItem("selectedChoice", task.description);
      navigate("/scan");
    } 
    // Otherwise, mark the task as completed via API
    else {
      try {
        const response = await axios.post(`${API_URL}/task/complete/`, { task_id: task.id }, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });

        // If the task is successfully completed, update the state
        if (response.status === 200) {
          setTasks(prevTasks =>
            prevTasks.map(t =>
              t.id === task.id ? { ...t, completed: true } : t
            )
          );
        }
      } catch (error) {
        console.error("Error completing task:", error);
      }
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
              className={`bingo-cell ${task.completed ? 'completed' : ''}`}
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
              </div>
            </div>
          )) : <p>No tasks available.</p>}
        </div>
      )}

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
