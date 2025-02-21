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

  const getRows = () => {
    const rows = [];
  for (let i = 0; i < tasks.length; i += 3){
    rows.push(tasks.slice(i,i+3));
  }  
  return rows;
};

return (
  <div className="bingo-board">
    {getRows().map((row, rowIndex) => (
      <div key={rowIndex} className="bingo-row">
        {row.map((task) => (
          <div key={task.id} className={`bingo-cell ${task.completed ? 'completed' : ''}`}>
            {task.description}
          </div>
        ))}
      </div>
    ))}
  </div>
);
}

export default BingoBoard;
