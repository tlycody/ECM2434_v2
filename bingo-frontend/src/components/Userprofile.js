import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';

const API_URL = process.env.REACT_APP_API_URL;

const Profile = () => {
  const [userData, setUserData] = useState({});
  const [tasks, setTasks] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await axios.get(`${API_URL}/user/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });
        setUserData(response.data);
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    const fetchCompletedTasks = async () => {
      try {
        const response = await axios.get(`${API_URL}/tasks/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        setTasks(response.data);
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    };

    fetchUserData();
    fetchCompletedTasks();
  }, [navigate]);

  return (
    <div className="profile-container">
      <h1 className="profile-title">Player Profile</h1>
      <div className="profile-info">
        <h2>Welcome, {userData.username}</h2>
        <p><strong>Total Points:</strong> {userData.total_points || 0}</p>
        <p><strong>Completed Tasks:</strong> {tasks.length}</p>
      </div>

      <div className="completed-tasks">
        <h3>Completed Bingo Tasks</h3>
        {tasks.length > 0 ? (
          <ul>
            {tasks.map(task => (
              <li key={task.id}>{task.description}</li>
            ))}
          </ul>
        ) : (
          <p>No completed tasks yet.</p>
        )}
      </div>

      <div className="buttons">
        <button onClick={() => navigate('/bingo')}>Back to Bingo Board</button>
        <button onClick={() => navigate('/leaderboard')}>View Leaderboard</button>
        <button
          onClick={() => {
            localStorage.removeItem('token');
            navigate('/login');
          }}
        >
          Logout
        </button>
      </div>
    </div>
  );
};

export default Profile;
