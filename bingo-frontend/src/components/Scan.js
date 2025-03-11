import { Html5QrcodeScanner } from "html5-qrcode";

const Scan = () => {
    const root = document.getElementById("root");

    if (!root) {
        console.error("Root element not found");
        return;
    }

    // Prevent multiple scanner instances by checking if it already exists
    if (document.getElementById("reader")) {
        console.warn("Scanner already exists. Skipping initialization.");
        return;
    }

    // Create scanner container
    const scannerContainer = document.createElement("div");
    scannerContainer.id = "reader";
    scannerContainer.style.width = "600px";
    root.appendChild(scannerContainer);

    // Create result container
    const resultContainer = document.createElement("div");
    resultContainer.id = "result";
    resultContainer.style.textAlign = "center";
    resultContainer.style.fontSize = "1.5rem";
    root.appendChild(resultContainer);

    // Initialize QR Scanner
    const scanner = new Html5QrcodeScanner("reader", {
        qrbox: {
            width: 250,
            height: 250,
        },
        fps: 20,
    });

    scanner.render(success, error);

    function success(result) {
        resultContainer.innerHTML = `
            <h2>Success!</h2>
            <p><a href="${result}">${result}</a></p>
        `;

        scanner.clear();

        // Ensure scannerContainer exists before removing
        if (scannerContainer && scannerContainer.parentNode) {
            scannerContainer.parentNode.removeChild(scannerContainer);
        }
    }

    function error(err) {
        console.error(err);
    }
};

export default Scan;
