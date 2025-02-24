import React, { useEffect, useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import './UserProfile.css';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Profile = () => {
  const [userData, setUserData] = useState(null);
  const [tasks, setTasks] = useState([]);
  const [editMode, setEditMode] = useState(false);
  const [updatedUser, setUpdatedUser] = useState({});
  const [profileImage, setProfileImage] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const fetchUserData = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/profile/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });
        setUserData(response.data);
        setUpdatedUser(response.data);
      } catch (error) {
        console.error('Error fetching user data:', error);
      }
    };

    const fetchCompletedTasks = async () => {
      try {
        const response = await axios.get(`${API_URL}/api/tasks/`, {
          headers: { Authorization: `Bearer ${localStorage.getItem('accessToken')}` },
        });
        setTasks(response.data);
      } catch (error) {
        console.error('Error fetching completed tasks:', error);
      }
    };

    fetchUserData();
    fetchCompletedTasks();
  }, []);

  const handleInputChange = (e) => {
    setUpdatedUser({ ...updatedUser, [e.target.name]: e.target.value });
  };

  const handleFileChange = (e) => {
    setProfileImage(e.target.files[0]);
  };

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
      await axios.put(`${API_URL}/api/profile/update/`, formData, {
        headers: {
          Authorization: `Bearer ${localStorage.getItem('accessToken')}`,
          'Content-Type': 'multipart/form-data',
        },
      });
      alert('Profile updated successfully');
      setEditMode(false);
      setUserData(updatedUser);
    } catch (error) {
      console.error('Error updating profile:', error);
      alert('Failed to update profile');
    }
  };

  return (
    <div className="profile-container">
      <h1 className="profile-title">Player Profile</h1>
      <div className="profile-header">
        <img
          src={userData?.profile_picture || 'https://via.placeholder.com/150'}
          alt="Profile"
          className="profile-image"
        />

        {!editMode ? (
          <div className="profile-details">
            <h2>{userData?.username}</h2>
            <p><strong>Email:</strong> {userData?.email || 'N/A'}</p>
            <p><strong>Rank:</strong> {userData?.rank || 'Unranked'}</p>
            <p><strong>Total Points:</strong> {userData?.total_points || 0}</p>
            <p><strong>Completed Tasks:</strong> {tasks.length}</p>
            <button onClick={() => setEditMode(true)}>Edit Profile</button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="edit-profile-form">
            <input type="text" name="username" value={updatedUser.username} onChange={handleInputChange} />
            <input type="email" name="email" value={updatedUser.email} onChange={handleInputChange} />
            <input type="file" accept="image/*" onChange={handleFileChange} />
            <button type="submit">Save Changes</button>
            <button type="button" onClick={() => setEditMode(false)}>Cancel</button>
          </form>
        )}
      </div>

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

      <div className="buttons">
        <button onClick={() => navigate('/bingo')}>Back to Bingo Board</button>
        <button onClick={() => navigate('/leaderboard')}>View Leaderboard</button>
        <button onClick={() => { localStorage.removeItem('token'); navigate('/login'); }}>Logout</button>
      </div>
    </div>
  );
};

export default Profile;
