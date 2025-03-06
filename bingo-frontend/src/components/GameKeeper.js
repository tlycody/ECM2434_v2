// SimpleGameKeeper.js - Minimal admin component for game keepers
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './GameKeeper.css';
import { useNavigate } from 'react-router-dom'; 

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";


const GameKeeper = () => {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // React Router navigation hook
  const [tasks, setTasks] = useState([]);
  const [pendingTasks, setPendingTasks]= useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [newTask, setNewTask] = useState({
    description: '',
    points: 10,
    requires_upload: false,
    requires_scan: false
  });
  
  // Get token from localStorage
  const token = localStorage.getItem('token');
  
  // Set up auth header
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchData();
    }
  }, [token]);
  
  useEffect(() => {
    fetchData();
  }, []);

  // Fetch initial data
const fetchData = async () => {
    setLoading(true);
    try {
      // Get tasks
      const tasksResponse = await axios.get(`${API_URL}/api/tasks/`);
      console.log('Tasks fetched:', tasksResponse.data);
      setTasks(tasksResponse.data);

      //Get Pending tasks
// In your fetchData function in GameKeeper.js
      const pendingResponse = await axios.get(`${API_URL}/api/pending-tasks/`, {
      headers: {
      'Authorization': `Bearer ${token}`
      }
      });
      
      // Get leaderboard
      const leaderboardResponse = await axios.get(`${API_URL}/api/leaderboard/`);
      console.log("Leaderboard fetched:", leaderboardResponse.data);
      setLeaderboard(leaderboardResponse.data);
    } catch (error) {
      console.error('Error fetching data:', error);
      setError("Failed to load data. Please try again.");
      if (error.response && error.response.status === 403) {
        setError("You don't have permission to access this page");
      }
    } finally {
      setLoading(false);
    }
  };
  
  // Handle creating a new task
  const handleCreateTask = async (e) => {
    e.preventDefault();
    try {
      await axios.post('http://127.0.0.1:8000/admin/tasks/create/', newTask);
      setNewTask({
        description: '',
        points: 10,
        requires_upload: false,
        requires_scan: false
      });
      fetchData(); // Refresh tasks
    } catch (error) {
      console.error('Error creating task:', error);
    }
  };
  
    // Handle task approval
    const handleApproveTask = async (userId, taskId) => {
      try {
        await axios.post(`${API_URL}/api/approve-task/`, {
          user_id: userId,
          task: taskId
        });
        // Update the UI after successful approval
        fetchData();
      } catch (error) {
        console.error('Error approving task:', error);
        setError("Failed to approve task");
      }
    };

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setNewTask({
      ...newTask,
      [name]: type === 'checkbox' ? checked : value
    });
  };
  
  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('token');
    window.location.href = '/login';
  };
  
  return (
    <div className="gamekeeper-container">
      <div className="header">
        <h1>Bingo Game Keeper</h1>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>

{/* Pending Tasks Section */}
<div className="pending-tasks-section">
  <h2>Pending Task Approvals</h2>
  {pendingTasks.length === 0 ? (
    <p>No pending tasks to approve</p>
  ) : (
    <table>
      <thead>
        <tr>
          <th>Username</th>
          <th>Task Description</th>
          <th>Points</th>
          <th>Photo</th>
          <th>Action</th>
        </tr>
      </thead>
      <tbody>
        {pendingTasks.map((task, index) => (
          <tr key={index}>
            <td>{task.username}</td>
            <td>{task.task_description}</td>
            <td>{task.points}</td>
            <td>
              {task.photo_url ? (
                <img 
                  src={task.photo_url} 
                  alt="Task submission" 
                  style={{ maxWidth: '100px', maxHeight: '100px' }} 
                />
              ) : (
                <span>No photo</span>
              )}
            </td>
            <td>
              <button 
                className="approve-btn"
                onClick={() => handleApproveTask(task.user_id, task.task_id)}
              >
                Approve
              </button>
            </td>
          </tr>
        ))}
      </tbody>
    </table>
  )}
</div>

      {/* Create Task Section */}
      <div className="create-task-section">
        <h2>Create New Task</h2>
        <form onSubmit={handleCreateTask}>
          <div className="form-group">
            <label>
              Description:
              <textarea
                name="description"
                value={newTask.description}
                onChange={handleInputChange}
                required
              />
            </label>
          </div>
          
          <div className="form-group">
            <label>
              Points:
              <input
                type="number"
                name="points"
                value={newTask.points}
                onChange={handleInputChange}
                required
              />
            </label>
          </div>
          
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                name="requires_upload"
                checked={newTask.requires_upload}
                onChange={handleInputChange}
              />
              Requires Photo Upload
            </label>
          </div>
          
          <div className="form-group checkbox">
            <label>
              <input
                type="checkbox"
                name="requires_scan"
                checked={newTask.requires_scan}
                onChange={handleInputChange}
              />
              Requires QR Scan
            </label>
          </div>
          
          <button type="submit" className="create-btn">
            Create Task
          </button>
        </form>
      </div>
      
      {/* Tasks List */}
      <div className="tasks-section">
        <h2>Current Tasks</h2>
        <table>
          <thead>
            <tr>
              <th>Description</th>
              <th>Points</th>
              <th>Upload</th>
              <th>QR Scan</th>
            </tr>
          </thead>
          <tbody>
            {tasks.map(task => (
              <tr key={task.id}>
                <td>{task.description}</td>
                <td>{task.points}</td>
                <td>{task.requires_upload ? 'Yes' : 'No'}</td>
                <td>{task.requires_scan ? 'Yes' : 'No'}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      
      {/* Leaderboard */}
      <div className="leaderboard-section">
        <h2>Leaderboard</h2>
        <table>
          <thead>
            <tr>
              <th>Rank</th>
              <th>Username</th>
              <th>Points</th>
            </tr>
          </thead>
          <tbody>
            {leaderboard.map((entry, index) => (
              <tr key={index}>
                <td>{index + 1}</td>
                <td>{entry.user}</td>
                <td>{entry.points}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default GameKeeper;