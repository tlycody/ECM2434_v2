// BingoBoard.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './bingoboard.css';  
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const BingoBoard = () => {
  const [tasks, setTasks] = useState([
    {
      id: 1,
      description: "Complete the Green Consultant Training Program",
      points: 10,
      requiresUpload: true,
      requireScan: false,
    },
    {
      id: 2,
      description: "Join an Environmental Society (e.g., Be the Change or Enactus)",
      points: 7,
      requiresUpload: true,
      requireScan: false,
    },
    {
      id: 3,
      description: "Participate in the University’s 'Gift it, Reuse it' Initiative",
      points: 10,
      requiresUpload: false,
      requireScan: true,
    },
    {
      id: 4,
      description: "Donate clothes using the British Heart Foundation Banks on campus",
      points: 8,
      requiresUpload: false,
      requireScan: true,
    },
    {
      id: 5,
      description: "Subscribe to the University’s Sustainability Newsletter",
      points: 5,
      requiresUpload: true,
      requireScan: false,
    },
    {
      id: 6,
      description: "Refill your reusable water bottle at any of the 100+ free refill stations on campus",
      points: 8,
      requiresUpload: true,
    },
    {
      id: 7,
      description: "Shop sustainably at local zero-waste stores (e.g., Nourish and Zero)",
      points: 10,
      requiresUpload: false,
      requireScan: true,
    },
    {
      id: 8,
      description: "Recycle glass bottles by placing them in the designated campus bins",
      points: 8,
      requiresUpload: true,
      requireScan: false,
    },
    {
      id: 9,
      description: "Engage in the Environmental Sustainability Volunteer (ESV) Project",
      points: 10,
      requiresUpload: false,
      requireScan: true,
    },
  ]);

  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`${API_URL}/tasks/`)
      .then(response => {
        console.log('Tasks fetched:', response.data);
        setTasks(response.data);
      })
      .catch(error => console.log(error));
  }, []);

  const handleTaskClick = (task) => {
    if (!task) return;
  
    if (task.requiresUpload) {
      localStorage.setItem("selectedChoice", task.description);
      navigate("/upload");
    } else if (task.requireScan) {
      localStorage.setItem("selectedChoice", task.description);
      window.open("https://webqr.com/", "_blank");
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
      <div className="bingo-board">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`bingo-cell ${task.completed ? 'completed' : ''}`}
            onClick={() => handleTaskClick(task)}
          >
            <div className='cell-content'>
              <div className='points'>{task.points} Points</div>
              <div className='description'>{task.description}</div>
              {task.requiresUpload && <div className='upload-indicator'>📷</div>}
              {task.requireScan && (
                <a href="https://webqr.com/" target="_blank" rel="noreferrer">
                  <div className="scan-indicator">📍</div>
                </a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BingoBoard;
