import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "universal-cookie";
import "./SignIn.css";

const SignIn = () => {
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [errorMessage, setErrorMessage] = useState("");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      console.log("Redirecting to homepage...");
      navigate("/Transactions");
    }
  }, [isAuthenticated, navigate]);

  async function hashPassword(password) {
    const encoder = new TextEncoder();
    const data = encoder.encode(password); // Converts password to a Uint8Array
    const hashBuffer = await crypto.subtle.digest('SHA-256', data); // Hashes the data
    const hashArray = Array.from(new Uint8Array(hashBuffer)); // Converts hash to byte array
    const hashHex = hashArray.map(b => b.toString(16).padStart(2, '0')).join(''); // Converts bytes to hex string
    return hashHex;
  };


  const onLoginButtonClick = async (e) => {
    e.preventDefault(); // Prevent the default form submission behavior

    const jsonData = { username, password }; // Send plaintext password
    console.log("Attempting to log in with:", jsonData);

    try {
      const response = await fetch("http://127.0.0.1:5000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonData),
      });

      const data = await response.json();
      console.log("Login response:", data);

      if (response.ok && data.authenticated) {
        const cookies = new Cookies();
        cookies.set("jwt", data.token, { path: "/" });
        setIsAuthenticated(true); // Set isAuthenticated to true upon successful login
        sessionStorage.setItem("username", username);
        sessionStorage.setItem("authenticated", true);
        navigate("/Transactions"); // Redirect after login
      } else {
        console.error("Login failed:", data);
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
          type="UserID"
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
        <button className="form-button" type="submit">
          Login
        </button>
      </form>
    </div>
  );
};

export default SignIn;
