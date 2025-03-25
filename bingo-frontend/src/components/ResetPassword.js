 
// Reset Password Component
 

import React, { useState, useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import './Login.css'; // Reusing the login styles

// Fetch API URL from environment variables (fallback to localhost if not set)
const API_URL = process.env.REACT_APP_API_URL;

const ResetPassword = () => {
  // Get token from URL params
  const { token } = useParams();

  // State variables for form data, error/success messages, and loading status
  const [formData, setFormData] = useState({
    password: '',
    confirmPassword: '',
  });
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  // Redirect if no token is provided
  useEffect(() => {
    if (!token) {
      navigate('/forgot-password');
    }
  }, [token, navigate]);

   
  // Handle Input Changes
   

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }));
    // Clear any previous messages when input changes
    setError('');
    setSuccess('');
  };

   
  // Validate Form Inputs
   

  const validateForm = () => {
    if (!formData.password) return 'Password is required';
    if (formData.password.length < 8) return 'Password must be at least 8 characters long';
    if (formData.password !== formData.confirmPassword) return 'Passwords do not match';

    return null; // No errors
  };

   
  // Handle Reset Password Submission
   

  const handleResetPassword = async (e) => {
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
    console.log("Sending request to:", `${API_URL}/api/password-reset/confirm/`);
    console.log("With data:", { token, password: formData.password });

    try {
      const response = await fetch(`${API_URL}/api/password-reset/confirm/`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          token: token,
          password: formData.password,
        }),
      });

      // Check if response is OK before trying to parse JSON
      if (!response.ok) {
        // For debugging
        const contentType = response.headers.get("content-type");
        console.log("Response content type:", contentType);

        if (contentType && contentType.includes("application/json")) {
          const errorData = await response.json();
          console.log("Error data:", errorData);
          throw new Error(errorData.detail || errorData.error || 'Password reset failed');
        } else {
          // If not JSON, get text
          const errorText = await response.text();
          console.log("Error response (not JSON):", errorText);
          throw new Error('Server error: Not a valid JSON response');
        }
      }

      // Parse JSON response
      const data = await response.json();
      console.log("Success response:", data);

      // Show success message
      setSuccess('Your password has been reset successfully!');

      // Clear the form
      setFormData({
        password: '',
        confirmPassword: '',
      });

      // Redirect to login after a delay
      setTimeout(() => {
        navigate('/login');
      }, 3000);

    } catch (err) {
      console.error('Password reset error:', err);
      setError(err.message || 'An error occurred while resetting your password');
    } finally {
      setLoading(false);
    }
  };

   
  // Render Reset Password UI
   

  return (
    <div className="login-container">
      {/* Page Title */}
      <h2>Reset Password</h2>

      {/* Error Message Display */}
      {error && <div className="error-message">{error}</div>}

      {/* Success Message Display */}
      {success && <div className="success-message">{success}</div>}

      {/* Reset Password Form */}
      <form onSubmit={handleResetPassword}>
        {/* New Password Input */}
        <div className="form-group">
          <input
            type="password"
            placeholder="New Password"
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
            placeholder="Confirm New Password"
            name="confirmPassword"
            value={formData.confirmPassword}
            onChange={handleChange}
            required
          />
        </div>

        {/* Submit Button */}
        <button type="submit" disabled={loading || success}>
          {loading ? 'Processing...' : 'Reset Password'}
        </button>

        {/* Back to Login Button */}
        <button type="button" onClick={() => navigate('/login')} className="secondary-button">
          Back to Login
        </button>
      </form>
    </div>
  );
};

export default ResetPassword;