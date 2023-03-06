import paho.mqtt.client as paho
import sys

client = paho.Client()

if client.connect("localhost", 1883, 60) != 0:
    print("Could not connect to MQTT Broker!")
    sys.exit(-1)

client.publish("test/status", "Hello World from louis!", 0)

client.disconnect()
