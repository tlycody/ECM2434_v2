import React, { useEffect, useRef, useState } from 'react';
import { Html5Qrcode } from "html5-qrcode";
import { useNavigate } from 'react-router-dom';
import './Scan.css';

const Scan = () => {
  const [scanResult, setScanResult] = useState(null);
  const [error, setError] = useState(null);
  const [isScanning, setIsScanning] = useState(false);
  const scannerRef = useRef(null);
  const isScannerInitialized = useRef(false); // Track if scanner is initialized
  const navigate = useNavigate();

  const onScanSuccess = (decodedText) => {
    console.log("QR Code scanned successfully:", decodedText);
    setScanResult(decodedText);

    if (scannerRef.current && scannerRef.current.isScanning) {
      scannerRef.current.stop()
        .then(() => {
          setIsScanning(false);
          handleScanResult(decodedText);
        })
        .catch(() => {});
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

    // Clear the #reader element before initialization
    if (readerElement) {
      while (readerElement.firstChild) {
        readerElement.removeChild(readerElement.firstChild);
      }
    }

    // Initialize the scanner only once
    if (!isScannerInitialized.current) {
      const html5QrCode = new Html5Qrcode("reader", /* verbose= */ true);
      scannerRef.current = html5QrCode;
      isScannerInitialized.current = true;

      const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
      };

      html5QrCode.start(
        { facingMode: "environment" },
        config,
        onScanSuccess,
        onScanError
      )
      .then(() => {
        setIsScanning(true);
      })
      .catch(err => {
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

      // Clear the #reader element again
      if (readerElement) {
        while (readerElement.firstChild) {
          readerElement.removeChild(readerElement.firstChild);
        }
      }
    };
  }, []);

  const handleScanResult = async (result) => {
    try {
      const taskId = localStorage.getItem('selectedTaskId');
      const isResubmission = localStorage.getItem('isResubmission') === 'true';
      const token = localStorage.getItem('accessToken');

      if (!token) {
        setError('You must be logged in to submit a task');
        setTimeout(() => navigate('/login'), 2000);
        return;
      }

      if (!taskId) {
        setError('Task ID not found. Please select a task again.');
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
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(requestData)
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
    if (scannerRef.current && scannerRef.current.isScanning) {
      scannerRef.current.stop().catch(() => {});
    }

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
          <h2>Successfully Scanned!</h2>
          <p>{scanResult}</p>
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