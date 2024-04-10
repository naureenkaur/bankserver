import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import Cookies from 'universal-cookie';

// Ensure your CSS file is correctly linked
import "./SignIn.css";

const SignIn = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      console.log('Redirecting to homepage...');
      navigate("/Transactions");
    }
  }, [isAuthenticated, navigate]);

  const onLoginButtonClick = async (e) => {
    e.preventDefault(); // Prevent the default form submission behavior

    const jsonData = { email, password };
    console.log('Attempting to log in with:', jsonData);

    try {
      const response = await fetch("http://localhost:8000/api/login", {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jsonData),
      });

      const data = await response.json();

      if (response.ok && data.token) {
        const cookies = new Cookies();
        cookies.set('jwt', data.token, { path: '/' });
        setIsAuthenticated(true); // Set isAuthenticated to true upon successful login
      } else {
        console.error('Login failed:', data);
        setErrorMessage(data.message || 'Invalid email or password.');
      }
    } catch (error) {
      console.error('Error during sign in:', error);
      setErrorMessage('Error during sign in. Please try again.');
    }
  };

  return (
    <div className="form-container">
      <form className="signin-form" onSubmit={onLoginButtonClick}>
        <h2 className="form-title text-center">SIGN IN</h2>
        {errorMessage && <div className="error-message">{errorMessage}</div>}
        <input
          className="form-input"
          type="UserID"
          name="USER ID"
          placeholder="User ID"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
        />
        <input
          className="form-input"
          type="password"
          name="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button className="form-button" type="submit">Login</button>
      </form>
    </div>
  );
};

export default SignIn;