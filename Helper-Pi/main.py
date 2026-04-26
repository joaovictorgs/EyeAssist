import paho.mqtt.client as mqtt
import json
import time
import socket
import os
from datetime import datetime

# Configuration
HOSTNAME = socket.gethostname()
DEVICE_ID = HOSTNAME

BROKER_ADDRESS = os.getenv("MQTT_BROKER_IP", "192.168.1.29") 
BROKER_PORT = 1883
TOPIC = f"{DEVICE_ID}/Reading"

def get_payload(dist_satellite, dist_target):
    return json.dumps({
        "timestamp": time.time(),
        "datetime": datetime.utcnow().isoformat() + "Z",
        "device_id": DEVICE_ID,
        "measurements": {
            "distance_to_satellite": dist_satellite,
            "distance_to_target": dist_target
        }
    })

def main():
    print(f"Starting MQTT Publisher (Writer) on host: {HOSTNAME}")
    
    client = mqtt.Client(f"{DEVICE_ID}_Writer_Client")
    
    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT)
        client.loop_start()
        print("Connected to MQTT Broker successfully!")
    except Exception as e:
        print(f"Connection failed: {e}")
        return

    try:
        while True:
            # TODO: Replace with real RSSI/distance readings
            dist_satellite = 3.51
            dist_target = 1.25

            payload = get_payload(dist_satellite, dist_target)
            client.publish(TOPIC, payload)
            
            print(f"Published to {TOPIC}: {payload}")
            time.sleep(5)
            
    except KeyboardInterrupt:
        print("\nStopping writer manually...")
        client.loop_stop()
        client.disconnect()
        print("Disconnected cleanly.")

if __name__ == "__main__":
    main()
