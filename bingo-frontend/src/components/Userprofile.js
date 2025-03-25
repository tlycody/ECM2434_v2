import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';

// Fetch API URL from environment variables (fallback to localhost if not set)
const API_URL = "https://ecm2434-v3.onrender.com";

// Default profile picture path with the correct filename
const DEFAULT_PROFILE_PIC = "/media/profile_pics/default.png";

const Profile = () => {
  // State variables for user data, completed tasks, edit mode, and profile image
  const [userData, setUserData] = useState(null);
  const [/*tasks,*/ setTasks] = useState([]);
  const [badges, setBadges] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [updatedUser, setUpdatedUser] = useState({});
  const [profileImage, setProfileImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const navigate = useNavigate(); // React Router navigation hook

   // Fetch User Data, Completed Tasks & Badges
 
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
      
      // Set badges directly from the profile response
      if (response.data.badges) {
        console.log('Badges from profile:', response.data.badges);
        setBadges(response.data.badges);
      }
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



    fetchUserData();
    fetchCompletedTasks();

  }, []);

   // Handle Input & File Changes
 
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

   // Handle Profile Update
 
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

   // Handle Profile Deletion
   
  const handleDeleteProfile = async () => {
    try {
      // First, try to see what API endpoints are available by checking profile data
      console.log('Checking available endpoints in userData:', userData);
      
      // Option 1: Try standard DELETE method first
      try {
        console.log('Attempting DELETE to /api/profile/');
        const response = await axios.delete(`${API_URL}/api/profile/`, {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
          },
        });
        
        console.log('Profile deletion response:', response.data);
        
        localStorage.clear();
        alert('Your profile has been successfully deleted');
        window.location.href = '/login';
        return;
      } catch (deleteError) {
        console.error('DELETE method failed:', deleteError);
        // Continue to alternative methods if DELETE fails
      }
      
      // Option 2: Try using the update endpoint with a "delete" flag
      // This is a common pattern when DELETE endpoints aren't implemented
      console.log('Attempting PUT to /api/profile/update/ with delete flag');
      const updateResponse = await axios.put(
        `${API_URL}/api/profile/update/`,
        { is_deleted: true, delete_account: true },
        {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
            'Content-Type': 'application/json',
          },
        }
      );
      
      console.log('Profile update (delete) response:', updateResponse.data);
      
      // Clear ALL local storage items
      localStorage.clear();
      
      // Show success message
      alert('Your profile has been successfully deleted');
      
      // Force redirect to login page
      window.location.href = '/login';
    } catch (error) {
      console.error('All profile deletion attempts failed:', error);
      
      // Try one more approach - logout and show instructions
      try {
        localStorage.clear();
        alert('We could not delete your profile automatically. Please contact support to complete the deletion.');
        window.location.href = '/login';
      } catch (finalError) {
        console.error('Final attempt failed:', finalError);
        alert('Could not process your request. Please try again later or contact support.');
        setShowDeleteConfirm(false);
      }
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


  const getBadgeEmoji = (badgeType) => {
    console.log("Badge type:", badgeType);
    
    switch(badgeType) {
      case 'O': return '♻️';
      case 'X': return '💚';
      case 'H': return '🌈';
      case 'V': return '🌱';
      default: return '🏆';
    }
  };

  const getBadgeTypeName = (badgeType) => {
    switch(badgeType) {
      case 'O': return 'Ozone defender';
      case 'X': return 'Xtra Green';
      case 'H': return 'Healthy Hero';
      case 'V': return 'Green Champion';
      default: return 'Achievement Badge';
    }
  };

   // Render Profile UI
 
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
                        {/* User Badges Section */}
                        <div className="user-badges">
  <p><strong>Earned Badges:</strong></p>
  {badges && badges.length > 0 ? (
  <div className="badges-grid">
    {badges.map(badge => (
      <div key={badge.id || badge.name} className="badge-item">
        <div className="badge-emoji">
          {getBadgeEmoji(badge.type)}
        </div>
        <div className="badge-name">
          {getBadgeTypeName(badge.type)}
        </div>
      </div>
    ))}
  </div>
) : (
  <p>No badges earned yet. Complete patterns on your bingo board to earn badges!</p>
)}
</div>
            <button className="edit-profile-btn" onClick={() => setEditMode(true)}>Edit Profile</button>
            <button className="delete-profile-btn" onClick={() => setShowDeleteConfirm(true)}>Delete Profile</button>
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

      {/* Navigation Buttons */}
      <div className="buttons">
        <button onClick={() => navigate('/bingo')}>Go to Bingo Board</button>
        {/* Replace the single leaderboard button with two specific buttons */}
        <button onClick={() => navigate('/leaderboard?type=lifetime')}>
          🏆 Lifetime Leaderboard
        </button>
        <button onClick={() => navigate('/leaderboard?type=monthly')}>
          📅 Monthly Leaderboard
        </button>
        <button onClick={() => { 
          localStorage.removeItem('accessToken'); 
          localStorage.removeItem('profilePicture'); // Also clear the profile picture from localStorage
          navigate('/login'); 
        }}>Logout</button>
      </div>

      {/* Delete Confirmation Dialog */}
      {showDeleteConfirm && (
        <div className="delete-confirmation-overlay">
          <div className="delete-confirmation-dialog">
            <h3>Delete Your Profile?</h3>
            <p>This action cannot be undone. All your data will be permanently removed.</p>
            <div className="delete-confirmation-buttons">
              <button 
                className="delete-confirm-btn"
                onClick={handleDeleteProfile}
              >
                Yes, Delete My Profile
              </button>
              <button 
                className="delete-cancel-btn"
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}

    </div>
  );
};

export default Profile;