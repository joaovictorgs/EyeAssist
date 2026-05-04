# Helper-Pi

This module runs on the secondary Raspberry Pi node (the "Helper") deployed in the environment.

## Overview

Written in **Python**, this script is responsible for edge scanning:

- Uses `bleak` to scan asynchronously for the target BLE MAC Address.
- Accumulates raw RSSI signals and applies a **Simple Moving Average (Low-Pass Filter)** using a buffer of samples to reduce multipath interference.
- Converts the smoothed RSSI into a distance estimation.
- Publishes the telemetry (name, distance, RSSI, timestamp) over **MQTT** to the generic `+/Reading` topic on the Main-Pi broker.

## Setup & Run

### Finding System Information
Before running the script, you might need to find specific network and device information:
- **Finding the Main-Pi IP (for MQTT_BROKER_IP):** Connect to the Main-Pi terminal and run `hostname -I`.
- **Finding the Target MAC Address (BLE Device):** Open the terminal on the Raspberry Pi and run:
  1. `bluetoothctl`
  2. `scan on`
  3. Look for your target device (e.g., your smartphone) and copy the MAC Address formatted as `XX:XX:XX:XX:XX:XX`.

1. Install Python requirements:
   ```bash
   pip install -r requirements.txt
   ```
2. Open `main.py` and ensure the `TARGET_MAC` matches your BLE device.
3. Ensure you have the `MQTT_BROKER_IP` environment variable set to point to the Main-Pi's IP address (or update the `BROKER_ADDRESS` string directly in `main.py`).
4. Run the script:
   ```bash
   python main.py
   ```
