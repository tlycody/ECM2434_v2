// ============================
// QR Code Scanner Component
// ============================

import { useRef, useState } from "react";
import jsQR from "jsqr";

const Scan = () => {
    // Refs for DOM elements
    const videoRef = useRef(null);
    const canvasRef = useRef(null);
    const ctxRef = useRef(null);

    // State for scanner status & results
    const [scanning, setScanning] = useState(false);
    const [status, setStatus] = useState("Click start to scan");
    const [qrResult, setQrResult] = useState("");
    const [stream, setStream] = useState(null);

    // ============================
    // Start the QR Scanner
    // ============================

    const startScanner = async () => {
        try {
            const videoElement = videoRef.current;
            const canvasElement = canvasRef.current;

            // Ensure video & canvas exist
            if (!videoElement || !canvasElement) return;

            // Request camera access
            const mediaStream = await navigator.mediaDevices.getUserMedia({
                video: { facingMode: "environment" } // Use back camera for better scanning
            });

            videoElement.srcObject = mediaStream;
            setStream(mediaStream);

            videoElement.onloadedmetadata = () => {
                videoElement.play();
                setScanning(true);
                setStatus("Scanning for QR code...");

                // Set canvas size to match video
                canvasElement.width = videoElement.videoWidth;
                canvasElement.height = videoElement.videoHeight;

                // Get canvas context
                ctxRef.current = canvasElement.getContext("2d");

                // Start scanning loop
                scanQRCode();
            };
        } catch (error) {
            setStatus(`Error accessing camera: ${error.message}`);
            console.error("Error accessing camera:", error);
        }
    };

    // ============================
    // Scan for QR Code in the Video Stream
    // ============================

    const scanQRCode = () => {
        if (!scanning) return;
        const videoElement = videoRef.current;
        const canvasElement = canvasRef.current;
        const ctx = ctxRef.current;

        if (!videoElement || !canvasElement || !ctx) return;

        if (videoElement.readyState === videoElement.HAVE_ENOUGH_DATA) {
            ctx.drawImage(videoElement, 0, 0, canvasElement.width, canvasElement.height);
            const imageData = ctx.getImageData(0, 0, canvasElement.width, canvasElement.height);

            // Attempt to read the QR code
            const code = jsQR(imageData.data, imageData.width, imageData.height, {
                inversionAttempts: "dontInvert",
            });

            if (code) {
                console.log("QR Code detected:", code.data);
                stopScanner(); // Stop scanning when a QR code is found
                setQrResult(code.data);
                setStatus("QR Code found!");
            }
        }

        requestAnimationFrame(scanQRCode); // Continue scanning in a loop
    };

    // ============================
    // Stop the Scanner
    // ============================

    const stopScanner = () => {
        setScanning(false);
        if (stream) {
            stream.getTracks().forEach(track => track.stop()); // Stop camera stream
            setStream(null);
        }
    };

    // ============================
    // Render Scanner UI
    // ============================

    return (
        <div className="scanner-container">
            <h1>QR Code Scanner</h1>
            <p>{status}</p>

            {/* Video Feed for QR Scanning */}
            <video ref={videoRef} style={{ display: scanning ? "block" : "none" }}></video>

            {/* Hidden Canvas for Processing the QR Code */}
            <canvas ref={canvasRef} style={{ display: "none" }}></canvas>

            {/* Display Scanned QR Code Result */}
            {qrResult && (
                <div id="qr-result">
                    <strong>QR Code:</strong> {qrResult}
                </div>
            )}

            {/* Button to Start Scanning */}
            <button onClick={startScanner} disabled={scanning}>
                {scanning ? "Scanning..." : "Start Scan"}
            </button>
        </div>
    );
};

export default Scan;
