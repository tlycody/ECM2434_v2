// ============================
// Register Component
// ============================

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Register.css';

// Fetch API URL from environment variables (fallback to localhost if not set)
const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Register = () => {
  // State variables for form data, errors, and loading status
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordagain: '',
    gdprConsent: false, // GDPR consent must be explicitly checked
  });

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate(); // React Router navigation hook

  // ============================
  // Handle Input Changes
  // ============================

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value, // Handle checkboxes separately
    }));
  };

  // ============================
  // Validate Form Inputs
  // ============================

  const validateForm = () => {
    if (!formData.username.trim()) return 'Username is required';
    if (!formData.email.trim()) return 'Email is required';
    if (!formData.password) return 'Password is required';
    if (formData.password !== formData.passwordagain) return 'Passwords do not match';
    if (!formData.gdprConsent) return "You need to accept the Privacy Policy to register";
    return null; // ✅ No errors
  };

  // ============================
  // Handle Form Submission
  // ============================

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    setLoading(true);

    // Validate form fields before making the API call
    const validationError = validateForm();
    if (validationError) {
        setError(validationError);
        setLoading(false);
        return;
    }

    try {
      const response = await fetch(`${API_URL}/api/register/`, {  // ✅ API call to register
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const text = await response.text(); // Handle text responses
        console.log("Raw response:", text);
        const data = JSON.parse(text); // Convert response to JSON

        if (response.ok) {
            navigate('/login'); // ✅ Redirect to login on successful registration
        } else {
            throw new Error(data.detail || data.error || 'Registration failed');
        }
    } catch (err) {
        console.error('Registration error:', err);
        setError(err.message || 'An error occurred during registration'); // ✅ Show error message
    } finally {
        setLoading(false);
    }
  };

  // ============================
  // Render Registration Form UI
  // ============================

  return (
    <div className="register-container">
      {/* Page Title */}
      <h2>Register</h2>

      {/* Error Message Display */}
      {error && <div className="error-message">{error}</div>}

      {/* Registration Form */}
      <form onSubmit={handleSubmit}>
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

        {/* University Email Input */}
        <div className="form-group">
          <input
            type="email"
            placeholder="Email address"
            name="email"
            value={formData.email}
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

        {/* Confirm Password Input */}
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

        {/* GDPR Consent Checkbox */}
        <div className="form-group privacy-policy">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="gdprConsent"
              checked={formData.gdprConsent}
              onChange={handleChange}
              required
            />
            I have read and agree to the&nbsp;
            <Link to="/privacy-policy" target="_blank">Privacy Policy</Link>
          </label>
        </div>

        {/* Register Button */}
        <button type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
    </div>
  );
};

export default Register;
