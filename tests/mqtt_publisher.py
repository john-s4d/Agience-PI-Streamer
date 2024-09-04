import paho.mqtt.client as mqtt 
from random import randrange, uniform
import time

mqttBroker ="44.209.26.208" 
port= 1883

client = mqtt.Client("publisherr1")
client.username_pw_set(username="audiostream", password="7snLBemg1T")
client.connect(mqttBroker) 

while True:
    randNumber = uniform(20.0, 21.0)
    client.publish("audio/stream", str(randNumber))
    print("Just published " + str(randNumber) + " to topic TEMPERATURE")
    time.sleep(1)