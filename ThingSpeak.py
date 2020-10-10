# -*- coding: utf-8 -*-

"""
This subscriber takes care of uploading the various surveys to ThingSpeak. 
Unfortunately the free version allows an update every 15 seconds, but it is still useful and pleasant 
to have a graph in real time.
"""

import json
import paho.mqtt.client as PahoMQTT
from urllib.request import urlopen
import requests
from requests.auth import HTTPDigestAuth
import sys
import socket

class ThingSpeak:
     
    def __init__(self, IP_broker, PORT_broker, api_key, key):
        self.deviceID = 'TaS_ThingSpeak'
        self.broker = IP_broker
        self.port = PORT_broker
        self.key = api_key
        self.digest_key = key
        
        self._isSubscriber = False
        self._paho_mqtt = PahoMQTT.Client(self.deviceID, False)
        self._paho_mqtt.on_connect = self.Connect
        self._paho_mqtt.on_message = self.MessageReceived
        self.flag1 = 0
        self.flag2 = 0
                
    def Subscribe (self, topic):
        
        print ("subscribing to %s" % (topic))
        # subscribe for a topic
        self._isSubscriber = True
        self._paho_mqtt.subscribe(topic, 2)
        self._topic = topic

    def Connect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
        
    def MessageReceived (self, paho_mqtt , userdata, msg):        
     
        if (msg.topic=="MotionDetect"):

            print("Mov rilevato")
            self.flag1 = 1
            
        if (msg.topic=="GasDetect"):
             
            message=json.loads(msg.payload)
            value = int(message["Value"])
            print(value)
            self.flag2 = 1
            
        # If you received both gas and movement, update both                               
        if (self.flag1 == 1 and self.flag2 == 1):
            urlopen("https://api.thingspeak.com/update?api_key={}&field1={}&field2={}".format(self.key, 1, value))
            self.flag1 = 0
            self.flag2 = 0

        # If you received the gas but not the movement, just update the movement                     
        elif (self.flag1 == 0 and self.flag2 == 1):
            urlopen("https://api.thingspeak.com/update?api_key={}&field1={}&field2={}".format(self.key, 0, value))
            self.flag1 = 0
            self.flag2 = 0

         
    def start(self):
        self._paho_mqtt.connect(self.broker , self.port)
        self.Subscribe('#')
        self._paho_mqtt.loop_forever()


    def stop (self):
        if self._isSubscriber :
            self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()

if __name__ == "__main__":
     
     
    file = open("configTSpeak.json","r")
    data = json.loads(file.read())
    file.close() 
    
    api_key = str(data["api_key"]) 
    key = str(data["encryption_key"]) 
    IP_Catalog = str(data["IP_catalog"])
    PORT_Catalog = str(data["PORT_catalog"])
    my_port = data["MyPort"]

    url = "http://" + str(IP_Catalog) + ":" + str(PORT_Catalog)

    try:
        r = requests.get(url + "/get" + "/broker", auth=HTTPDigestAuth('TakeASmile', key))
        r.raise_for_status()
        broker = json.loads(r.text)
        print(broker)
        
        IP_broker = broker["IP_broker"]
        PORT_broker = broker["PORT_broker"]
        print ("Broker ip = {}, port = {}".format(IP_broker, PORT_broker))
        
    except requests.HTTPError as err:
        print (err)
        sys.exit()    
     
    
    ts=ThingSpeak(IP_broker, PORT_broker, api_key, key)
    ts.start()

