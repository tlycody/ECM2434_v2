// BingoBoard.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './bingoboard.css';  
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const BingoBoard = () => {
  const [tasks, setTasks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`${API_URL}/tasks/`)
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

  const handleTaskClick = (task) => {
    if (!task) return;
  
    if (task.requires_upload) {
      localStorage.setItem("selectedChoice", task.description);
      navigate("/upload");
    } else if (task.requires_scan) {
      localStorage.setItem("selectedChoice", task.description);
      navigate("/scan");
    } else {
      setTasks(prevTasks =>
        prevTasks.map(t =>
          t.id === task.id ? { ...t, completed: !t.completed } : t
        )
      );
    }
  };

  return (
    <div className="bingo-container">
      <h1 className="bingo-header">Sustainability Bingo</h1>
      {loading ? (
        <p>Loading tasks...</p>
      ) : error ? (
        <p className="error-message">{error}</p>
      ) : (
        <div className="bingo-board">
          {tasks.length > 0 ? tasks.map((task) => (
            <div
              key={task.id}
              className={`bingo-cell ${task.completed ? 'completed' : ''}`}
              onClick={() => handleTaskClick(task)}
            >
              <div className='cell-content'>
                <div className='points'><strong>{task.points} Points</strong></div>
                <div className='description'>{task.description}</div>
                {task.requires_upload && <div className='upload-indicator'>📷</div>}
                {task.requires_scan && <div className='scan-indicator'>🤳🏻</div>}
              </div>
            </div>
          )) : <p>No tasks available.</p>}
        </div>
      )}
    </div>
  );
};

export default BingoBoard;
