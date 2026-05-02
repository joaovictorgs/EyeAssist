import paho.mqtt.client as mqtt
import json
import time
import socket
import os
import asyncio
from datetime import datetime
from bleak import BleakScanner

# Configuration
HOSTNAME = socket.gethostname()
DEVICE_ID = HOSTNAME

# To get the Broker IP address:
# Run `hostname -I` (Linux/Pi) or `ipconfig` (Windows) on the machine where the MQTT Broker (Mosquitto) is installed.
# You can either change the default IP string below or set the environment variable: export MQTT_BROKER_IP="YOUR_IP"
BROKER_ADDRESS = os.getenv("MQTT_BROKER_IP", "192.168.1.29") 
BROKER_PORT = 1883
TOPIC = f"{DEVICE_ID}/Reading"

# BLE Configuration
# To get the target MAC address using the Raspberry Pi's terminal:
# 1. run bluetoothctl on pi terminal
# 2. write power on
# 3. write scan on
# 4. Find your device name in the list, copy its MAC address (XX:XX:XX:XX:XX:XX), and replace here.
TARGET_MAC = "78:EB:F5:B7:41:18"
CALIBRATION_1M_RSSI = -80
ENVIRONMENT_FACTOR = 2.0 
SMOOTHING_SAMPLES = 5

def calculate_distance(rssi):
    distance = 10 ** ((CALIBRATION_1M_RSSI - rssi) / (10 * ENVIRONMENT_FACTOR))
    return round(distance, 2)

def get_payload(dist_target):
    return json.dumps({
        "timestamp": time.time(),
        "datetime": datetime.utcnow().isoformat() + "Z",
        "device_id": DEVICE_ID,
        "measurements": {
            "distance_to_target": dist_target
        }
    })

async def main():
    print(f"Starting MQTT Publisher (Writer) on host: {HOSTNAME}")
    
    client = mqtt.Client(f"{DEVICE_ID}_Writer_Client")
    
    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT)
        client.loop_start()
        print("Connected to MQTT Broker successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    recent_readings = []

    def detection_callback(device, advertisement_data):
        mac = device.address.upper()
        if mac == TARGET_MAC:
            recent_readings.append(advertisement_data.rssi)

    scanner = BleakScanner(detection_callback)
    await scanner.start()

    try:
        while True:
            await asyncio.sleep(1.0)
            
            if len(recent_readings) >= SMOOTHING_SAMPLES:
                avg_rssi = sum(recent_readings) / len(recent_readings)
                estimated_distance = calculate_distance(avg_rssi)
                
                payload = get_payload(estimated_distance)
                client.publish(TOPIC, payload)
                
                print(f"Reading: RSSI Average={avg_rssi:.1f} dBm | Distance={estimated_distance}m")
                print(f"-> Sending to the topic: '{TOPIC}': {payload}")
                print("-" * 50)
                
    
                recent_readings.clear()
            else:
                pass # Waiting for enough samples to calculate average
            
    except asyncio.CancelledError:
        pass
    finally:
        print("\nStopping writer manually...")
        await scanner.stop()
        client.loop_stop()
        client.disconnect()
        print("Disconnected cleanly.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
