import time
import paho.mqtt.client as mqtt
import json
from gpiozero import LED

# MQTT Configuration
MQTT_BROKER = "192.168.68.106"
MQTT_PORT = 1884

# Pod Door Configuration
POD_ID = 'TD01'
ZONE_ID = 'zone1'
POD_TOPIC = f"{ZONE_ID}{POD_ID}"
POD_DOOR_PINS = [LED(23), LED(24)]  # GPIO 23 and 24 control the pod door

# Port Door Configuration
PORT_ID = 'P01'
PORT_TOPIC = f"{PORT_ID}portControl"
PORT_DOOR_PINS = [LED(17), LED(27)]  # GPIO 17 and 27 control the port door

# MQTT Client Initialization
client = mqtt.Client()


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker")
        client.subscribe([(POD_TOPIC, 0), (PORT_TOPIC, 0)])  
        print(f"Subscribed to: {POD_TOPIC} and {PORT_TOPIC}")
    else:
        print(f"Failed to connect, return code {rc}")


def on_message(client, userdata, msg):
    try:
        payload = json.loads(msg.payload.decode())
        print("Received MQTT message on topic:", msg.topic, "| Payload:", payload)
        
        if msg.topic == POD_TOPIC:
            handle_pod_door(payload)
        elif msg.topic == PORT_TOPIC:
            handle_port_door(payload)
        else:
            print("Unknown topic received")
    except Exception as e:
        print("Error processing message:", e)


# Function to handle pod door control
def handle_pod_door(payload):
    if payload.get('type') == 'DoorOpening':
        action = payload.get('path')
        
        if action == "O00000":
            print(f"Opening Pod Door at {POD_ID}, {ZONE_ID}...")
            for pin in POD_DOOR_PINS:
                pin.on()
            
            time.sleep(2)  # Wait 2 seconds

            POD_DOOR_PINS[1].off()  # Stop expansion midway
            print(f"Pod Door stopped midway at: {POD_ID}, {ZONE_ID}")

        elif action == "C00000":
            print(f"Closing Pod Door at {POD_ID}, {ZONE_ID}...")
            for pin in POD_DOOR_PINS:
                pin.off()
            print(f"Pod Door fully closed at: {POD_ID}, {ZONE_ID}")

        else:
            print("Invalid pod door action received")


# Function to handle port door control
def handle_port_door(payload):
    if payload.get('type') == 'doorControl':
        door_number = payload.get('message', {}).get('doorNumber')
        signal = payload.get('message', {}).get('signal')

        if door_number == 'A' and signal in ['0', '1']:
            if signal == '1':
                print(f"Opening Port Door {door_number} at {PORT_ID}...")
                for pin in PORT_DOOR_PINS:
                    pin.on()
                
                time.sleep(2)  # Wait 2 seconds

                PORT_DOOR_PINS[1].off()  # Stop expansion midway
                print(f"Port Door {door_number} stopped midway at: {PORT_ID}")

            else:  # signal == '0'
                print(f"Closing Port Door {door_number} at {PORT_ID}...")
                for pin in PORT_DOOR_PINS:
                    pin.off()
                print(f"Port Door {door_number} fully closed at: {PORT_ID}")

        else:
            print(f"Invalid port door action received: {door_number}, {signal}")


# Assign Callbacks
client.on_connect = on_connect
client.on_message = on_message

# Connect to MQTT Broker
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# Start MQTT Loop
try:
    client.loop_forever()
except KeyboardInterrupt:
    print("Exiting program")
finally:
    print("Program terminated")