import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Upload = () => {
  const [selectedTask, setSelectedTask] = useState('');
  const navigate = useNavigate();
  
  useEffect(() => {
    const choice = localStorage.getItem('selectedChoice');
    console.log('Selected task:', choice);
    if (choice) {
      setSelectedTask(choice);
    }
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    alert('Thank you for your submission! We will review it soon.');
    // Here you can add actual file upload logic
    navigate('/bingo'); // Return to bingo board after submission
  };

  return (
    <div className="upload-container">
      <h1>Upload your proof of Gameplay</h1>
      <p>Selected Task: {selectedTask}</p>
      <form onSubmit={handleSubmit}>
        <input type="file" required />
        <button type="submit">Upload</button>
      </form>
    </div>
  );
};

export default Upload;