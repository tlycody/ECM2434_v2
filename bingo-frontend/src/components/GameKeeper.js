// GameKeeper.js - Enhanced with rejection comments
import React, { useState, useEffect } from 'react';
import axios from 'axios';
import './GameKeeper.css';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const GameKeeper = () => {
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();
  const [tasks, setTasks] = useState([]);
  const [pendingTasks, setPendingTasks] = useState([]);
  const [leaderboard, setLeaderboard] = useState([]);
  const [selectedImage, setSelectedImage] = useState(null);
  const [newTask, setNewTask] = useState({
    description: '',
    points: 10,
    requires_upload: false,
    requires_scan: false
  });

  // New state variables for rejection modal
  const [rejectionModalOpen, setRejectionModalOpen] = useState(false);
  const [selectedForRejection, setSelectedForRejection] = useState(null);
  const [rejectionComment, setRejectionComment] = useState('');

  // Get token from localStorage
  const token = localStorage.getItem('accessToken');

  // Set up auth header
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
      fetchData();
    }
  }, [token]);

  // Fetch initial data
  const fetchData = async () => {
    setLoading(true);
    try {
      // Get tasks
      const tasksResponse = await axios.get(`${API_URL}/api/tasks/`);
      setTasks(tasksResponse.data);

      // Get pending tasks with debug logs
      console.log("Fetching pending tasks...");
      try {
        const pendingResponse = await axios.get(`${API_URL}/api/pending-tasks/`, {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        console.log("Pending tasks response:", pendingResponse);
        setPendingTasks(pendingResponse.data);
      } catch (pendingError) {
        console.error("Error fetching pending tasks:", pendingError);
        setError("Failed to load pending tasks: " + (pendingError.response?.data?.error || pendingError.message));
      }

      // Get leaderboard
      const leaderboardResponse = await axios.get(`${API_URL}/api/leaderboard/`);
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
      await axios.post(`${API_URL}/admin/tasks/create/`, newTask);
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
      console.log(`Approving: user_id=${userId}, task_id=${taskId}`);
      await axios.post(`${API_URL}/api/approve-task/`, {
        user_id: userId,
        task_id: taskId
      });
      // Update the UI after successful approval
      fetchData();
    } catch (error) {
      console.error('Error approving task:', error);
      setError("Failed to approve task");
    }
  };

  // Show rejection modal for a task
  const showRejectionModal = (userId, taskId) => {
    setSelectedForRejection({userId, taskId});
    setRejectionModalOpen(true);
  };

  // Handle task rejection with comments
  const handleRejectTask = async () => {
    if (!selectedForRejection) return;

    const { userId, taskId } = selectedForRejection;

    try {
      await axios.post(`${API_URL}/api/reject-task/`, {
        user_id: userId,
        task_id: taskId,
        reason: rejectionComment || "Task rejected by game keeper" // Use default if empty
      });

      // Clear the rejection comment and close modal
      setRejectionComment('');
      setRejectionModalOpen(false);
      setSelectedForRejection(null);

      // Refresh data
      fetchData();
    } catch (error) {
      console.error('Error rejecting task:', error);
      setError("Failed to reject task");
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

  // Handle image click to show enlarged view
  const handleImageClick = (imageUrl) => {
    setSelectedImage(imageUrl);
  };

  // Close enlarged image view
  const closeImageView = () => {
    setSelectedImage(null);
  };

  // Handle logout
  const handleLogout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('userProfile');
    navigate('/login');
  };

  // Check user submissions for the same task
  const checkUserSubmissions = async (userId, taskId) => {
    try {
      const response = await axios.get(`${API_URL}/api/user-submissions/?user_id=${userId}&task_id=${taskId}`);
      return response.data.submissions || [];
    } catch (error) {
      console.error("Error checking user submissions:", error);
      return [];
    }
  };

  // Enhanced render method with user image history and fraud detection tools
  return (
    <div className="gamekeeper-container">
      <div className="header">
        <h1>BINGO Game - Game Keeper Dashboard</h1>
        <button onClick={handleLogout} className="logout-btn">
          Logout
        </button>
      </div>

      {error && <div className="error-message">{error}</div>}

      {/* Image Modal for enlarged view */}
      {selectedImage && (
        <div className="image-modal-overlay" onClick={closeImageView}>
          <div className="image-modal-content" onClick={e => e.stopPropagation()}>
            <span className="close-button" onClick={closeImageView}>&times;</span>
            <img src={selectedImage} alt="Enlarged view" />
          </div>
        </div>
      )}

      {/* Rejection Modal */}
      {rejectionModalOpen && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h3>Reject Task Submission</h3>
            <p>Please provide feedback to the user about why their submission was rejected:</p>

            <textarea
              value={rejectionComment}
              onChange={(e) => setRejectionComment(e.target.value)}
              placeholder="Enter rejection reason..."
              className="rejection-comment"
              rows={4}
            />

            <div className="modal-actions">
              <button
                onClick={() => {
                  // Close modal without rejecting
                  setRejectionModalOpen(false);
                  setSelectedForRejection(null);
                  setRejectionComment('');
                }}
                className="cancel-button"
              >
                Cancel
              </button>
              <button
                onClick={handleRejectTask}
                className="reject-btn"
              >
                Confirm Rejection
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Pending Tasks Section with Enhanced Fraud Detection */}
      <div className="pending-tasks-section">
        <h2>Pending Task Approvals</h2>
        {loading ? (
          <p>Loading pending tasks...</p>
        ) : pendingTasks.length === 0 ? (
          <p>No pending tasks to approve</p>
        ) : (
          <div className="task-cards-container">
            {pendingTasks.map((task, index) => (
              <div key={index} className="task-approval-card">
                <div className="task-header">
                  <h3>{task.username}</h3>
                  <span className="task-points">{task.points} points</span>
                </div>

                <div className="task-description">
                  <p>{task.task_description}</p>
                </div>

                <div className="submission-details">
                  <p>Submitted: {new Date(task.completion_date).toLocaleString()}</p>
                </div>

                <div className="task-photo">
                  {task.photo_url ? (
                    <>
                      <img
                        src={task.photo_url}
                        alt="Task submission"
                        onClick={() => handleImageClick(task.photo_url)}
                        className="submission-photo"
                      />
                      <div className="image-tools">
                        <button
                          className="enlarge-btn"
                          onClick={() => handleImageClick(task.photo_url)}
                        >
                          🔍 Zoom
                        </button>
                      </div>
                    </>
                  ) : (
                    <div className="no-photo">No photo provided</div>
                  )}
                </div>

                <div className="task-actions">
                  <button
                    className="approve-btn"
                    onClick={() => handleApproveTask(task.user_id, task.task_id)}
                  >
                    ✅ Approve
                  </button>

                  <button
                    className="reject-btn"
                    onClick={() => showRejectionModal(task.user_id, task.task_id)}
                  >
                    ❌ Reject
                  </button>
                </div>
              </div>
            ))}
          </div>
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
                <td>
                  {task.requires_upload ? (
                    <span>Photo requirement: Yes</span>
                  ) : (
                    <span>No photo required</span>
                  )}
                </td>
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