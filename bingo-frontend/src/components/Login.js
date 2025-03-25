// Login Component

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css';

const API_URL = process.env.REACT_APP_API_URL;

const Login = () => {
  // State variables for form data, error messages, and loading status
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    profile: 'Player', 
    
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); 

  // Handle Input Changes

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value, 
    }));
  };

  const handleProfileChange = (e) => {
    const { value } = e.target;
    setFormData((prev) => ({
      ...prev,
      profile: value, 
      extraPassword: value === 'Player' ? '' : prev.extraPassword, // Clear special password if switching back to Player
    }));
  };

  // Validate Form Inputs

  const validateForm = () => {
    if (!formData.username.trim()) return 'Username is required';
    if (!formData.password) return 'Password is required';
    
    return null; // No errors
  };

  // Handle Login Submission

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validate input fields before sending the request
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      setLoading(false);
      return;
    }

    try {
      const response = await fetch(`${API_URL}/api/login/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password,
          profile: formData.profile,
          // extraPassword: formData.extraPassword,
        }),
      });

      const text = await response.text(); 
      console.log("Raw response:", text);
      const data = JSON.parse(text); // Convert response to JSON


      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Login failed');
      }

      // Store authentication tokens in localStorage
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('userProfile', formData.profile);
      localStorage.setItem('username', data.user);

      // Redirect based on user role
      if (formData.profile === 'Developer') {
        window.location.href = '/developer-front.html'; 
      } else if (formData.profile === 'GameKeeper') {
        window.location.href = '/gamekeeper';
      } else {
        navigate('/userprofile');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'An error occurred during login'); // Show error message
    } finally {
      setLoading(false);
    }
  };

  // Render Login UI

  return (
    <div className="login-container">
      {/* Page Title */}
      <h2>Login</h2>

      {/* Error Message Display */}
      {error && <div className="error-message">{error}</div>}

      {/* Login Form */}
      <form onSubmit={handleLogin}>
        {/* Username Input */}
        <div className="form-group">
          <input
            type="text"
            placeholder="Username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            required
          />
        </div>

        {/* Password Input */}
        <div className="form-group">
          <input
            type="password"
            placeholder="Password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            required
          />
        </div>

        {/* Profile Selection Dropdown */}
        <div className="form-group">
          <select name="profile" value={formData.profile} onChange={handleProfileChange} required>
            <option value="Player">Player</option>
            <option value="GameKeeper">Game Keeper</option> 
            <option value="Developer">Developer</option>
          </select>
        </div>

        {/* Forgot Password Link */}
        <div className="forgot-password-link">
          <Link to="/forgot-password">Forgot Password?</Link>
        </div>

        {/* Login Button */}
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>

        {/* Home Button */}
        <button type="button" onClick={() => navigate('/')} className="secondary-button">
          Home
        </button>
      </form>

      {/* Redirect to Registration */}
      <p>
        Don't have an account? <Link to="/register">Register Here!</Link>
      </p>
    </div>
  );
};

export default Login;