# -*- coding: utf-8 -*-

"""
The GasREST class is used to take the last detection, get the treshold, and set the treshold 
The CameraMQTT class is used to start image recognition. In particular, when it receives messages with 
the topic "MotionDetect", for each message arrived, it will start the Handler class with a thread. 
If the Handler is already active, the timer will be increased, so as not to risk that the camera switches 
off and on again immediately afterwards, just because the timer was over.
"""

import json
import paho.mqtt.client as PahoMQTT
from datetime import datetime
import time
import requests
import cherrypy
from dateutil import tz
from cryptography.fernet import Fernet
from requests.auth import HTTPDigestAuth
from cherrypy.lib import auth_digest
import socket

class GasREST(object):
     
    print("Web avviato")
    exposed = True

    def __init__(self, gas):
           self.gas = gas
      
    def GET(self, *uri, **params):

        if (len(uri) == 2 and uri[0] == 'get' and uri[1] == 'gas'):

            return self.gas.getLastGas()

        elif (len(uri) == 2 and uri[0] == 'get' and uri[1] == 'treshold'):

            return self.gas.getTreshold()
       
    def POST(self, *uri, **params):
         
        if len(uri) == 0:
            raise cherrypy.HTTPError(400)

        mybody = cherrypy.request.body.read()

        try:
            data = json.loads(mybody)
        except:
            raise cherrypy.HTTPError(400)
       
        if (len(uri) == 2 and uri[0] == 'set' and uri[1] == 'treshold'):
             
            print(data)
            self.gas.setTreshold(data["treshold"])
            return "Treshold setted"

class GasMQTT:
     
    def __init__(self, IP_broker, PORT_broker, IP_Catalog, PORT_Catalog, key):
        self.deviceID = 'Gas_device'
        self.broker = IP_broker
        self.port = PORT_broker
        self.IP_Catalog = IP_Catalog
        self.PORT_Catalog = PORT_Catalog
        self.key = key
        
        self._paho_mqtt = PahoMQTT.Client(self.deviceID, False)
        self._paho_mqtt.on_connect = self.Connect
        self._paho_mqtt.on_message = self.MessageReceived
        
        self.topic = ""
        self._isSubscriber = False
        
        # One second of unix time, useful for the first alert (1 is a symbolic value)
        self.timeLastAlert = 1
        self.lastGas = None
        self.lastTime = None
        self.treshold = 150

        
    def Subscribe (self, topic):
        print ("subscribing to %s" % (topic))
        self._isSubscriber = True
        self._paho_mqtt.subscribe(topic, 2)
        self._topic = topic

    def getLastGas (self):
        return "Gas detected: {}\nDatetime: {}".format(self.lastGas, self.lastTime)
    
    def setTreshold (self, newTreshold):
        self.treshold = int(newTreshold)
        
    def getTreshold (self):
        return "The current treshold is {}".format(self.treshold)
         
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

         
        if (msg.topic=="GasDetect"):
             
            message=json.loads(msg.payload)
            value=message["Value"]
            self.lastGas = value
            
            # From UTC to Italy
            italyDatetime = self.utcToItaly(datetime.utcnow())
            # Date to string
            self.lastTime = self.dateTimeToString(italyDatetime)
            # Date to unix
            currentUnix = self.dateTimeToUnix(italyDatetime)
                        
            # If more than 20 minutes have passed...
            if (value > self.treshold and (int(currentUnix-self.timeLastAlert) / 60) > 20):
                
                    URL = 'http://' + self.IP_Catalog + ':' + self.PORT_Catalog + '/get/userslist'
           
                    try:
                         r = requests.get(URL, auth=HTTPDigestAuth('TakeASmile', self.key))
                         r.raise_for_status()
                         
                    except requests.HTTPError as err:
                         raise SystemExit(err)

                    
                    chats = json.loads(r.text)
                 
                    IDs = [x["ID"] for x in chats["chatList"] if x["AllOk"] == True]
                    
                    for ID in IDs:
                        requests.post('https://api.telegram.org/YOUR_BOT_TOKEN/sendMessage', data={'chat_id': ID, 'text': "Attention, a large amount of gas ({}) was detected on date\n{}\nPossible risk of fire!".format(value, self.lastTime)})
                                        
                    # Publish numbers 
                    numbers = [x["PhoneNumber"] for x in chats["chatList"] if x["SMS_ON"] == True and x["PhoneNumber"] != ""]
                    for number in numbers:
                         self.publish("SMS_ALERT_GAS", json.dumps({"number":number}))
                    
                    self.timeLastAlert = currentUnix
            
    def start(self):
        self._paho_mqtt.connect(self.broker , self.port)
        self._paho_mqtt.loop_start()


    def stop (self):
        if self._isSubscriber :
            self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect() 

    def publish(self, topic, number):
         
        # Encrypt numbers and send on the topic "SMS_ALERT"
        message = number.encode("utf-8")
        encrypted_message = Fernet(self.key).encrypt(message).decode("utf-8")
        # Print encrypted message, useful for debug
        print(encrypted_message)
        self._paho_mqtt.publish(topic, encrypted_message, 2)   

     
if __name__ == '__main__':
     
    # Get local ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    s.close()
     
    file = open("configGas.json","r")
    data = json.loads(file.read())

    IP_Catalog = str(data["IP_catalog"])
    PORT_Catalog = str(data["PORT_catalog"])
    key = str(data["encryption_key"])
    my_port = data["MyPort"]
    
    deviceName = "Gas_control"

    file.close()
    
    # Get broker ip and port from the catalog    
    url = "http://" + str(IP_Catalog) + ":" + str(PORT_Catalog)

    try:
        r = requests.get(url + "/get" + "/broker", auth=HTTPDigestAuth('TakeASmile', key))
        r.raise_for_status()
        broker = json.loads(r.text)
        
        IP_broker = broker["IP_broker"]
        PORT_broker = broker["PORT_broker"]
        print ("Broker ip = {}, port = {}".format(IP_broker, PORT_broker))
        
    except requests.HTTPError as err:
        raise SystemExit(err)
     
     
    # Register device to the catalog    
    deviceName = "Gas control"
    
    jsonData = {"NAME":deviceName, "IP":my_ip, "PORT":my_port}
    URL = 'http://' + IP_Catalog + ':' + PORT_Catalog + '/add/device'
 
    try:
        r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', key))
        r.raise_for_status()
     
    except requests.HTTPError as err:
        raise SystemExit(err)
             
          
    gas=GasMQTT(IP_broker, PORT_broker, IP_Catalog, PORT_Catalog, key)
    gas.start()
    gas.Subscribe('GasDetect')
    
    userpassdict = {'TakeASmile':key}
     
          
    conf={
        '/':{
                  
                
                'tools.auth_digest.on': True,
                'tools.auth_digest.realm': 'localhost',
                'tools.auth_digest.get_ha1': auth_digest.get_ha1_dict_plain(userpassdict),
                'tools.auth_digest.key': 'a565c27146791cfb',
                
                'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on':True
         }
    }        
    cherrypy.tree.mount(GasREST(gas),'/',conf)    
    cherrypy.config.update({'server.socket_host': my_ip})
    cherrypy.config.update({'server.socket_port': my_port})
    cherrypy.engine.start()
    cherrypy.engine.block()
