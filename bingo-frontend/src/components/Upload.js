import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import './Upload.css'; // Using our updated CSS file

const Upload = () => {
  // State variables (unchanged)
  const [selectedTask, setSelectedTask] = useState('');
  const [selectedFile, setSelectedFile] = useState(null);
  const [isUploading, setIsUploading] = useState(false);
  const [previewUrl, setPreviewUrl] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [similarityDetails, setSimilarityDetails] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');
  const [isResubmission, setIsResubmission] = useState(false);
  const navigate = useNavigate();

  // Retrieve Selected Task from Local Storage
  useEffect(() => {
    const choice = localStorage.getItem('selectedChoice');
    const isResubmitting = localStorage.getItem('isResubmission') === 'true';

    console.log('Selected Task:', choice);
    console.log('Is Resubmission:', isResubmitting);

    if (choice) {
      setSelectedTask(choice);
    }

    if (isResubmitting) {
      setIsResubmission(true);
    }
  }, []);

  // Handle File Selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];

    if (!file) {
      setSelectedFile(null);
      setPreviewUrl('');
      return;
    }

    // Clear previous errors and similarity details
    setErrorMessage('');
    setSimilarityDetails(null);

    // Validate file type
    const validTypes = ['image/jpeg', 'image/png', 'image/jpg'];
    if (!validTypes.includes(file.type)) {
      setErrorMessage('Please select a JPEG or PNG image file.');
      setSelectedFile(null);
      setPreviewUrl('');
      return;
    }

    // Validate file size (max 10MB)
    if (file.size > 10 * 1024 * 1024) {
      setErrorMessage('Image size is too large. Maximum size is 10MB.');
      setSelectedFile(null);
      setPreviewUrl('');
      return;
    }

    // Set selected file
    setSelectedFile(file);

    // Create preview URL
    const reader = new FileReader();
    reader.onload = () => {
      setPreviewUrl(reader.result);
    };
    reader.readAsDataURL(file);
  };

  // Handle File Submission
  const handleSubmit = async (e) => {
    e.preventDefault();

    if (!selectedFile) {
      setErrorMessage('Please select a file to upload');
      return;
    }

    // Clear previous messages
    setErrorMessage('');
    setSimilarityDetails(null);
    setSuccessMessage('');

    // Set loading state
    setIsUploading(true);

    // Create a FormData object to send the file
    const formData = new FormData();

    // Get the task ID from localStorage
    const taskId = localStorage.getItem('selectedTaskId');

    if (!taskId) {
      setErrorMessage('Task ID not found. Please select a task again.');
      setIsUploading(false);
      navigate('/bingo');
      return;
    }

    formData.append('task_id', taskId);
    formData.append('photo', selectedFile);

    // Add flag for resubmission if applicable
    if (isResubmission) {
      formData.append('is_resubmission', 'true');
    }

    try {
      // Get the access token from localStorage
      const token = localStorage.getItem('accessToken');

      if (!token) {
        setErrorMessage('You must be logged in to submit a task');
        setIsUploading(false);
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
        // Clear the resubmission flag from localStorage
        localStorage.removeItem('isResubmission');

        setSuccessMessage(data.message || (isResubmission
          ? 'Thank you for resubmitting your task! We will review it soon.'
          : 'Thank you for your submission! We will review it soon.'));

        // Delay navigation to allow user to see success message
        setTimeout(() => {
          navigate('/bingo');
        }, 2000);
      } else {
        // Handle fraud detection errors specially
        if (data.similarity) {
          // Set specific similarity details for UI display
          setSimilarityDetails({
            similarity: data.similarity,
            message: data.message
          });
          setErrorMessage(data.error || 'Please take a new photo for this task.');
        } else {
          setErrorMessage(data.message || data.error || 'Failed to submit task. Please try again.');
        }
      }
    } catch (error) {
      console.error('Error submitting task:', error);
      setErrorMessage('An error occurred while submitting your task. Please try again.');
    } finally {
      setIsUploading(false);
    }
  };

  // Handle Back Button
  const handleBack = () => {
    // Clear the resubmission flag from localStorage
    localStorage.removeItem('isResubmission');
    navigate('/bingo');
  };

  return (
    <div className="upload-container">
      {/* Page Header - Outside the scrollable card */}
      <h1>{isResubmission ? 'Resubmit Your Task' : 'Upload your proof of Gameplay'}</h1>
      
      {/* Card Container - Scrollable content */}
      <div className="upload-form-card">
        {/* Display the selected task */}
        <div className="selected-task">
          <h3>Selected Task:</h3>
          <p>{selectedTask}</p>
        </div>

        {/* Display resubmission message if applicable */}
        {isResubmission && (
          <div className="resubmission-notice">
            <p>You are resubmitting a previously rejected task. Please address the feedback from the game keeper.</p>
          </div>
        )}

        {/* Error and Success Messages */}
        {errorMessage && (
          <div className="error-message">
            <p>{errorMessage}</p>
          </div>
        )}

        {/* Similarity Details (for fraud detection) */}
        {similarityDetails && (
          <div className="similarity-warning">
            <h4>Duplicate Image Detected</h4>
            <p>{similarityDetails.message}</p>
            <p>Similarity: {similarityDetails.similarity}</p>
            <div className="similarity-tips">
              <h5>Tips:</h5>
              <ul>
                <li>Take a new photo specifically for this task</li>
                <li>Make sure your photo clearly shows you completing this specific task</li>
                <li>Each task requires its own unique photo evidence</li>
              </ul>
            </div>
          </div>
        )}

        {successMessage && (
          <div className="success-message">
            <p>{successMessage}</p>
          </div>
        )}

        {/* File Upload Form */}
        <form onSubmit={handleSubmit}>
          <div className="file-input-container">
            <label htmlFor="file-upload" className="custom-file-upload">
              Choose File
            </label>
            <input
              id="file-upload"
              type="file"
              accept="image/jpeg,image/png"
              onChange={handleFileChange}
              required
            />
            <span className="file-name">
              {selectedFile ? selectedFile.name : 'No file selected'}
            </span>
          </div>

          {/* Image Preview with Fixed Height Container */}
          {previewUrl && (
            <div className="image-preview">
              <h3>Preview:</h3>
              <div className="image-preview-container">
                <img src={previewUrl} alt="Preview" />
              </div>
            </div>
          )}

          {/* Navigation Buttons */}
          <div className="button-container">
            <button type="button" onClick={handleBack} className="back-button">
              Back
            </button>
            <button
              type="submit"
              className="submit-button"
              disabled={isUploading || !selectedFile}
            >
              {isUploading ? 'Uploading...' : (isResubmission ? 'Resubmit' : 'Upload')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Upload;