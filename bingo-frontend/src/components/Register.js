import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL;

const Register = () => {
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [passwordagain, setPasswordagain] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== passwordagain) {
      setError('Passwords do not match!');
      return;
    }

    try{
      console.log("Attempting to register user with:",
      {
        username,
        email,
        password,
        passwordagain
      });

      const response = await axios.post('http://localhost:8000/api/register_user/',
      {
        username,
        email,
        password,
        passwordagain,
      }, {
        headers: {
          'Content-Type': 'application/json',
        },
      });
    
      if (response.data.access){
        localStorage.setItem('access_token',response.data.access);
        localStorage.setItem('refresh_token',response.data.refresh);
        navigate('/login')
    }
  } catch (error) {
      console.error('Full error object',error);
      console.error('Response data:', error.response?.data);
      console.error('Response status:', error.response?.status);

      if (error.response && error.response.data && error.response.data.detail) {
        setError(error.response.data.detail);  // Show the specific error message
      } else if (error.response) {
        setError("An error occurred during registration.");  // Default error response
      } else {
        setError(`Network error occurred: ${error.message}`);
      }
    }
  };

  return (
    <div className="register-container">
      <h2>Register</h2>
      {error && <p>{error}</p>}
      <form onSubmit={handleRegister}>
        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <input type="email" placeholder="university email" value={email} onChange={(e) => setEmail(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <input type="password" placeholder="Confirm Password" value={passwordagain} onChange={(e) => setPasswordagain(e.target.value)} required />
        <button type="submit">Register</button>
      </form>
    </div>
  );
};

export default Register;