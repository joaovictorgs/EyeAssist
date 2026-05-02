import paho.mqtt.client as mqtt
import socket
import json
import time
import asyncio
import math
from bleak import BleakScanner

# Configuration
HOSTNAME = socket.gethostname()
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
TOPIC_TO_SUBSCRIBE = "+/Reading"

API_BACKEND_URL = "http://192.168.1.16:3000/api/location" # Change to your PC's IP

# BLE Configuration
TARGET_MAC = "78:EB:F5:B7:41:18" # Check your target phone's MAC
CALIBRATION_1M_RSSI = -80
ENVIRONMENT_FACTOR = 2.0
SMOOTHING_SAMPLES = 5

# Global dictionary to store the latest readings from each anchor (Pi)
# They will expire or be overwritten based on their arrival time
latest_readings = {}
recent_rssi_buffer = []

def calculate_distance(rssi):
    distance = 10 ** ((CALIBRATION_1M_RSSI - rssi) / (10 * ENVIRONMENT_FACTOR))
    return round(distance, 2)

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker successfully!")
        client.subscribe(TOPIC_TO_SUBSCRIBE)
        print(f"Subscribing to wildcard topic: {TOPIC_TO_SUBSCRIBE}")
    else:
        print(f"Connection failed with code: {rc}")

def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        
        # Get the device ID that sent the message (e.g., "Satelite" or "Main")
        device_id = data.get("device_id", msg.topic.split('/')[0])
        distance = data.get("measurements", {}).get("distance_to_target")
        read_timestamp = data.get("timestamp", time.time())
        
        if distance is not None:
            print(f"Received MQTT reading from '{device_id}': {distance}m")
            # Store the reading based on the sender device
            latest_readings[device_id] = {
                "distance": distance,
                "timestamp": read_timestamp
            }
            
    except Exception as e:
        print(f"Error processing MQTT message: {e}")

def detection_callback(device, advertisement_data):
    mac = device.address.upper()
    if mac == TARGET_MAC:
        # Add to buffer if we haven't reached the limit yet
        if len(recent_rssi_buffer) < SMOOTHING_SAMPLES:
            recent_rssi_buffer.append(advertisement_data.rssi)
            
            # The moment we hit the required samples, calculate and save!
            if len(recent_rssi_buffer) == SMOOTHING_SAMPLES:
                avg_rssi = sum(recent_rssi_buffer) / len(recent_rssi_buffer)
                estimated_distance = calculate_distance(avg_rssi)
                
                print(f"Local BLE reading ready: {estimated_distance}m (Avg RSSI: {avg_rssi:.1f})")
                
                latest_readings[HOSTNAME] = {
                    "distance": estimated_distance,
                    "timestamp": time.time()
                }

def pack_and_send_to_db():
    now = time.time()
    valid_readings = {}
    
    # Filter out data that arrived more than 15 seconds ago to avoid phantom readings
    for device_id, info in latest_readings.items():
        if (now - info["timestamp"]) < 15.0:
            valid_readings[device_id] = info["distance"]

    if len(valid_readings) >= 2:
        # Pack the data into the official format for the Database/Backend
        payload_bd = {
            "timestamp_sync": now,
            "target_mac": TARGET_MAC,
            "anchors": valid_readings,
            "status": "tracking"
        }

        payload_json = json.dumps(payload_bd, indent=2)
        print("\n--- PREPARING TO SEND TO API (EXPRESS/MONGO) ---")
        print(payload_json)
        
        # clear the arrays to reset the loop and wait for fresh values!
        latest_readings.clear()
        recent_rssi_buffer.clear()

async def async_main():
    print(f"Starting Main (Reader & API Sender) on host: {HOSTNAME}")

    # Set up MQTT (runs in its own background thread automatically)
    client = mqtt.Client(f"{HOSTNAME}_Aggregator_Client")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT)
        client.loop_start() 
        
        # Set up BLE Scanner
        scanner = BleakScanner(detection_callback)
        await scanner.start()
        print(f"BLE Scanner Started. Listening for {TARGET_MAC}")

        while True:
            # Check every second if we have enough data (Main + Satellites) to dispatch
            await asyncio.sleep(1.0)
            pack_and_send_to_db()
            
    except asyncio.CancelledError:
        pass
    except KeyboardInterrupt:
        print("\nStopping Aggregator manually...")
    except Exception as e:
        print(f"Fatal Error: {e}")
    finally:
        client.loop_stop()
        client.disconnect()
        await scanner.stop()
        print("Shutdown complete.")

if __name__ == "__main__":
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        pass
