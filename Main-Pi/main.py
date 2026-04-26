import paho.mqtt.client as mqtt
import json
import time

id = "Main"

client_name = id + '_EyeAssist'
client_Reading_topic = id + '/Reading'

mqtt_client = mqtt.Client(client_name)
mqtt_client.connect('localhost', 1883)

mqtt_client.loop_start()

print("MQTT connected!")

while True:
    telemetry = json.dumps({'temperature' : 'aaaa'})

    print("Sending telemetry ", telemetry)

    mqtt_client.publish(client_Reading_topic, telemetry)

    time.sleep(5)