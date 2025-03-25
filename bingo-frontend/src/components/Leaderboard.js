import React, { useState, useEffect } from 'react';
import { useSearchParams } from 'react-router-dom';
import axios from 'axios';
import './Leaderboard.css';

const API_URL = "https://ecm2434-v3.onrender.com";

const Leaderboard = () => {
    const [lifetimeLeaderboard, setLifetimeLeaderboard] = useState([]);
    const [monthlyLeaderboard, setMonthlyLeaderboard] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const [searchParams] = useSearchParams();
    const leaderboardType = searchParams.get('type') || 'lifetime';

    const isLoggedIn = localStorage.getItem('accessToken') !== null;

    useEffect(() => {
        setLoading(true);
        
        axios.get(`${API_URL}/api/leaderboard/`)
            .then((response) => {
                console.log(" API Raw Response:", response.data);

                if (Array.isArray(response.data)) {
                    // Assuming the first item is lifetime and second is monthly
                    const lifetimeData = response.data;
                    const monthlyData = response.data;

                    console.log(" Setting Lifetime Leaderboard:", lifetimeData);
                    console.log(" Setting Monthly Leaderboard:", monthlyData);

                    setLifetimeLeaderboard(lifetimeData);
                    setMonthlyLeaderboard(monthlyData);
                } else {
                    // Original code for when the API returns the expected object structure
                    const lifetimeData = response.data.lifetime_leaderboard || [];
                    const monthlyData = response.data.monthly_leaderboard || [];

                    console.log("🔥 Setting Lifetime Leaderboard:", lifetimeData);
                    console.log("🔥 Setting Monthly Leaderboard:", monthlyData);

                    setLifetimeLeaderboard(lifetimeData);
                    setMonthlyLeaderboard(monthlyData);
                }
                
                setLoading(false);
            })
            .catch((error) => {
                console.error(" Error fetching leaderboard:", error);
                setError("Failed to fetch leaderboard");
                setLoading(false);
            });
    }, []);

    return (
        <div className="leaderboard-container">
            {error && <p className="error-message">{error}</p>}
            {loading ? (
                <p>Loading...</p>
            ) : (
                <>
                    <div className="leaderboard-navigation">
                        <button 
                            className={`leaderboard-nav-button ${leaderboardType === 'lifetime' ? 'active' : ''}`}
                            onClick={() => window.location.href = '/leaderboard?type=lifetime'}
                        >
                            🏆 Lifetime Leaderboard
                        </button>
                        <button 
                            className={`leaderboard-nav-button ${leaderboardType === 'monthly' ? 'active' : ''}`}
                            onClick={() => window.location.href = '/leaderboard?type=monthly'}
                        >
                            📅 Monthly Leaderboard
                        </button>
                    </div>
                    
                    {leaderboardType === 'lifetime' ? (
                        <div className="leaderboard-section">
                            <h2 className="leaderboard-title">🏆 Lifetime Leaderboard</h2>
                            <ul className="leaderboard-list">
                                {lifetimeLeaderboard.length > 0 ? (
                                    lifetimeLeaderboard.map((player, index) => (
                                        <li key={index} className={`leaderboard-item ${index % 2 === 0 ? "even" : "odd"}`}>
                                            <span className="rank">{index + 1}.</span>
                                            {/* Adjust these field names if necessary based on your API response */}
                                            <span className="name">{player.user || player.username || player.name || "Unknown Player"}</span>
                                            <span className="points">{player.points !== undefined ? player.points : player.score || "0"} Points</span>
                                        </li>
                                    ))
                                ) : (
                                    <p> No lifetime leaderboard data available.</p>
                                )}
                            </ul>
                        </div>
                    ) : (
                        <div className="leaderboard-section">
                            <h2 className="leaderboard-title">📅 This Month's Stars</h2>
                            <ul className="leaderboard-list">
                                {monthlyLeaderboard.length > 0 ? (
                                    monthlyLeaderboard.map((player, index) => (
                                        <li key={index} className={`leaderboard-item ${index % 2 === 0 ? "even" : "odd"}`}>
                                            <span className="rank">{index + 1}.</span>
                                            {/* Adjust these field names if necessary based on your API response */}
                                            <span className="name">{player.user || player.username || player.name || "Unknown Player"}</span>
                                            <span className="points">{player.points !== undefined ? player.points : player.score || "0"} Points</span>
                                        </li>
                                    ))
                                ) : (
                                    <p> No monthly leaderboard data available.</p>
                                )}
                            </ul>
                        </div>
                    )}
                </>
            )}
            <button 
                    className="back-to-home" 
                    onClick={() => window.location.href = isLoggedIn ? '/userprofile' : '/'}
            >
                ← Back to {isLoggedIn ? 'Profile' : 'Home'}
            </button>
        </div>


    );
};

export default Leaderboard;