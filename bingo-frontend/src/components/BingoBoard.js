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
      description: "Finish Green Consultant training",
      points: 10,
      requiresUpload: true,
      requireScan: false,
    },
    {
      id: 2,
      description:  "Join a 'Green' society",
      points: 7,
      requiresUpload: true,
      requireScan: false,
    },
    {
      id: 3,
      description:  "Get involved in Gift it, Reuse it scheme",
      points: 10,
      requiresUpload: false,
      requireScan: true,
    },
    {
      id: 4,
      description: "Use British Heart Foundation Banks on campus to recycle clothes",
      points: 8,
      requiresUpload: false,
      requireScan: true,
    },
    {
      id: 5,
      description: "Sign up to university sustainability newsletter",
      points: 5,
      requiresUpload: true,
      requireScan: false,
    },
    {
      id: 6,
      description: "Refill your reusable water bottle from one of over 100 free water refill stations on campus",
      points: 8,
      requiresUpload: true,
    },
    {
      id: 7,
      description: "Shopping at Exeter's zero waste shops, Nourish and Zero",
      points: 10,
      requiresUpload: false,
      requireScan: true,
    },
    {
      id: 8,
      description: "Empty glasses put in nearest glass bottle bank",
      points: 8,
      requiresUpload: true,
      requireScan: false,
    },
    {
      id: 9,
      description: "Getting involved in ESV - Environmental Project",
      points: 10,
      requiresUpload: false,
      requireScan: true,
    },
  ]);
  const navigate = useNavigate();

  useEffect(() => {
    axios.get(`${API_URL}/tasks/`)
      .then(response => {
        console.log('Tasks fetched:',response.data);
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
      // Open webqr.com in a new tab
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
        <h1 className="bingo-header">Bingo Board</h1>
        <div className="bingo-board">
        {tasks.map((task, index) => (
          <div
              key={task.id}
              className={`bingo-cell ${task.completed ? 'completed' : ''}`}
              onClick={() => handleTaskClick(task)} // Added onClick handler
            >
              <div className='cell-content'>
                <div className='points'>{tasks.points} marks</div>
                <div className='description'>{task.description}</div>
                {task.requiresUpload && <div className='upload indicator'>📷</div>}
                {task.requireScan && (
  <a href="https://webqr.com/" target="_blank" rel="scan qr code">
    <div className="scan-indicator">🤳🏻</div>
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