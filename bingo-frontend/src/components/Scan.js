import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from "html5-qrcode";
import { useNavigate } from 'react-router-dom';
import './Scan.css';

const Scan = () => {
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef(null);
  const isScannerInitialized = useRef(false);
  const navigate = useNavigate();

  // List of valid QR codes
  const VALID_QR_CODES = [
    "https://maps.app.goo.gl/tzWHSuGUG35X8m3MA",
    "https://maps.app.goo.gl/ZFQUUL5xqUQQp8BD7?g_st=com.google.maps.preview.copy",
    "https://maps.app.goo.gl/9zrjkXXHMJDXtMrC8?g_st=com.google.maps.preview.copy",
    "https://maps.app.goo.gl/FnhwTw3eB2zvpnzq6?g_st=com.google.maps.preview.copy"
  ];

  const isValidQRCode = (decodedText) => {
    return VALID_QR_CODES.includes(decodedText);
  };

  const onScanSuccess = (decodedText) => {
    console.log("Scanned QR Code Data:", decodedText);

    // Validate the QR code
    if (isValidQRCode(decodedText)) {
      setScanResult(decodedText);

      // Stop scanning
      if (scannerRef.current && scannerRef.current.isScanning) {
        scannerRef.current.stop()
          .then(() => {
            setIsScanning(false);
            handleScanResult(decodedText);
          })
          .catch(() => setError("Error stopping the scanner"));
      }
    } else {
      setError("Invalid QR Code. Please scan the correct QR code.");
    }
  };

  const onScanError = (err) => {
    if (!err.toString().includes("NotFoundException")) {
      console.error("QR Code scan error:", err);
      setError("Error scanning QR code: " + err.toString());
    }
  };

  useEffect(() => {
    const readerElement = document.getElementById('reader');

    // Clear previous scanner instance
    if (scannerRef.current) {
      scannerRef.current.clear();
    }

    if (!isScannerInitialized.current && readerElement) {
      const html5QrCode = new Html5Qrcode("reader", true);
      scannerRef.current = html5QrCode;
      isScannerInitialized.current = true;

      html5QrCode.start(
        { facingMode: "environment" },
        { fps: 10, qrbox: { width: 250, height: 250 } },
        onScanSuccess,
        onScanError
      ).then(() => {
        setIsScanning(true);
      }).catch(err => {
        console.error("Failed to start scanner:", err);
        setError("Failed to start camera. Please check camera permissions.");
      });
    }

    // Cleanup on unmount
    return () => {
      if (scannerRef.current && scannerRef.current.isScanning) {
        scannerRef.current.stop().catch(() => {});
        scannerRef.current = null;
        isScannerInitialized.current = false;
      }
    };
  }, []);

  const handleScanResult = async (result) => {
    try {
      const taskId = localStorage.getItem('selectedTaskId');
      const isResubmission = localStorage.getItem('isResubmission') === 'true';
      const token = localStorage.getItem('accessToken');

      if (!token) {
        setError('You must be logged in to submit a task.');
        setTimeout(() => navigate('/login'), 2000);
        return;
      }

      if (!taskId) {
        setError('No task selected. Redirecting to Bingo Board...');
        setTimeout(() => navigate('/bingo'), 2000);
        return;
      }

      setScanResult(`Processing: ${result}`);

      const requestData = {
        task_id: taskId,
        qr_code_data: result,
        is_resubmission: isResubmission
      };

      const response = await fetch('http://localhost:8000/api/complete_task/', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('accessToken')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData),
      });

      const data = await response.json();

      if (response.ok) {
        localStorage.removeItem('isResubmission');
        setScanResult(`Success! ${data.message || 'Submission received.'}`);
        setTimeout(() => navigate('/bingo'), 2000);
      } else {
        setError(data.message || 'Failed to submit scan. Please try again.');
      }
    } catch (error) {
      setError('An error occurred while processing your scan.');
    }
  };

  const handleBack = () => {
    localStorage.removeItem('isResubmission');
    navigate('/bingo');
  };

  return (
    <div className="scan-container">
      <h1>Scan QR Code</h1>

      <div id="reader-container">
        <div id="reader"></div>
      </div>

      {isScanning && !scanResult && !error && (
        <p>Position the QR code within the frame...</p>
      )}

      {scanResult && (
        <div className="scan-result">
          <p>{scanResult}</p>
        </div>
      )}

      {error && (
        <div className="error-message">
          <p>{error}</p>
        </div>
      )}

      <div className="button-container">
        <button onClick={handleBack} className="back-button">
          Back to Bingo Board
        </button>
      </div>
    </div>
  );
};

export default Scan;