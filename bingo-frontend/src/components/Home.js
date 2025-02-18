import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const Home = () => {
  const [tasks, setTasks] = useState([]);
  const navigate = useNavigate();

  useEffect(() => {
    // Fetch Bingo tasks from Django API
    const fetchTasks = async () => {
      try {
        const response = await axios.get('http://127.0.0.1:8000/api/tasks/', {
          headers: { Authorization: `Bearer ${localStorage.getItem('token')}` },
        });
        setTasks(response.data);
      } catch (error) {
        console.error('Error fetching tasks:', error);
      }
    };

    fetchTasks();
  }, []);

  const handleCompleteTask = async (taskId) => {
    try {
      await axios.post(
        'http://127.0.0.1:8000/api/complete_task/',
        { task_id: taskId },
        { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
      );

      // Update UI after task completion
      setTasks((prevTasks) =>
        prevTasks.map((task) =>
          task.id === taskId ? { ...task, completed: true } : task
        )
      );
    } catch (error) {
      console.error('Error completing task:', error);
    }
  };

  return (
    <div className="home-container">
      <h1>Bingo Game Board</h1>
      <p>Complete tasks to earn points and win!</p>

      <div className="bingo-board">
        {tasks.map((task) => (
          <div
            key={task.id}
            className={`bingo-cell ${task.completed ? 'completed' : ''}`}
            onClick={() => handleCompleteTask(task.id)}
          >
            <p>{task.description}</p>
            {task.completed && <span>✔️</span>}
          </div>
        ))}
      </div>

      <div className="buttons">
        <button onClick={() => navigate('/leaderboard')}>View Leaderboard</button>
        {localStorage.getItem('token') ? (
          <button
            onClick={() => {
              localStorage.removeItem('token');
              navigate('/login');
            }}
          >
            Logout
          </button>
        ) : (
          <button onClick={() => navigate('/login')}>Login</button>
        )}
      </div>
    </div>
  );
};

export default Home;
