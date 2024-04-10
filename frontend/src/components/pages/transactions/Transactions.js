import React, { useState } from 'react';
import "./Transactions.css";

function Transactions() {
    const [balance, setBalance] = useState(0);
    const [amount, setAmount] = useState('');
    const [showInput, setShowInput] = useState(false);
    const [showBalance, setShowBalance] = useState(false); // New state for showing the balance message

    const handleAction = (type) => {
        setShowInput(true);
        // Hide the balance message when adding or withdrawing
        setShowBalance(false);
    };

    const handleChange = (event) => {
        setAmount(event.target.value);
    };

    const handleSubmit = (e) => {
        e.preventDefault();
        const numberAmount = parseFloat(amount);
        if (!numberAmount) return; // Early return if amount is not a number

        if (showInput && numberAmount > 0) {
            if (amount && numberAmount <= balance) {
                setBalance(prevBalance => prevBalance - numberAmount);
            } else {
                setBalance(prevBalance => prevBalance + numberAmount);
            }
            setAmount('');
            setShowInput(false);
        }
    };

    const handleBalance = () => {
        // Toggle the balance message display
        setShowBalance(!showBalance);
        // Ensure the input form is hidden when viewing the balance
        setShowInput(false);
    };

    const renderInputForm = () => (
        <form onSubmit={handleSubmit}>
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

    const handleAudit = () => {
        
    };

    return (
        <div className="form-container">
            <div className="landing-form">
                <button className="form-button" onClick={() => handleAction('withdraw')}>Withdraw</button>
                <button className="form-button" onClick={() => handleAction('add')}>Add</button>
                <button className="form-button" onClick={handleBalance}>View Current Balance</button>
                <button className="form-button" onClick={handleAudit}>Download Audit</button>
                {showInput && renderInputForm()}
                {showBalance && 
                    <div className="balance-display">
                        Your current balance is: ${balance.toFixed(2)}
                    </div>
                }
            </div>
        </div>
    );
}

export default Transactions;
