// BingoBoard.js
import React, { useEffect, useState } from 'react';
import axios from 'axios';
import './bingoboard.css';  

const BingoBoard = () => {
  const [tasks, setTasks] = useState([
    // Add some initial tasks (we can fetch these later)
    { id: 1, description: "Task 1", completed: false },
    { id: 2, description: "Task 2", completed: false },
    { id: 3, description: "Task 3", completed: false },
    { id: 4, description: "Task 4", completed: false },
    { id: 5, description: "Task 5", completed: false },
    { id: 6, description: "Task 6", completed: false },
    { id: 7, description: "Task 7", completed: false },
    { id: 8, description: "Task 8", completed: false },
    { id: 9, description: "Task 9", completed: false },
  ]);

  return (
    <div className="container">
      <h1>Sustainability Bingo</h1>
      <div className="bingo-board">
        <div className="grid">
          {tasks.map((task, index) => (
            <div key={index} className="cell">
              <div className="cell-content">
                {task.description}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default BingoBoard;