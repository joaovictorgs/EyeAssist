import paho.mqtt.client as mqtt
import socket
import json
import time
import asyncio
import math
import requests
from bleak import BleakScanner

# Configuration
HOSTNAME = socket.gethostname()
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
TOPIC_TO_SUBSCRIBE = "+/Reading"

API_BACKEND_URL = "http://192.168.1.16:3000/readings" # Updated to match backend route

# BLE Configuration
TARGET_MAC = "57:06:FA:24:0F:0A" # Check your target phone's MAC
CALIBRATION_1M_RSSI = -80
ENVIRONMENT_FACTOR = 2.0
SMOOTHING_SAMPLES = 5
DISTANCE_BETWEEN_PIS = 3.0

# Global dictionary to store the latest readings from each anchor (Pi)
# They will expire or be overwritten based on their arrival time
latest_readings = {}
recent_rssi_buffer = []

def calculate_distance(rssi):
    distance = 10 ** ((CALIBRATION_1M_RSSI - rssi) / (10 * ENVIRONMENT_FACTOR))
    return round(distance, 2)

def calculate_position_wls(main_distance, helper_distance):
    if main_distance is None or helper_distance is None:
        return 0.5

    L = DISTANCE_BETWEEN_PIS
    x1 = main_distance
    x2 = L - helper_distance

    eps = 1e-6
    w1 = 1.0 / ((main_distance + 0.1) ** 2 + eps)
    w2 = 1.0 / ((helper_distance + 0.1) ** 2 + eps)

    denom = (w1 + w2)
    if denom == 0:
        return 0.5

    x = (w1 * x1 + w2 * x2) / denom
    x = max(0.0, min(L, x))
    ratio = round(x / L, 3)
    return ratio

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
        device_id = data.get("name", msg.topic.split('/')[0])
        distance = data.get("distance")
        rssi_raw = data.get("rssi_raw")
        read_timestamp = data.get("timestamp", time.time())
        
        if distance is not None:
            print(f"Received MQTT reading from '{device_id}': {distance}m (RSSI: {rssi_raw})")
            # Store the reading based on the sender device
            latest_readings[device_id] = {
                "distance": distance,
                "rssi_raw": rssi_raw,
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
                    "rssi_raw": avg_rssi,
                    "timestamp": time.time()
                }

def pack_and_send_to_db():
    now = time.time()
    active_anchors = []
    main_distance = None
    helper_distance = None
    main_rssi = None
    helper_rssi = None
    
    # Filter out data older than 15 seconds
    for device_id, info in list(latest_readings.items()):
        if (now - info["timestamp"]) < 15.0:
            active_anchors.append({
                "name": device_id,
                "distance": info["distance"],
                "rssi": round(info.get("rssi_raw", -100), 1)
            })
            if device_id == HOSTNAME:
                main_distance = info["distance"]
                main_rssi = info.get("rssi_raw")
            else:
                helper_distance = info["distance"]
                helper_rssi = info.get("rssi_raw")

    # We need both anchors to calculate position properly
    if main_distance is not None and helper_distance is not None:
        # Use simple distance-based WLS fusion
        position_ratio = calculate_position_wls(main_distance, helper_distance)
        position_meters = round(position_ratio * DISTANCE_BETWEEN_PIS, 2)
        
        payload_bd = {
            "timestamp_sync": now,
            "target_mac": TARGET_MAC,
            "anchors": active_anchors,
            "estimated_position_ratio": position_ratio,
            "estimated_position_meters": position_meters,
            "status": "tracking"
        }

        payload_json = json.dumps(payload_bd, indent=2)
        print("\n--- PREPARING TO SEND TO API (EXPRESS/MONGO) ---")
        print(payload_json)
        
        try:
            response = requests.post(API_BACKEND_URL, json=payload_bd, timeout=2)
            print(f"Sent to API. Status Code: {response.status_code}")
        except Exception as e:
            print(f"Failed to reach API: {e}")
                    
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
