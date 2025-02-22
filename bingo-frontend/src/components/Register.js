import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordagain: '',
    profile: 'Player',
    extraPassword: ''  
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
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
    if (!formData.email.trim()) return 'Email is required';
    if (!formData.email.endsWith('@exeter.ac.uk')) return 'Please use your @exeter.ac.uk email';
    if (!formData.password) return 'Password is required';
    if (formData.password !== formData.passwordagain) return 'Passwords do not match. Please enter again';
    if (['Game Keeper', 'Developer'].includes(formData.profile) && !formData.extraPassword) {
      return `Special password required for ${formData.profile}`;
    }
    return null;
  };

  const handleSubmit = async (e) => {
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
        console.log('Sending request to:', `${API_URL}/register_user/`); // Debug log
        console.log('Request body:', JSON.stringify(formData)); // Debug log

        const response = await fetch(`${API_URL}/register_user/`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        console.log('Response status:', response.status); // Debug log

        const data = await response.json();
        console.log('Response data:', data); // Debug log

        if (!response.ok) {
            throw new Error(data.detail || data.error || 'Registration failed');
        }

        // Registration successful
        navigate('/login');
    } catch (err) {
        console.error('Registration error:', err);
        setError(err.message || 'An error occurred during registration');
    } finally {
        setLoading(false);
    }
};

  return (
    <div className="register-container">
      <h2>Register</h2>
      {error && <div className="error-message">{error}</div>}
      <form onSubmit={handleSubmit}>
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
            type="email"
            placeholder="University email"
            name="email"
            value={formData.email}
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
          <input
            type="password"
            placeholder="Confirm Password"
            name="passwordagain"
            value={formData.passwordagain}
            onChange={handleChange}
            required
          />
        </div>
        <div className="form-group">
          <select 
            name="profile" 
            value={formData.profile}   
            onChange={handleProfileChange}  
            required
          >
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
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
    </div>
  );
};

export default Register;