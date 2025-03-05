import time
import paho.mqtt.client as mqtt
import json
from gpiozero import LED

# ================= MQTT Configuration ================= #

# MQTT Broker details
MQTT_BROKER = "192.168.68.106"
MQTT_PORT = 1884  # Port for unencrypted MQTT

# ================= Pod Door Configuration ================= #

# Pod door identifiers
POD_ID = 'TD01'
ZONE_ID = 'zone1'
POD_TOPIC = f"{ZONE_ID}{POD_ID}"  # Topic for pod door control

# GPIO pins controlling the pod door actuators
POD_DOOR_PINS = [LED(23), LED(24)]  # [Expansion Control, Retraction Control]

# ================= Port Door Configuration ================= #

# Port door identifiers
PORT_ID = 'P01'
PORT_TOPIC = f"{PORT_ID}portControl"  # Topic for port door control

# GPIO pins controlling the port door actuators
PORT_DOOR_PINS = [LED(17), LED(27)]  # [Expansion Control, Retraction Control]

# ================= MQTT Client Initialization ================= #

client = mqtt.Client()  # Initialize MQTT client


def on_connect(client, userdata, flags, rc):
    """
    Callback function triggered when the MQTT client connects to the broker.
    Subscribes to pod and port door topics upon successful connection.
    """
    if rc == 0:
        print("✅ Connected to MQTT Broker")
        client.subscribe([(POD_TOPIC, 0), (PORT_TOPIC, 0)])
        print(f"📡 Subscribed to topics: {POD_TOPIC} and {PORT_TOPIC}")
    else:
        print(f"❌ Failed to connect, return code: {rc}")


def on_message(client, userdata, msg):
    """
    Callback function triggered when an MQTT message is received.
    Processes messages for pod or port doors based on topic.
    """
    try:
        payload = json.loads(msg.payload.decode())  # Decode JSON payload
        print(f"📩 Received MQTT message on topic: {msg.topic} | Payload: {payload}")

        # Check the topic and route to the appropriate handler
        if msg.topic == POD_TOPIC:
            handle_pod_door(payload)
        elif msg.topic == PORT_TOPIC:
            handle_port_door(payload)
        else:
            print("⚠️ Unknown topic received, ignoring message.")
    except Exception as e:
        print(f"❌ Error processing message: {e}")


# ================= Pod Door Control ================= #

def handle_pod_door(payload):
    """
    Handles opening and closing of the pod door based on MQTT messages.
    Uses GPIO control to drive actuators.
    """
    if payload.get('type') == 'DoorOpening':
        action = payload.get('path')

        if action == "O00000":  # Open pod door
            print(f"🔓 Opening Pod Door at {POD_ID}, {ZONE_ID}...")
            for pin in POD_DOOR_PINS:
                pin.on()  # Activate both pins to expand
            
            print("⏳ Waiting 2 seconds before stopping expansion...")
            time.sleep(2)  # Wait for partial expansion

            POD_DOOR_PINS[1].off()  # Stop expansion
            print(f"⏹ Pod Door expansion stopped midway at {POD_ID}, {ZONE_ID}")

        elif action == "C00000":  # Close pod door
            print(f"🔒 Closing Pod Door at {POD_ID}, {ZONE_ID}...")
            for pin in POD_DOOR_PINS:
                pin.off()  # Deactivate both pins to retract (mechanical stop)
            print(f"✅ Pod Door fully closed at {POD_ID}, {ZONE_ID}")

        else:
            print(f"⚠️ Invalid pod door action received: {action}")


# ================= Port Door Control ================= #

def handle_port_door(payload):
    """
    Handles opening and closing of the port door based on MQTT messages.
    Uses GPIO control to drive actuators.
    """
    if payload.get('type') == 'doorControl':
        door_number = payload.get('message', {}).get('doorNumber')
        signal = payload.get('message', {}).get('signal')

        if door_number == 'A' and signal in ['0', '1']:
            if signal == '1':  # Open port door
                print(f"🔓 Opening Port Door {door_number} at {PORT_ID}...")
                for pin in PORT_DOOR_PINS:
                    pin.on()  # Activate both pins to expand

                print("⏳ Waiting 2 seconds before stopping expansion...")
                time.sleep(2)  # Wait for partial expansion

                PORT_DOOR_PINS[1].off()  # Stop expansion
                print(f"⏹ Port Door expansion stopped midway at {PORT_ID}")

            else:  # signal == '0' → Close port door
                print(f"🔒 Closing Port Door {door_number} at {PORT_ID}...")
                for pin in PORT_DOOR_PINS:
                    pin.off()  # Deactivate both pins to retract (mechanical stop)
                print(f"✅ Port Door {door_number} fully closed at {PORT_ID}")

        else:
            print(f"⚠️ Invalid port door action received: {door_number}, {signal}")


# ================= MQTT Client Setup ================= #

# Assign callback functions to the MQTT client
client.on_connect = on_connect
client.on_message = on_message

# Connect to the MQTT Broker
print("🔄 Connecting to MQTT Broker...")
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# ================= Main Loop ================= #
try:
    print("🚀 Starting MQTT event loop...")
    client.loop_forever()  # Keep listening for messages
except KeyboardInterrupt:
    print("🛑 Exiting program due to KeyboardInterrupt")
finally:
    print("🔚 Program terminated")