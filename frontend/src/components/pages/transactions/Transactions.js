import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import CryptoJS from "crypto-js";
import "./Transactions.css";

function Transactions() {
  const navigate = useNavigate();
  const isAuthenticated = sessionStorage.getItem("isAuthenticated")  === "true";

  useEffect(() => {
    // Redirect to signin page if not authenticated
    if (!isAuthenticated) {
      navigate("/signin");
    }
  }, [isAuthenticated, navigate]);

  const [balance, setBalance] = useState(0);
  const [amount, setAmount] = useState("");
  const [showInputAdd, setShowInputAdd] = useState(false);
  const [showInputWithdraw, setShowInputWithdraw] = useState(false);
  const [showBalance, setShowBalance] = useState(false);

  const username = sessionStorage.getItem("username");
  const encryptionKey = sessionStorage.getItem("encryptionKey"); // Ensure this key is securely provided and stored
  const macKey = sessionStorage.getItem("macKey"); // Ensure this key is securely provided and stored

  const encryptData = (data) => {
    const ciphertext = CryptoJS.AES.encrypt(JSON.stringify(data), CryptoJS.enc.Utf8.parse(encryptionKey), {
      mode: CryptoJS.mode.CFB,
      padding: CryptoJS.pad.NoPadding
    }).toString();
    return ciphertext;
  };

  const generateHMAC = (data) => {
    const hmac = CryptoJS.HmacSHA256(data, macKey).toString();
    return hmac;
  };

  const handleTransaction = async (endpoint, jsonData) => {
    const encryptedData = encryptData(jsonData);
    const hmac = generateHMAC(encryptedData);
    const response = await fetch(`http://127.0.0.1:5000/${endpoint}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ encryptedData, hmac }),
    });

    return response.json();
  };

  const handleSubmitAdd = async (e) => {
    e.preventDefault();
    const numberAmount = parseFloat(amount);
    if (!numberAmount) return;
    const jsonData = { username, amount: numberAmount };
    const data = await handleTransaction("add_money", jsonData);
    console.log("Add response:", data);

    setAmount("");
    setShowInputAdd(false);
  };

  const handleSubmitWithdraw = async (e) => {
    e.preventDefault();
    const numberAmount = parseFloat(amount);
    if (!numberAmount) return;
    const jsonData = { username, amount: numberAmount };
    const data = await handleTransaction("withdraw_money", jsonData);
    console.log("Withdraw response:", data);

    setAmount("");
    setShowInputWithdraw(false);
  };

  const handleBalance = async () => {
    const jsonData = { username };
    const data = await handleTransaction("view_balance", jsonData);
    console.log("Balance response:", data);

    if (data.balance !== undefined) {
      setBalance(data.balance);
    }
    setShowBalance(!showBalance);
    setShowInputAdd(false);
    setShowInputWithdraw(false);
  };

  const handleAudit = async () => {
    const response = await fetch("http://127.0.0.1:5000/download_audit_log", {
      method: "GET",
    });
    if (response.ok) {
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "audit_log.csv";
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      a.remove();
    }
  };

  const handleLogout = () => {
    sessionStorage.clear();
    navigate("/signin");
  };

  return (
    <div className="form-container">
      <div className="landing-form">
        <button className="form-button" onClick={() => setShowInputAdd(true)}>Add Funds</button>
        <button className="form-button" onClick={() => setShowInputWithdraw(true)}>Withdraw Funds</button>
        <button className="form-button" onClick={handleBalance}>View Current Balance</button>
        <button className="form-button" onClick={handleAudit}>Download Audit</button>
        <button className="form-button" onClick={handleLogout}>Logout</button>
        {showInputAdd && (
          <form onSubmit={handleSubmitAdd}>
            <input type="number" name="amount" placeholder="Enter amount" value={amount} onChange={(e) => setAmount(e.target.value)} required />
            <button className="form-button">Submit</button>
          </form>
        )}
        {showInputWithdraw && (
          <form onSubmit={handleSubmitWithdraw}>
            <input type="number" name="amount" placeholder="Enter amount" value={amount} onChange={(e) => setAmount(e.target.value)} required />
            <button className="form-button">Submit</button>
          </form>
        )}
        {showBalance && <div className="balance-display">Your current balance is: ${balance.toFixed(2)}</div>}
      </div>
    </div>
  );
}

export default Transactions;
