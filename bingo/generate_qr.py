# Import the qrcode library to generate QR codes
import qrcode

# ============================
# Define Locations and Coordinates
# ============================

# Dictionary containing predefined locations with their latitude and longitude values
LOCATIONS = {
    "clydesdale house": {"lat": 50.73640075076695, "lon": -3.5403583050147263},
    "british heart foundation1": {"lat": 50.72665675075289, "lon": -3.524533819396889},
    "british heart foundation2": {"lat": 50.72212089681603, "lon": -3.5329984815588897},
    "zero waste shop": {"lat": 50.72116105745902, "lon": -3.520127589180877},
    "community garden": {"lat": 50.74041515153113, "lon": -3.5296544924117383}
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
