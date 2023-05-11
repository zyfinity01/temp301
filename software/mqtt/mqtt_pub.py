import paho.mqtt.client as paho
import sys
import json

client = paho.Client()

if client.connect("test.mosquitto.org", 1883, 60) != 0:
    print("Could not connect to MQTT Broker!")
    sys.exit(-1)

payload = {"DateTime": "04/05/23", "temperature": 15, "pressure": "3pa", "rainfall": 6}
payload = json.dumps(payload)

client.publish("test/environmentMonitoring/DomsTest", payload, 0)

client.disconnect()
