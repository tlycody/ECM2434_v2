# Import the qrcode library to generate QR codes
import qrcode

# ============================
# Define Locations and Coordinates
# ============================

# Dictionary containing predefined locations with their latitude and longitude values
LOCATIONS = {
    "clydesdale house": {"lat": 50.736, "lon": -3.540},
    "british heart foundation1": {"lat": 50.727, "lon": -3.525},
    "british heart foundation2": {"lat": 50.722, "lon": -3.533},
    "zero waste shop": {"lat": 50.721, "lon": -3.520},
    "community garden": {"lat": 50.740, "lon": -3.530}
}

# ============================
# QR Code Generation Process
# ============================

# Loop through each location and generate a QR code
for name, coords in LOCATIONS.items():
    # Construct Google Maps URL using latitude and longitude values
    google_maps_url = f"https://www.google.com/maps?q={coords['lat']},{coords['lon']}"
    
    # Generate a QR code based on the Google Maps link
    qr = qrcode.make(google_maps_url)
    
    # Format filename by replacing spaces with underscores for readability
    filename = f"{name.replace(' ', '_')}.png"
    
    # Save the generated QR code as an image file
    qr.save(filename)
    
    # Print a success message for each QR code generated
    print(f"QR code saved: {filename}")

# Print final confirmation message after all QR codes are created
print("QR codes generated successfully.")
