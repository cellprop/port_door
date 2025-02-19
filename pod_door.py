import time
import paho.mqtt.client as mqtt
import json
from gpiozero import LED

# MQTT setup
MQTT_BROKER = "192.168.68.106"  # Replace with your broker's IP
MQTT_PORT = 1884
pod_id = 'TD01'
zone_id = 'zone1'
MQTT_TOPIC = f"{zone_id}{pod_id}"  # Match the new topic format

# Define GPIO pin for the door
door = LED(23)  # Directly assign GPIO pin

# MQTT Client initialization
client = mqtt.Client()

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

# Callback when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print("Received MQTT message:", payload)  # Debug print
        
        if payload.get('type') == 'DoorOpening':
            action = payload.get('path')
            process_door_action(action)
        else:
            print("Invalid message format:", payload)
    except Exception as e:
        print("Error processing message:", e)

def process_door_action(action):
    """Controls the door based on the received action."""
    if action == "O00000":
        door.on()
        print(f"Door opened at port: {pod_id}, {zone_id}")
    elif action == "C00000":
        door.off()
        print(f"Door closed at port: {pod_id}, {zone_id}")
    else:
        print(f"Invalid door action received: {action}")

# Assign callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start the MQTT client loop
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Exiting program")
finally:
    print("Program terminated")