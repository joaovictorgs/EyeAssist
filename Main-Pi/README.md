# Main-Pi

This module acts as both a physical edge sensor and the core data aggregator/calculator for the EyeAssist tracking system.

## Overview

Written in **Python**, it performs several critical responsibilities:

- **Local Scanner:** Uses `bleak` to scan for the target BLE MAC address and applies a smoothing filter (Medium Moving Average) to calculate its own distance to the target.
- **MQTT Subscriber:** Runs an MQTT client to receive localized readings from the `Helper-Pi`.
- **Sensor Fusion (WLS):** Fuses its own measurements and the Helper's measurements using a **simplified 1D Weighted Least Squares** approach. It calculates the exact position of the target along the 3-meter axis between the two Pis based on an inverse-square distance confidence metric.
- **Backend Sync:** Serializes the aggregated payload and POSTs it directly to the Node.js API.

## Setup & Run

### Finding System Information
Before running the script, you need to configure the network paths and target inputs:
- **Finding the Backend IP (for API_BACKEND_URL):** On the machine running the Node.js server, run `hostname -I` (Linux/Mac) or `ipconfig` (Windows). Form the URL as `http://<IP>:3000/readings`.
- **Finding the Target MAC Address (BLE Device):** Open the terminal on the Raspberry Pi and run:
  1. `bluetoothctl`
  2. `scan on`
  3. Wait for your target device to appear and copy its MAC Address (e.g., `57:06:FA:24:0F:0A`).

1. Make sure you have Mosquitto (or another MQTT broker) running on this machine (`sudo apt install mosquitto`).
2. Install Python requirements:
   ```bash
   pip install -r requirements.txt
   ```
3. Open `main.py` and modify `TARGET_MAC` to match your target beacon.
4. Set the correct `API_BACKEND_URL` pointing to the Node.js server's IP.
5. Run the script:
   ```bash
   python main.py
   ```
