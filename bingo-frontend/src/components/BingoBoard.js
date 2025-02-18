import React, { useEffect, useState } from 'react';
import axios from 'axios';

const BingoBoard = () => {
  const [tasks, setTasks] = useState([]);

  useEffect(() => {
    axios.get("http://127.0.0.1:8000/api/tasks/")
      .then(response => setTasks(response.data))
      .catch(error => console.log(error));
  }, []);

  const completeTask = (taskId) => {
    axios.post("http://127.0.0.1:8000/api/complete_task/", { task_id: taskId }, {
      headers: { Authorization: `Bearer ${localStorage.getItem('token')}` }
    }).then(() => {
      setTasks(tasks.map(task => task.id === taskId ? { ...task, completed: true } : task));
    }).catch(error => console.log(error));
  };

  return (
    <div className="grid grid-cols-3 gap-2 p-4">
      {tasks.map(task => (
        <div
          key={task.id}
          onClick={() => completeTask(task.id)}
          className={`p-6 border text-center cursor-pointer ${
            task.completed ? "bg-green-500 text-white" : "bg-gray-200"
          }`}
        >
          {task.title}
        </div>
      ))}
    </div>
  );
};

export default BingoBoard;
