import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import Cookies from "universal-cookie";
import "./Transactions.css";

function Transactions() {
  const navigate = useNavigate();
  const [balance, setBalance] = useState(0);
  const [amount, setAmount] = useState("");
  const [showInputAdd, setShowInputAdd] = useState(false);
  const [showInputWithdraw, setShowInputWithdraw] = useState(false);
  const [showBalance, setShowBalance] = useState(false); // New state for showing the balance message

  const username = sessionStorage.getItem("username");

  const handleAction = (type) => {
    if (type === "withdraw") {
      console.log("Withdraw action selected");
      setShowInputWithdraw(true);
      setShowInputAdd(false);
    } else if (type === "add") {
      setShowInputAdd(true);
      setShowInputWithdraw(false);
      console.log("Add action selected");
    }

    // Hide the balance message when adding or withdrawing
    setShowBalance(false);
  };

  const handleChange = (event) => {
    setAmount(event.target.value);
  };

  const handleSubmitAdd = async (e) => {
    e.preventDefault();
    const numberAmount = parseFloat(amount);
    if (!numberAmount) return; // Early return if amount is not a number

    if (showInputAdd && numberAmount > 0) {
      const jsonData = { username, amount: numberAmount };
      const response = await fetch("http://127.0.0.1:5000/add_money", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonData),
      });

      const data = await response.json();

      console.log("Add response:", data);

      if (response.ok) {
        console.log("Add successful");
      } else {
        console.error("Failed to add money:", data.message);
      }
    }

    setAmount("");
    setShowInputAdd(false);
  };

  const handleSubmitWithdraw = async (e) => {
    e.preventDefault();
    const numberAmount = parseFloat(amount);
    if (!numberAmount) return; // Early return if amount is not a number

    if (showInputWithdraw && numberAmount > 0) {
      const jsonData = { username, amount: numberAmount };
      const response = await fetch("http://127.0.0.1:5000/withdraw_money", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(jsonData),
      });

      const data = await response.json();

      console.log("Withdraw response:", data);

      if (response.ok) {
        console.log("Withdraw successful");
      } else {
        console.error("Failed to withdraw money:", data.message);
      }
    }

    setAmount("");
    setShowInputWithdraw(false);
  };

  const handleBalance = async () => {
    // Toggle the balance message display
    const jsonData = { username };
    const response = await fetch("http://127.0.0.1:5000/view_balance", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify(jsonData),
    });

    const data = await response.json();

    console.log("Login response:", data);

    if (response.ok) {
      setBalance(data.balance);
    } else {
      console.error("Failed to view balance:", data.message);
    }

    setShowBalance(!showBalance);
    // Ensure the input form is hidden when viewing the balance
    setShowInputAdd(false);
    setShowInputWithdraw(false);
  };

  const renderInputFormAdd = () => (
    <form onSubmit={handleSubmitAdd}>
      <input
        type="number"
        name="amount"
        placeholder="Enter amount"
        value={amount}
        onChange={handleChange}
        required
      />
      <button className="form-button">Submit</button>
    </form>
  );

  const renderInputFormWithdraw = () => (
    <form onSubmit={handleSubmitWithdraw}>
      <input
        type="number"
        name="amount"
        placeholder="Enter amount"
        value={amount}
        onChange={handleChange}
        required
      />
      <button className="form-button">Submit</button>
    </form>
  );

  const handleAudit = async () => {
    const response = await fetch("http://127.0.0.1:5000/download_audit_log", {
      method: "GET",
    });

    if (response.ok) {
      // Assuming the server response is the CSV file
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;

      // This filename can be dynamic based on your requirements
      a.download = "audit_log.csv";
      document.body.appendChild(a); // Append the anchor to the body to make it clickable
      a.click(); // Simulate a click on the anchor to start the download

      window.URL.revokeObjectURL(url); // Clean up the URL object
      a.remove(); // Remove the anchor from the DOM
    } else {
      // Handle HTTP error responses
      console.error("Failed to download audit log:", response.statusText);
    }
  };

  const handleLogout = async () => {
    const response = await fetch("http://127.0.0.1:5000/logout", {
      method: "GET",
    });

    if (response.ok) {
      const cookies = new Cookies();
      cookies.remove("jwt", { path: "/" });
      sessionStorage.clear();
      navigate("/signin");
    } else {
      // Handle HTTP error responses
      console.error("Failed to logout:", response.statusText);
    }
  };

  return (
    <div className="form-container">
      <div className="landing-form">
        <button
          className="form-button"
          onClick={() => handleAction("withdraw")}
        >
          Withdraw
        </button>
        <button className="form-button" onClick={() => handleAction("add")}>
          Add
        </button>
        <button className="form-button" onClick={handleBalance}>
          View Current Balance
        </button>
        <button className="form-button" onClick={handleAudit}>
          Download Audit
        </button>
        <button className="form-button" onClick={handleLogout}>
          Logout
        </button>
        {showInputAdd && renderInputFormAdd()}
        {showInputWithdraw && renderInputFormWithdraw()}
        {showBalance && (
          <div className="balance-display">
            Your current balance is: ${balance.toFixed(2)}
          </div>
        )}
      </div>
    </div>
  );
}

export default Transactions;
