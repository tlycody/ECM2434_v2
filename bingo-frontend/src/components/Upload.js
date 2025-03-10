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

  const handleSubmit = async (e) => {
    e.preventDefault();
  
    // Get the file from the input
    const fileInput = e.target.querySelector('input[type="file"]');
    const file = fileInput.files[0];
  
    if (!file) {
      alert('Please select a file to upload');
      return;
    }

    // Create a FormData object to send the file
    const formData = new FormData();
  
    // Add the task_id - you need to store the task ID, not just the description
    // Make sure you're storing the task ID in localStorage when a task is selected
    const taskId = localStorage.getItem('selectedTaskId');
  
    if (!taskId) {
      alert('Task ID not found. Please select a task again.');
      navigate('/bingo');
      return;
    }
  
    formData.append('task_id', taskId);
    formData.append('photo', file);
  
    try {
      // Get the access token from localStorage
      const token = localStorage.getItem('accessToken');
    
      if (!token) {
        alert('You must be logged in to submit a task');
        navigate('/login');
        return;
      }
    
      // Make the API request
      const response = await fetch('http://localhost:8000/api/complete_task/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        },
        body: formData
      });
    
      const data = await response.json();
    
      if (response.ok) {
        alert(data.message || 'Thank you for your submission! We will review it soon.');
        navigate('/bingo');
      } else {
        alert(data.message || 'Failed to submit task. Please try again.');
      }
    } catch (error) {
      console.error('Error submitting task:', error);
      alert('An error occurred while submitting your task. Please try again.');
    }
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
