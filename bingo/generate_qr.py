import qrcode

# Define locations with latitude and longitude
LOCATIONS = {
    "clydesdale house": {"lat": 50.73640075076695, "lon": -3.5403583050147263},
    "british heart foundation1": {"lat": 50.72665675075289, "lon": -3.524533819396889},
    "british heart foundation2": {"lat": 50.72212089681603, "lon": -3.5329984815588897},
    "zero waste shop": {"lat": 50.72116105745902, "lon": -3.520127589180877},
    "community garden": {"lat": 50.74041515153113, "lon": -3.5296544924117383}
}

# Generate and save QR codes
for name, coords in LOCATIONS.items():
    google_maps_url = f"https://www.google.com/maps?q={coords['lat']},{coords['lon']}"
    qr = qrcode.make(google_maps_url)
    
    # Save QR code as an image
    filename = f"{name.replace(' ', '_')}.png"
    qr.save(filename)
    print(f"QR code saved: {filename}")

print("QR codes generated successfully.")
