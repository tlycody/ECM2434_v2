import React, { useEffect, useState } from 'react';
import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL;

const BingoBoard = () => {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    axios.get(`${API_URL}/tasks/`)
      .then(response => setTasks(response.data))
      .catch(error => console.log(error));
  }, []);

  return (
    <div className="bingo-board">
      {tasks.map((task) => (
        <div key={task.id} className={`bingo-cell ${task.completed ? 'completed' : ''}`}>{task.description}</div>
      ))}
    </div>
  );
};

export default BingoBoard;
