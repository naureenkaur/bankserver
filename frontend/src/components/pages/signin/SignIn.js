import React, { useState, useEffect } from "react";
import { json, useNavigate } from "react-router-dom";
import CryptoJS from 'crypto-js';


const SignIn = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      navigate("/Transactions");
    }
  }, [isAuthenticated, navigate]);

  async function fetchSalt(username) {
    const response = await fetch(`http://127.0.0.1:5000/get_salt?username=${username}`);
    if (response.ok) {
      const data = await response.json();
      return data.salt; // Assuming the backend sends the salt encoded in base64
    }
    return null;
  }

  async function hashPassword(password, salt) {
    const saltBytes = Uint8Array.from(atob(salt), c => c.charCodeAt(0));
    const passwordBuffer = new TextEncoder().encode(password);
    const keyMaterial = await window.crypto.subtle.importKey(
      "raw",
      passwordBuffer,
      { name: "PBKDF2" },
      false,
      ["deriveBits"]
    );
    const key = await window.crypto.subtle.deriveBits(
      {
        name: "PBKDF2",
        salt: saltBytes,
        iterations: 100000,
        hash: "SHA-256",
      },
      keyMaterial,
      256
    );
    const hash = btoa(String.fromCharCode(...new Uint8Array(key)));
    return hash;
  }

  const generateHMAC = (data, key) => {
    if (!data || !key) {
        console.error("Invalid input to HMAC generation function.");
        return null; // or handle this scenario appropriately
    }
    return CryptoJS.HmacSHA256(data, key).toString();
};



const onLoginButtonClick = async (e) => {
  e.preventDefault();
  const salt = await fetchSalt(username);
  if (!salt) {
      setErrorMessage("Failed to retrieve user salt.");
      return;
  }
  
  const hashedPassword = await hashPassword(password, salt);
  if (!hashedPassword) {
      setErrorMessage("Password hashing failed.");
      return;
  }

  const hmacKey = 'your_hmac_key_here'; // This should be securely managed and not undefined
  if (!hmacKey) {
      setErrorMessage("HMAC key is not set.");
      return;
  }
  const mac = generateHMAC(hashedPassword, hmacKey);

  try {
      const response = await fetch("http://127.0.0.1:5000/login", {
          method: "POST",
          headers: {
              "Content-Type": "application/json",
          },
          body: JSON.stringify({ username, password: hashedPassword, mac }),
      });

      const data = await response.json();
      if (response.ok && data.authenticated) {
        console.log('Login successful, navigating to transactions...');
        navigate("/transactions");
        console.log('Navigation should have been executed');      
      } else {
          setErrorMessage(data.message || "Invalid username or password.");
      }
  } catch (error) {
      console.error("Error during sign in:", error);
      setErrorMessage("Error during sign in. Please try again.");
  }
};



  return (
    <div className="form-container">
      <form className="signin-form" onSubmit={onLoginButtonClick}>
        <h2 className="form-title text-center">SIGN IN</h2>
        {errorMessage && <div className="error-message">{errorMessage}</div>}
        <input
          className="form-input"
          type="text"
          name="USER ID"
          placeholder="User ID"
          value={username}
          onChange={(e) => setUsername(e.target.value)}
        />
        <input
          className="form-input"
          type="password"
          name="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
        />
        <button className="form-button" type="submit" onClick={onLoginButtonClick}>
          Login
        </button>
      </form>
    </div>
  );
};

export default SignIn;
