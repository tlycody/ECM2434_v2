import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL;

const Home = () => {
  const [tasks, setTasks] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchTasks = async () => {
      try {
        const response = await axios.get(`${API_URL}/tasks/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        setTasks(response.data);
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    };

    fetchTasks();
  }, []);

  return (
    <div className="home-container">
      <h1>Bingo Game Board</h1>
      <p>Complete tasks to earn points and win!</p>

      <div className="bingo-board">
        {tasks.map((task) => (
          <div key={task.id} className={`bingo-cell ${task.completed ? 'completed' : ''}`}>{task.description}</div>
        ))}
      </div>

      <div className="buttons">
        <button onClick={() => navigate('/leaderboard')}>View Leaderboard</button>
        <button onClick={() => navigate('/profile')}>Profile</button>
      </div>
    </div>
  );
};

export default Home;