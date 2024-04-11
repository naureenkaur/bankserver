// Import necessary libraries
import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import CryptoJS from "crypto-js";
import "./Transactions.css";

// Define the Transactions component
function Transactions() {
  // Initialize state variables
  const navigate = useNavigate();
  const [username, setUsername] = useState(sessionStorage.getItem("username"));
  const [balance, setBalance] = useState(0);
  const [amount, setAmount] = useState("");
  const [showInputAdd, setShowInputAdd] = useState(false);
  const [showInputWithdraw, setShowInputWithdraw] = useState(false);
  const [showBalance, setShowBalance] = useState(false);

  // Define the encryption and MAC keys (ensure secure key management)
  const encryptionKey = CryptoJS.enc.Utf8.parse('your-encryption-key-here');
  const macKey = CryptoJS.enc.Utf8.parse('your-mac-key-here');

  // Define the function to encrypt data before sending to the server
  const encryptData = (data) => {
    const iv = CryptoJS.lib.WordArray.random(128 / 8);
    const key = CryptoJS.enc.Hex.parse('your-encryption-key-here');
    const encrypted = CryptoJS.AES.encrypt(JSON.stringify(data), key, {
      iv: iv,
      padding: CryptoJS.pad.Pkcs7,
      mode: CryptoJS.mode.CFB,
    });
    return iv.toString() + encrypted.ciphertext.toString(CryptoJS.enc.Base64);
  };

  // Define the function to generate a MAC for data integrity
  const generateMac = (ciphertext) => {
    const hmacDigest = CryptoJS.HmacSHA256(ciphertext, macKey);
    return hmacDigest.toString(CryptoJS.enc.Base64);
  };

  // Define the function to decrypt data received from the server
  const decryptData = (transitmessage) => {
    const salt = CryptoJS.enc.Hex.parse(transitmessage.substr(0, 32));
    const iv = CryptoJS.enc.Hex.parse(transitmessage.substr(32, 32));
    const encryptedData = transitmessage.substring(64);
    const key = CryptoJS.PBKDF2(encryptionKey, salt, {
      keySize: 256 / 32,
      iterations: 100,
    });
    const decrypted = CryptoJS.AES.decrypt(encryptedData, key, {
      iv: iv,
      padding: CryptoJS.pad.Pkcs7,
      mode: CryptoJS.mode.CFB,
    });
    return JSON.parse(decrypted.toString(CryptoJS.enc.Utf8));
  };

  // Define the function to verify the MAC from the received data
  const verifyMac = (data, mac) => {
    const generatedMac = generateMac(data);
    return generatedMac === mac;
  };

  // Define the function to handle the action (withdraw or add)
  const handleAction = (type) => {
    if (type === "withdraw") {
      setShowInputWithdraw(true);
      setShowInputAdd(false);
    } else if (type === "add") {
      setShowInputAdd(true);
      setShowInputWithdraw(false);
    }
    setShowBalance(false);
  };

  // Define the function to handle the form input change
  const handleChange = (event) => {
    setAmount(event.target.value);
  };

  // Define the function to handle adding money
  const handleSubmitAdd = async (e) => {
    e.preventDefault();
    const numberAmount = parseFloat(amount);
    if (!numberAmount) return;

    if (showInputAdd && numberAmount > 0) {
      const jsonData = { username, amount: numberAmount };
      const encryptedData = encryptData(jsonData);
      const mac = generateMac(encryptedData);

      // Make the POST request to the server
      const response = await fetch('http://127.0.0.1:5000/add_money', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ encryptedData, mac }),
      });

      // Handle the response from the server
      const responseData = await response.json();
      if (!verifyMac(responseData.encryptedData, responseData.mac)) {
        console.error('MAC verification failed');
        return;
      }
      const decryptedData = decryptData(responseData.encryptedData);

      if (response.ok) {
        console.log('Add successful');
      } else {
        console.error('Failed to add money:', decryptedData.message);
      }
    }

    setAmount('');
    setShowInputAdd(false);
  };

  // Define the function to handle withdrawing money
  const handleSubmitWithdraw = async (e) => {
    e.preventDefault();
    const numberAmount = parseFloat(amount);
    if (!numberAmount) return;

    if (showInputWithdraw && numberAmount > 0) {
      const jsonData = { username, amount: numberAmount };
      const encryptedData = encryptData(jsonData);
      const mac = generateMac(encryptedData);

      // Make the POST request to the server
      const response = await fetch('http://127.0.0.1:5000/withdraw_money', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ encryptedData, mac }),
      });

      // Handle the response from the server
      const responseData = await response.json();
      if (!verifyMac(responseData.encryptedData, responseData.mac)) {
        console.error('MAC verification failed');
        return;
      }
      const decryptedData = decryptData(responseData.encryptedData);

      if (response.ok) {
        console.log('Withdraw successful');
      } else {
        console.error('Failed to withdraw money:', decryptedData.message);
      }
    }

    setAmount('');
    setShowInputWithdraw(false);
  };

  // Define the function to handle viewing the balance
  const handleBalance = async () => {
    const jsonData = { username };
    const encryptedData = encryptData(jsonData);
    const mac = generateMac(encryptedData);

    // Make the POST request to the server
    const response = await fetch('http://127.0.0.1:5000/view_balance', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ encryptedData, mac }),
    });

    // Handle the response from the server
    const responseData = await response.json();
    if (!verifyMac(responseData.encryptedData, responseData.mac)) {
      console.error('MAC verification failed');
      return;
    }
    const decryptedData = decryptData(responseData.encryptedData);

    if (response.ok) {
      setBalance(decryptedData.balance);
    } else {
      console.error('Failed to view balance:', decryptedData.message);
    }

    setShowBalance(!showBalance);
    setShowInputAdd(false);
    setShowInputWithdraw(false);
  };

  // Define the function to render the form for adding money
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

  // Define the function to render the form for withdrawing money
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

  // Define the function to handle downloading the audit log
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
    } else {
      console.error("Failed to download audit log:", response.statusText);
    }
  };

  // Define the function to handle logging out
  const handleLogout = async () => {
    const response = await fetch("http://127.0.0.1:5000/logout", {
      method: "GET",
    });

    if (response.ok) {
      sessionStorage.clear();
      navigate("/signin");
    } else {
      console.error("Failed to logout:", response.statusText);
    }
  };

  // Return the JSX for the Transactions component
  return (
    <div className="form-container">
      <div className="landing-form">
        <button className="form-button" onClick={() => handleAction("withdraw")}>
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

// Export the Transactions component
export default Transactions;
