import time
import paho.mqtt.client as mqtt
import json
import RPi.GPIO as GPIO

# MQTT setup
MQTT_BROKER = "192.168.68.106"  # Replace with your MQTT broker IP or domain
MQTT_PORT = 1884  # Default MQTT port
port_id = 'port01'  # Define your port_id
MQTT_TOPIC = port_id + 'portControl'  # Topic to subscribe to

# GPIO setup
GPIO.setmode(GPIO.BCM)  # Use BCM numbering

# Define GPIO pins for Door A and Door B
DOOR_PINS = {
    'A': 17,  # Replace with your actual GPIO pin number for Door A
    'B': 27   # Replace with your actual GPIO pin number for Door B
}

# Setup GPIO pins
for pin in DOOR_PINS.values():
    GPIO.setup(pin, GPIO.OUT)
    GPIO.output(pin, GPIO.LOW)  # Initialize pins to LOW (doors closed)

# MQTT Client initialization
client = mqtt.Client()

# Callback when the client receives a CONNACK response from the server
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        # Subscribe to the topic
        client.subscribe(MQTT_TOPIC)
        print(f"Subscribed to topic: {MQTT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")

# Callback when a PUBLISH message is received from the server
def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        message_type = payload.get('type')
        message_content = payload.get('message')
        
        if message_type == 'doorControl':
            door_number = message_content.get('doorNumber')
            signal = message_content.get('signal')
            control_door(door_number, signal)
        else:
            print("Invalid message type received")
    except Exception as e:
        print("Error processing message:", e)

def control_door(door_number, signal):
    # Use door_number and signal to control the GPIO pin
    if door_number in DOOR_PINS and signal in [0, 1]:
        pin = DOOR_PINS[door_number]
        GPIO.output(pin, GPIO.HIGH if signal == 1 else GPIO.LOW)
        action = "opened" if signal == 1 else "closed"
        print(f"Door {door_number} {action}")
    else:
        print("Invalid door number or signal received")

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
    GPIO.cleanup()