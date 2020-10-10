# -*- coding: utf-8 -*-

"""
This MQTT subscriber listens to receive encrypted numbers. Once a number is received, it is decrypted
 and a text message is sent. After that, the number is entered into a dictionary
{number: last sent} and if at least 30 minutes have not passed, there will be no further SMS to that number.

Note that unfortunately Twilio offers, for the free plan, the possibility to sending only to one number.
However, sending to multiple users has been tested and captured by the try except.
"""

import json
import paho.mqtt.client as PahoMQTT
from datetime import datetime
import time
import socket
from dateutil import tz
from twilio.rest import Client
from cryptography.fernet import Fernet
import requests
from requests.auth import HTTPDigestAuth

class SMSMQTT:
     
    def __init__(self, IP_broker, PORT_broker, key):
        self.deviceID = 'SMS_device3'
        self.broker = IP_broker
        self.port = PORT_broker
        self.key = key
        
        self._paho_mqtt = PahoMQTT.Client(self.deviceID, False)
        self._paho_mqtt.on_connect = self.Connect
        self._paho_mqtt.on_message = self.MessageReceived
        
        self.topic = ""
        self._isSubscriber = False       
        
        self.lastGas = None
        self.lastTime = None
        self.treshold = 50
        # Dict that will contain the number and last date of sending the SMS
        self.numbersDict = {}
        self.minutes = 30

        
    def Subscribe (self, topic):
        print ("subscribing to %s" % (topic))
        self._isSubscriber = True
        self._paho_mqtt.subscribe(topic, 2)
        self._topic = topic
         
    def Connect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
        
    def utcToItaly(self, date):
        newDatetime = date.replace(tzinfo=tz.gettz('UTC'))
        return newDatetime.astimezone(tz.gettz('Europe/Rome'))
   
    def dateTimeToString(self, date):
        return date.strftime("%Y-%m-%d %H:%M:%S")
   
    def dateTimeToUnix(self, date):
        return time.mktime(date.timetuple())
        
    def MessageReceived (self, paho_mqtt , userdata, msg):
        
             
        if (msg.topic == "SMS_ALERT_GAS" or msg.topic == "SMS_ALERT_CAM"):
                      
            # Decrypt
            decrypted_message = Fernet(key).decrypt(msg.payload).decode("utf-8")
                                 
            message=json.loads(decrypted_message)
            number=message["number"]
            
            # From UTC to Italy
            italyDatetime = self.utcToItaly(datetime.utcnow())
                       
            # Current unix
            currentUnix = self.dateTimeToUnix(italyDatetime)            

            # If the number in the dictionary is missing or more than 30 minutes has passed
            if (number not in self.numbersDict or ((number in self.numbersDict) and (int(currentUnix-self.numbersDict[number])/ 60) > self.minutes)):
                            
                    print ("Sending an SMS")
                    
                    account_sid = 'YOUR_ACCOUNT_SID'
                    auth_token = 'YOUR_TOKEN'
                    
                    client = Client(account_sid, auth_token)
                    
                    if (msg.topic == "SMS_ALERT_GAS"):
                    
                         try:
                             message = client.messages \
                                         .create(
                                  body="- ATTENTION - \n- HIGHLY DANGEROUS GAS LEVELS - \nIt is advisable to check the situation on Telegram or from the dashboard \nhttps://freeboard.io/board/x5gqGh",
                                  from_='+12029331705',
                                  to='+39' + str(number)
                              )
                         except:
                             print("Message not sent due to a Twilio error")
                    else:
                         try:
                             message = client.messages \
                                         .create(
                                  body="- ATTENTION - \n- INTRUDER DETECTED - \nIt is advisable to check the situation on Telegram or from the dashboard \nhttps://freeboard.io/board/x5gqGh",
                                  from_='+12029331705',
                                  to='+39' + str(number)
                              )
                         except:
                              print("Message not sent due to a Twilio error")
                     
                    # Put the number in the dict, or update the value
                    self.numbersDict[number] = currentUnix

            
    def start(self):
        print("Started")
        self._paho_mqtt.connect(self.broker , self.port)
        self.Subscribe('#')
        self._paho_mqtt.loop_forever()
        #print("Partito")


    def stop (self):
        if self._isSubscriber :
            self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
        print("Stopped")

     
if __name__ == '__main__':
         

    file = open("configSMS.json","r")
    data = json.loads(file.read())
    file.close() 

    key = str(data["encryption_key"]) 
    IP_Catalog = str(data["IP_catalog"])
    PORT_Catalog = str(data["PORT_catalog"])
    my_port = data["MyPort"]
    
    # Get broker ip and port from the catalog
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
        raise SystemExit(err)


    sms=SMSMQTT(IP_broker, PORT_broker, key)
    sms.start()
    time.sleep(1)

