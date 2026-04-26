import paho.mqtt.client as mqtt
import socket
import json

# Configuration
HOSTNAME = socket.gethostname()
BROKER_ADDRESS = "localhost"
BROKER_PORT = 1883
TOPIC_TO_SUBSCRIBE = "+/Reading"


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker successfully!")
        client.subscribe(TOPIC_TO_SUBSCRIBE)
        print(f"Subscribed to topic: {TOPIC_TO_SUBSCRIBE}")
    else:
        print(f"Connection failed with code: {rc}")


def on_message(client, userdata, msg):
    print(f"\nNew Message on Topic: {msg.topic}\n")
    try:
        data = json.loads(msg.payload.decode())
        print(json.dumps(data, indent=2))
    except json.JSONDecodeError:
        print(f"Raw payload: {msg.payload.decode()}")


def main():
    print(f"Starting MQTT Subscriber (Reader) on host: {HOSTNAME}")

    client = mqtt.Client(f"{HOSTNAME}_Reader_Client")
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        client.connect(BROKER_ADDRESS, BROKER_PORT)
        client.loop_forever()
    except KeyboardInterrupt:
        print("\nStopping reader manually...")
        client.disconnect()
        print("Disconnected cleanly.")
    except Exception as e:
        print(f"Connection failed: {e}")

if __name__ == "__main__":
    main()
