import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL || "http://localhost:8000";

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    passwordagain: '',
    gdprConsent: false,
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const validateForm = () => {
    if (!formData.username.trim()) return 'Username is required';
    if (!formData.email.trim()) return 'Email is required';
    if (!formData.email.endsWith('@exeter.ac.uk')) return 'Please use your @exeter.ac.uk email';
    if (!formData.password) return 'Password is required';
    if (!formData.gdprConsent) return "You need to accept the Privacy Policy to register";
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
      const response = await fetch(`${API_URL}/api/register/`, {  // ✅ Fixed API URL
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        const text = await response.text();
        console.log("Raw response:", text);
        const data = JSON.parse(text);

        if (response.ok) {
            navigate('/login');
        } else {
            throw new Error(data.detail || data.error || 'Registration failed');
        }
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
        <div className="form-group privacy-policy">
          <label className="checkbox-label">
            <input
              type="checkbox"
              name="gdprConsent"
              checked={formData.gdprConsent}
              onChange={handleChange}
              required
            />
            I have read and agree to the <Link to="/privacy-policy" target="_blank">Privacy Policy</Link>
          </label>
        </div>
        <button type="submit" disabled={loading}>
          {loading ? 'Registering...' : 'Register'}
        </button>
      </form>
    </div>
  );
};

export default Register;
