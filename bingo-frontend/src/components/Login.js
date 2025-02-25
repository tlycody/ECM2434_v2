import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import './Login.css';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Login = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    profile: 'Player',
    extraPassword: '',
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

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
      extraPassword: value === 'Player' ? '' : prev.extraPassword,
    }));
  };

  const validateForm = () => {
    if (!formData.username.trim()) return 'Username is required';
    if (!formData.password) return 'Password is required';
    if (formData.profile === 'Game Keeper' && !formData.extraPassword) {
      return 'Special password required for Game Keeper';
    }
    if (formData.profile === 'Developer' && !formData.extraPassword) {
      return 'Special password required for Developer';
    }
    return null;
  };

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

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
          extraPassword: formData.extraPassword,
        }),
      });

      const text = await response.text();
      console.log("Raw response:", text);
      const data = JSON.parse(text);

      if (!response.ok) {
        throw new Error(data.detail || data.error || 'Login failed');
      }

      // Store tokens and navigate
      localStorage.setItem('accessToken', data.access);
      localStorage.setItem('refreshToken', data.refresh);
      localStorage.setItem('userProfile', formData.profile);
      localStorage.setItem('username', data.user);

      if (formData.profile === 'Developer') {
        // Redirect to developer dashboard
        window.location.href = '/developer-front.html';
      } else {
        // Normal user navigation
        navigate('/userprofile');
      }
    } catch (err) {
      console.error('Login error:', err);
      setError(err.message || 'An error occurred during login');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleLogin}>
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
        <div className="form-group">
          <select name="profile" value={formData.profile} onChange={handleProfileChange} required>
            <option value="Player">Player</option>
            <option value="Game Keeper">Game Keeper</option>
            <option value="Developer">Developer</option>
          </select>
        </div>
        {(formData.profile === 'Game Keeper' || formData.profile === 'Developer') && (
          <div className="form-group">
            <input
              type="password"
              placeholder="Special Password"
              name="extraPassword"
              value={formData.extraPassword}
              onChange={handleChange}
              required
            />
          </div>
        )}
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      <p>
        Don't have an account? <Link to="/register">Register Here!</Link>
      </p>
    </div>
  );
};

export default Login;