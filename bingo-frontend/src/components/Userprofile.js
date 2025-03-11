// ============================
// User Profile Component with Badges
// ============================

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';

// Fetch API URL from environment variables (fallback to localhost if not set)
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

// Default profile picture path with the correct filename
const DEFAULT_PROFILE_PIC = "/media/profile_pics/default.png";

const Profile = () => {
  // State variables for user data, completed tasks, edit mode, and profile image
  const [userData, setUserData] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [badges, setBadges] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [updatedUser, setUpdatedUser] = useState({});
  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const navigate = useNavigate(); // React Router navigation hook

  // ============================
  // Fetch User Data, Completed Tasks & Badges
  // ============================
  useEffect(() => {
    // Fetch user profile data
    const fetchUserData = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/profile/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });
        console.log('User profile data:', response.data);


        // Log the profile picture URL for debugging
        if (response.data.profile_picture) {
          console.log('Original profile picture path:', response.data.profile_picture);
          console.log('Constructed profile picture URL:', `${API_URL}${response.data.profile_picture}`);
        } else {
          console.log('No profile picture found in the response data');
        }


        setUserData(response.data);
        setUpdatedUser(response.data);
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };


    // Fetch tasks for display in the list
    const fetchCompletedTasks = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/tasks/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });
    
  
        
        // Filter tasks that are completed or approved
        const completedTasks = response.data.filter(task => 
          task.status === 'completed' || 
          task.status === 'approved' || 
          task.completed === true
        );
        
        setTasks(completedTasks);
      } catch (error) {
        console.error('Error fetching completed tasks:', error);
      }
    };

    // Fetch user badges
    const fetchUserBadges = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/badges/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });
        setBadges(response.data);
      } catch (error) {
        console.error('Error fetching badges:', error);
      }
    };

    fetchUserData();
    fetchCompletedTasks();
    fetchUserBadges();
  }, []);

  // ============================
  // Handle Input & File Changes
  // ============================

  // Handle text input changes for updating user details
  const handleInputChange = (e) => {
    setUpdatedUser({ ...updatedUser, [e.target.name]: e.target.value });
  };

  // Handle profile picture selection
  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setProfileImage(file);
      
      // Create a preview URL for the selected image
      const previewUrl = URL.createObjectURL(file);
      setImagePreview(previewUrl);
    }
  };

  // ============================
  // Handle Profile Update
  // ============================

  const handleSubmit = async (e) => {
    e.preventDefault();
    const formData = new FormData();

    if (profileImage) {
      formData.append('profile_picture', profileImage);
    }

    Object.keys(updatedUser).forEach((key) => {
      formData.append(key, updatedUser[key]);
    });

    try {
      const response = await axios.put(`${API_URL}/api/profile/update/`, formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
          'Content-Type': 'multipart/form-data',
        },
      });

      console.log('Profile update response:', response.data);

      // Log the updated profile picture URL
      if (response.data.profile_picture) {
        console.log('Updated profile picture path:', response.data.profile_picture);
      }

      alert('Profile updated successfully');
      setEditMode(false);

      // Update state with new profile data
      setUserData(response.data);

      // Clean up preview URL
      if (imagePreview) {
        URL.revokeObjectURL(imagePreview);
        setImagePreview(null);
      }


      setProfileImage(null); // Clear the selected image after upload

      // Make sure to save the updated profile picture URL in localStorage for persistence
      if (response.data.profile_picture) {
        localStorage.setItem('profilePicture', response.data.profile_picture);
      }


    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Failed to update profile');
    }
  };


  // Helper function to get proper image URL
  const getProfileImageUrl = () => {
    if (editMode && imagePreview) {
      return imagePreview;
    }
    
    // First check if userData has a profile picture
    if (userData?.profile_picture) {
      let picturePath = userData.profile_picture;
      
      // If the path doesn't start with 'http' or '/', add a leading slash
      if (!picturePath.startsWith('http') && !picturePath.startsWith('/')) {
        picturePath = `/${picturePath}`;
      }
      
      // Check if the path is a relative path that needs the API_URL
      if (!picturePath.startsWith('http')) {
        return `${API_URL}${picturePath}`;
      }
      
      return picturePath;
    }
    
    // Check if we have a saved profile picture in localStorage as fallback
    const savedPicture = localStorage.getItem('profilePicture');
    if (savedPicture) {
      if (!savedPicture.startsWith('http') && !savedPicture.startsWith('/')) {
        return `${API_URL}/${savedPicture}`;
      }
      return savedPicture.startsWith('http') ? savedPicture : `${API_URL}${savedPicture}`;
    }
    
    // Use our custom default picture instead of placeholder
    return `${API_URL}${DEFAULT_PROFILE_PIC}`;
  };

  // Handle cancel with preview cleanup
  const handleCancel = () => {
    setEditMode(false);
    // Clean up preview URL when canceling
    if (imagePreview) {
      URL.revokeObjectURL(imagePreview);
      setImagePreview(null);
    }
    setProfileImage(null);
  };

  // ============================
  // Render Profile UI
  // ============================

  return (
    <div className="profile-container">
      {/* Profile Title */}
      <h1 className="profile-title">Player Profile</h1>

      <div className="profile-header">
        {/* Display profile image */}
        <img
          src={getProfileImageUrl()}
          alt="Profile"
          className="profile-image"
          onError={(e) => {
            console.error('Image load error, falling back to alternative path');

            // Try an alternative path format if the main one fails
            // This handles the case where the server might be storing paths differently
            const userData = e.target.dataset.userData || '';
            if (userData && userData.profile_picture) {
              // Try with /media/ prefix if the regular path failed
              if (userData.profile_picture.includes('profile_pics') && !userData.profile_picture.includes('/media/')) {
                e.target.src = `${API_URL}/media/${userData.profile_picture}`;
                return;
              }
              
              // Try with /ECM2434_v2/media/ prefix based on your path info
              if (!userData.profile_picture.includes('ECM2434_v2/media/')) {
                e.target.src = `${API_URL}/ECM2434_v2/media/${userData.profile_picture.split('/').pop()}`;
                return;
              }
            }
            
            // Final fallback to placeholder
            e.target.src = `${API_URL}${DEFAULT_PROFILE_PIC}`;

            e.target.onerror = () => {
              e.target.src = 'https://via.placeholder.com/150';
              e.target.onerror = null; // Prevent infinite loop
            };
          }}
          data-userData={JSON.stringify(userData)} // Pass userData to the error handler
        />

        {/* Profile Info - View or Edit Mode */}
        {!editMode ? (
          <div className="profile-details">
            <h2>{userData?.username}</h2>
            <p><strong>Email:</strong> {userData?.email || 'N/A'}</p>
            <p><strong>Rank:</strong> {userData?.rank || 'Unranked'}</p>
            <p><strong>Total Points:</strong> {userData?.total_points || 0}</p>
            <p><strong>Completed Tasks:</strong> {userData?.completed_tasks || 0}</p>
            <button className="edit-profile-btn" onClick={() => setEditMode(true)}>Edit Profile</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="edit-profile-form">
            <input type="text" name="username" value={updatedUser.username} onChange={handleInputChange} placeholder="Enter your username"/>
            <input type="email" name="email" value={updatedUser.email} onChange={handleInputChange} placeholder="Email"/>
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <button type="submit">Save Changes</button>
            <button type="button" onClick={() => setEditMode(false)}>Cancel</button>
          </form>
        )}
      </div>

      {/* Completed Tasks Section */}
      <div className="completed-tasks">
        <h3>Completed Bingo Tasks</h3>
        {tasks.length > 0 ? (
          <ul>
            {tasks.map(task => (
              <li key={task.id}>{task.description}</li>
            ))}
          </ul>
        ) : (
          <p>No completed tasks yet.</p>
        )}
      </div>

      {/* Navigation Buttons */}
      <div className="buttons">
        <button onClick={() => navigate('/bingo')}>Go to Bingo Board</button>
        <button onClick={() => navigate('/leaderboard')}>View Leaderboard</button>
        <button onClick={() => { 
          localStorage.removeItem('accessToken'); 
          localStorage.removeItem('profilePicture'); // Also clear the profile picture from localStorage
          navigate('/login'); 
        }}>Logout</button>
      </div>
    </div>
  );
};

export default Profile;