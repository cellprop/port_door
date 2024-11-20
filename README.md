# Door Control System using Raspberry Pi and MQTT

This project implements a door control system using a Raspberry Pi. The Raspberry Pi listens to MQTT messages to control two doors (Door A and Door B) via GPIO pins. When a control message is received, the corresponding GPIO pin is set high or low to open or close the door.

## Features
- Control doors via MQTT messages.
- Use GPIO pins to open and close doors.
- Supports two doors: Door A and Door B.
- Simple JSON message format for door control commands.

## Prerequisites
- **Hardware:** Raspberry Pi (any model with GPIO pins), Door control mechanism connected to GPIO pins (e.g., relays, actuators), Network connection for the Raspberry Pi to communicate with the MQTT broker.
- **Software:** Raspberry Pi OS (or compatible Linux distribution), Python 3 installed on the Raspberry Pi.

## Installation and Configuration
Clone the repository and install dependencies:
```bash
git clone https://github.com/yourusername/door-control-system.git
cd door-control-system
pip3 install paho-mqtt
sudo apt-get install -y python3-rpi.gpio
