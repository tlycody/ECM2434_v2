// Privacy Policy Component

import React from 'react';
import { Link } from 'react-router-dom';
import './PrivacyPolicy.css';

const PrivacyPolicy = () => {
    return (
        <div className="privacy-policy-container">
            {/* Page Header */}
            <h1>Privacy Policy</h1>
            <p>Last Updated on 12th Mar 2025</p>

            {/* Introduction */}
            <p>
            This Privacy Policy explains how we collect, use, and disclose your information when you use our website and related services. "We", "Our", "Us" is committed to protecting and respecting your privacy.
            </p>

            {/* Data Controller */}
            <h2>Data Controller</h2>
            <p>The data controller for your personal information is:</p>
            <p>
                Caffeinated Divas<br />
                The University of Exeter<br />
                Exeter, Devon, UK<br />
                Email: caffeinateddivas@gmail.com
            </p>

            {/* Information Collection */}
            <h2>Information We Collect</h2>
            <p>We collect the following personal information:</p>
            <ul>
                <li>Username</li>
                <li>Email address</li>
                <li>Game activity and achievements</li>
            </ul>

            {/* Legal Basis */}
            <h2>Legal Basis for Processing</h2>
            <p>We process your personal data on the following legal bases:</p>
            <ul>
                <li><strong>Consent:</strong> You have given clear consent for us to process your personal data for the specific purpose of participating in our game.</li>
                <li><strong>Legitimate Interest:</strong> It is in our legitimate interests to process certain data to provide and improve our gaming services.</li>
            </ul>

            {/* Purpose of Data Collection */}
            <h2>How We Use Your Information</h2>
            <p>We use your information to:</p>
            <ul>
                <li>Create and manage your account</li>
                <li>Track your game progress</li>
                <li>Display leaderboard rankings</li>
                <li>Improve our game services</li>
                <li>Communicate with you about the game</li>
            </ul>

            {/* Data Retention */}
            <h2>Data Retention</h2>
            <p>
                We will retain your personal data only for as long as necessary to fulfill the purposes for which it was collected. Specifically:
            </p>
            <ul>
                <li>Account information will be retained as long as you maintain an active account</li>
                <li>Game activity data will be stored as long as you maintain an active account</li>
                <li>When you delete your account, all personal data will be permanently deleted from our records within 30 days</li>
            </ul>

            {/* Third-Party Sharing */}
            <h2>Third-Party Sharing</h2>
            <p>We do not share your personal information with third parties except in the following cases:</p>
            <ul>
                <li>When required by law</li>
                <li>With service providers who assist us in operating our game</li>
            </ul>

            {/* GDPR Compliance */}
            <h2>GDPR Rights</h2>
            <p>Under the General Data Protection Regulation (GDPR), you have the following rights:</p>
            <ul>
                <li><strong>Right to Access:</strong> You can request a copy of the personal data we hold about you.</li>
                <li><strong>Right to Rectification:</strong> You can request that we correct any inaccurate or incomplete personal data.</li>
                <li><strong>Right to Erasure:</strong> You can request that we delete your personal data (also known as the "right to be forgotten").</li>
            </ul>
            <p>
                To exercise any of these rights, please contact us at <strong>caffeinateddivas@gmail.com</strong>.
            </p>

            {/* Account Deletion */}
            <h2>Account Deletion</h2>
            <p>You can request to delete your profile permanently at any time. Upon deletion:</p>
            <ul>
                <li>All personal data associated with your account will be removed from our active databases</li>
                <li>Your data will be permanently deleted from our records within 30 days</li>
            </ul>
            <p>
                To delete account deletion, you can do it in the player profile."
            </p>

            {/* Data Security Measures */}
            <h2>Data Security</h2>
            <p>
                We implement appropriate security measures to protect your personal data.
            </p>

            {/* Changes to Privacy Policy */}
            <h2>Changes to This Privacy Policy</h2>
            <p>
            We may update this Privacy Policy occasionally. Please visit our website to check for any updates. We recommend reviewing the Privacy Policy periodically to stay informed about any changes.
            </p>

            {/* Contact Information */}
            <h2>Contact Us</h2>
            <p>If you have any questions about this Privacy Policy or our data practices, please contact us at:</p>
            <ul>
                <li>Email: <strong>caffeinateddivas@gmail.com</strong></li>
            </ul>

            {/* Back to Home Link */}
            <div className="back-link">
                <Link to="/">Back to Home</Link>
            </div>
            </div>
    );
};

export default PrivacyPolicy;
