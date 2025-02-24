import React from 'react';
import { Link } from 'react-router-dom';

const PrivacyPolicy = () => {
    return (
        <div className="privacy-policy-container">
          <h1>Privacy Policy</h1>
          <p>Last Updated on 24th Feb 2025</p>
            <p>This Privacy Policy explains how we collect, use, and disclose your information 
                when you use our website and related services.</p>
                <h2>Information We Collect</h2>
      <p>We collect the following personal information:</p>
      <ul>
        <li>Username</li>
        <li>University email address (@exeter.ac.uk)</li>
        <li>Game activity and achievements</li>
      </ul>
      
      <h2>How We Use Your Information</h2>
      <p>
        We use your information to create your account, track your game progress, and display leaderboard rankings.
      </p>
      
      <h2>GDPR Rights</h2>
      <p>
        Under GDPR, you have rights to access, correct, or delete your personal data.
        To exercise these rights, please contact us at bingo@exeter.ac.uk.
      </p>
      
      <h2>Data Security</h2>
      <p>
        We implement appropriate security measures to protect your personal data.
      </p>
      
      <div className="back-link">
        <Link to="/">Back to Home</Link>
      </div>
    </div>
  );
};

export default PrivacyPolicy;