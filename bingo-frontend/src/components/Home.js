// ============================
// Home Component - Bingo Game
// ============================

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './Home.css';

// Fetch API URL from environment variables (fallback to localhost if not defined)
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Home = () => {
  // State to store fetched tasks (optional for later functionality)
  const [tasks, setTasks] = useState([]);
  const navigate = useNavigate(); // React Router navigation hook

  // ============================
  // Fetch Tasks on Component Mount
  // ============================
  
  useEffect(() => {
    const fetchTasks = async () => {
      try {
        // Fetch task list from API with authentication token
        const response = await axios.get(`${API_URL}/tasks/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        
        // ✅ Update the task state with API response data
        setTasks(response.data);
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    };

    fetchTasks();
  }, []); // ✅ Empty dependency array ensures it runs only once when the component mounts

  // ============================
  // Render Home UI
  // ============================

  return (
    <div className="home-container">
      {/* Header Section */}
      <h1>Bingo Game Board</h1>
      <p>Complete tasks to earn points and win!</p>

      {/* Navigation Buttons */}
      <div className="buttons">
        <button onClick={() => navigate('/homeboard')}>View Leaderboard</button>
        <button onClick={() => navigate('/login')}>Login</button>
        <button onClick={() => navigate('/overview')}>Game Guide</button>
      </div>
    </div>
  );
};

export default Home;
