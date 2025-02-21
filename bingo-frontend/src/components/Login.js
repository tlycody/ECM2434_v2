import React, { useState } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const API_URL = process.env.REACT_APP_API_URL;

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();
    setError('');

    try {
      const response = await axios.post('http://localhost:8000/api/login/', { username, password });

      if(response.data.access){
        localStorage.setItem('access_token', response.data.access);
        localStorage.setItem('refresh_token',response.data.refresh);
        localStorage.setItem('user',response.data.user)
        navigate('/userprofile')
      }
    }catch (err) {
      const errorMessage = err.response?.data?.error || 'Invalid username or password';
      setError(errorMessage);
      console.error('Login error:', err.response?.data); 
    }
  }

  return (
    <div className="login-container">
      <h2>Login</h2>
      {error && <p>{error}</p>}
      <form onSubmit={handleLogin}>
        <input type="text" placeholder="Username" value={username} onChange={(e) => setUsername(e.target.value)} required />
        <input type="password" placeholder="Password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        <button type="submit">Login</button>
      </form>
      <p>Don't have an account?<a href ="/register">Register Here!</a></p>
    </div>
  );
};

export default Login;