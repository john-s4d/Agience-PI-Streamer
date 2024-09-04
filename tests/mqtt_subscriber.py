import paho.mqtt.client as mqtt
import time

def on_message(client, userdata, message):
    print("received message: " ,str(message.payload.decode("utf-8")))

mqttBroker ="44.209.26.208"
port = 1883

client = mqtt.Client("Smartphone")
client.username_pw_set(username="audiostream", password="7snLBemg1T")
client.connect(mqttBroker, port) 

client.loop_start()

client.subscribe("audio/stream")
client.on_message=on_message 

time.sleep(30)
client.loop_stop()