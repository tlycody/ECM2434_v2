// ============================
// User Profile Component with Badges
// ============================

import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';

// Fetch API URL from environment variables (fallback to localhost if not set)
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Profile = () => {
  // State variables for user data, completed tasks, edit mode, and profile image
  const [userData, setUserData] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [badges, setBadges] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [updatedUser, setUpdatedUser] = useState({});
  const [profileImage, setProfileImage] = useState(null);
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
        setUserData(response.data);
        setUpdatedUser(response.data);
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    // Debug fetch to directly get task data
    const debugFetch = async () => {
      try {
        // Get direct API data for debugging
        const response = await axios.get(`${API_URL}/api/debug-tasks/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });
        console.log('Debug task data from API:', response.data);
      } catch (error) {
        console.error('Error in debug fetch:', error);
      }
    };

    // Fetch tasks for display in the list
    const fetchCompletedTasks = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/tasks/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });
    
        // Log the response to debug
        console.log('All tasks data:', response.data);
        
        // Filter tasks that are completed or approved
        const completedTasks = response.data.filter(task => 
          task.status === 'completed' || 
          task.status === 'approved' || 
          task.completed === true
        );
        
        console.log('Filtered completed tasks:', completedTasks);
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
    debugFetch(); // Add this to get extra debug information
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
    setProfileImage(e.target.files[0]);
  };

  // ============================
  // Badge Emoji Selector
  // ============================
  
  const getBadgeEmoji = (type) => {
    switch (type) {
      case 'O':
        return '♻️'; // Recycling symbol for Zero Waste Hero
      case 'X':
        return '❌'; // X for Climate Action Influencer
      case 'H':
        return '🌈'; // Rainbow for Eco Horizon Pioneer
      case 'V':
        return '🌱'; // Seedling for Green Growth Champion
      default:
        return '🏆';
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

      alert('Profile updated successfully');
      setEditMode(false);

      // Update state with new profile data
      setUserData(response.data);
      setProfileImage(null); // Clear the selected image after upload
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Failed to update profile');
    }
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
          src={userData?.profile_picture ? `${API_URL}${userData.profile_picture}` : 'https://via.placeholder.com/150'}
          alt="Profile"
          className="profile-image"
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

      {/* Sustainability Badges Section */}
      <div className="sustainability-badges">
        <h3>Sustainability Badges</h3>
        {badges.length > 0 ? (
          <div className="badges-grid">
            {badges.map(badge => (
              <div key={badge.id} className="badge-item">
                <div className="badge-emoji">{getBadgeEmoji(badge.type)}</div>
                <div className="badge-info">
                  <h4>{badge.name}</h4>
                  <p className="badge-points">+{badge.bonus_points} points</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="badge-hints">
            <p>Complete patterns on your bingo board to earn badges!</p>
            <div className="hint-icons">
              <span className="hint-item">♻️ Zero Waste Hero</span>
              <span className="hint-item">❌ Climate Action Influencer</span>
              <span className="hint-item">🌈 Eco Horizon Pioneer</span>
              <span className="hint-item">🌱 Green Growth Champion</span>
            </div>
          </div>
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
          navigate('/login'); 
        }}>Logout</button>
      </div>
    </div>
  );
};

export default Profile;