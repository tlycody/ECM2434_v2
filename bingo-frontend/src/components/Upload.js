// ============================
// Upload Component - Task Proof Submission
// ============================

import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const Upload = () => {
  // State to store the selected task from localStorage
  const [selectedTask, setSelectedTask] = useState('');
  const navigate = useNavigate(); // React Router navigation hook
  
  // ============================
  // Retrieve Selected Task from Local Storage
  // ============================

  useEffect(() => {
    const choice = localStorage.getItem('selectedChoice'); // Retrieve the stored task choice
    console.log('Selected Task:', choice);
    if (choice) {
      setSelectedTask(choice);
    }
  }, []);

  // ============================
  // Handle File Submission
  // ============================

  const handleSubmit = (e) => {
    e.preventDefault();

    alert('Thank you for your submission! We will review it soon.');
    // TODO: Implement actual file upload logic

    navigate('/bingo'); // Redirect to bingo board after submission
  };

  // ============================
  // Render Upload UI
  // ============================

  return (
    <div className="upload-container">
      {/* Page Header */}
      <h1>Upload your proof of Gameplay</h1>
      
      {/* Display the selected task */}
      <p>Selected Task: {selectedTask}</p>

      {/* File Upload Form */}
      <form onSubmit={handleSubmit}>
        <input type="file" required /> {/* File input field */}
        <button type="submit">Upload</button> {/* Submit button */}
      </form>
    </div>
  );
};

export default Upload;
