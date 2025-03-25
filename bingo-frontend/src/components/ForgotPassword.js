// Forgot Password Component

import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import './Login.css'; 

const API_URL = "https://ecm2434-v3.onrender.com";

// For debugging
console.log("Using API URL:", API_URL);

const ForgotPassword = () => {
  // State variables for form data, error/success messages, and loading status
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Handle Input Changes

  const handleEmailChange = (e) => {
    setEmail(e.target.value);
    // Clear any previous messages when input changes
    setError('');
    setSuccess('');
  };

  // Validate Form Inputs

  const validateForm = () => {
    if (!email.trim()) return 'Email is required';

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) return 'Please enter a valid email address';

    return null; // No errors
  };

  // Handle Password Reset Request

  const handleResetRequest = async (e) => {
    e.preventDefault();
    setError('');
    setSuccess('');
    setLoading(true);

    // Validate input fields before sending the request
    const validationError = validateForm();
    if (validationError) {
      setError(validationError);
      setLoading(false);
      return;
    }

    // For debugging
    console.log("Sending request to:", `${API_URL}/api/password-reset/`);
    console.log("With data:", { email });

    try {
      // Make sure the URL structure matches your Django URL configuration
      const response = await fetch(`${API_URL}/api/password-reset/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: email,
        }),
      });

      // For debugging
      console.log("Response status:", response.status);

      if (!response.ok) {
        const errorData = await response.json();
        console.log("Error data:", errorData);
        throw new Error(errorData.detail || errorData.error || 'Request failed');
      }

      const data = await response.json();
      console.log("Success response:", data);

      // Show success message
      setSuccess('Password reset link has been sent to your email. Please check your inbox.');

      // Clear the form
      setEmail('');

    } catch (err) {
      console.error('Password reset error:', err);
      setError(err.message || 'An error occurred while processing your request');
    } finally {
      setLoading(false);
    }
  };

  // Render Password Reset UI

  return (
    <div className="login-container">
      {/* Page Title */}
      <h2>Forgot Password</h2>

      {/* Error Message Display */}
      {error && <div className="error-message">{error}</div>}

      {/* Success Message Display */}
      {success && <div className="success-message">{success}</div>}

      {/* Password Reset Form */}
      <form onSubmit={handleResetRequest}>
        {/* Email Input */}
        <div className="form-group">
          <input
            type="email"
            placeholder="Email address"
            name="email"
            value={email}
            onChange={handleEmailChange}
            required
          />
        </div>

        {/* Submit Button */}
        <button type="submit" disabled={loading}>
          {loading ? 'Processing...' : 'Send Reset Link'}
        </button>

        {/* Back to Login Button */}
        <button type="button" onClick={() => navigate('/login')} className="secondary-button">
          Back to Login
        </button>
      </form>
    </div>
  );
};

export default ForgotPassword;