# -*- coding: utf-8 -*-

"""
The CameraREST class is used to take pictures on demand.
The CameraMQTT class is used to start image recognition. In particular, when it receives messages with 
the topic "MotionDetect", for each message arrived, it will start the Handler class with a thread. 
If the Handler is already active, the timer will be increased, so as not to risk that the camera switches 
off and on again immediately afterwards, just because the timer was over.

Note that, having hardware availability (not our case), it is easily possible to add a light that can 
turn on every time image recognition is started. This can be crucial for the night or for times of day 
when the shutters are closed.
"""

import json
import paho.mqtt.client as PahoMQTT
import time
import requests
import cherrypy
from datetime import timezone
from Handler import HandlerClass
import threading
from Snap import takeASnap
from cryptography.fernet import Fernet
from requests.auth import HTTPDigestAuth
from cherrypy.lib import auth_digest
import socket

class MyThread(threading.Thread):

    def __init__(self, threadID, Handler, MQTT):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.Handler = Handler
        self.MQTT = MQTT
        
    def run(self):
        self.Handler.setCameraState(1, self.MQTT)

class CameraREST(object):
     
    exposed = True

    def __init__(self, cam):
           self.cam = cam
      
    def GET(self, *uri, **params):
        
        pass
    
    def POST(self, *uri):
        
        encoding = 'utf-8' 
        mybody = (cherrypy.request.body.read()).decode(encoding)
        print("\n\n%s\n\n" % mybody)
        print(*uri) 

        try:
            data = json.loads(mybody)
        except:
            raise cherrypy.HTTPError(400)

        chat_id = str(data["IDchat"])

        if (len(uri) == 2 and uri[0] == 'get' and uri[1] == 'pic'):

            if (self.cam.Handler.getCameraState() == 0):
                takeASnap()
                   
                requests.post('https://api.telegram.org/YOUR_TOKEN/sendMessage', data={'chat_id': chat_id, 'text': "Here's the picture, please take a smile!"})
                filename = "newSnap.jpg"
                requests.post('https://api.telegram.org/YOUR_TOKEN/sendPhoto', data={'chat_id': chat_id}, files={'photo': open('./{}'.format(filename), 'rb')})
                # Fake post for the promo video
#                requests.post('https://api.telegram.org/YOUR_TOKEN/sendPhoto', data={'chat_id': chat_id}, files={'photo': open('./{}'.format("frame8.png"), 'rb')})
            
            else:
                requests.post('https://api.telegram.org/YOUR_TOKEN/sendMessage', data={'chat_id': chat_id, 'text': "Sorry but the camera is busy, it's probably detecting some intruder..."})



class CameraMQTT:
     
    def __init__(self, IP_broker, PORT_broker, Handler, IP_Catalog, PORT_Catalog, key):
                
        self.deviceID = 'Camera_device'
        self.broker = IP_broker
        self.port = PORT_broker
        self.IP_Catalog = IP_Catalog
        self.PORT_Catalog = PORT_Catalog
        self.key = key
        
        self._paho_mqtt = PahoMQTT.Client(self.deviceID, False)
        self._paho_mqtt.on_connect = self.Connect
        self._paho_mqtt.on_message = self.MessageReceived
        
        self.topic = "MotionDetect"
        self._isSubscriber = False
         
        self.Handler = Handler
        
    def TakeASnap(self):
        if (self.Handler.getCameraState() == 1):
            print("Camera busy, SORRY!")      
        
    def Subscribe (self, topic):
        print ("subscribing to %s" % (topic))
        self._isSubscriber = True
        self._paho_mqtt.subscribe(topic, 2)
        self._topic = topic

         
    def Connect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
          
    def utc_to_local(self, utc_dt):
         return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
     
    def aslocaltimestr(self, utc_dt):
         return self.utc_to_local(utc_dt).strftime('%Y-%m-%d %H:%M:%S.%f %Z%z')
   
    def dateTimeToUnix(self, date):
        return time.mktime(date.timetuple())
        
    def MessageReceived (self, paho_mqtt , userdata, msg):         
         
        if (msg.topic=="MotionDetect"):
                                  
               t = MyThread(1, self.Handler, self)
               t.start()
            
    def start(self):
        self._paho_mqtt.connect(self.broker , self.port)
        self._paho_mqtt.loop_start()


    def stop (self):
        if self._isSubscriber :
            self._paho_mqtt.unsubscribe(self.topic)
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()      
        
    def publish(self, topic, number):
        # Encrypt the number before sending it online, as it is sensitive information       
        message = number.encode("utf-8")
        encrypted_message = Fernet(self.key).encrypt(message).decode("utf-8")
        print(encrypted_message)
        self._paho_mqtt.publish(topic, encrypted_message, 2)   

     
if __name__ == '__main__':
     
    # Get local ip
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    my_ip = s.getsockname()[0]
    s.close()
     
    Handler = HandlerClass()

    file = open("configCamera.json","r")
    data = json.loads(file.read())

    IP_Catalog = data["IP_catalog"]
    PORT_Catalog = data["PORT_catalog"]
    key = str(data["encryption_key"])
    my_port = data["MyPort"]
    
    deviceName = "Camera_control"

    file.close()
    
    # Get broker ip and port from the catalog
    url = "http://" + str(IP_Catalog) + ":" + str(PORT_Catalog)

    try:
        r = requests.get(url + "/get" + "/broker", auth=HTTPDigestAuth('TakeASmile', key))
        r.raise_for_status()
        broker = json.loads(r.text)
        
        IP_broker = broker["IP_broker"]
        PORT_broker = broker["PORT_broker"]
        print ("Broker ip = {}, port = {}".format(str(IP_broker), str(PORT_broker)))
        
    except requests.HTTPError as err:
        raise SystemExit(err)
      

    # Register device to the catalog     
    deviceName = "Camera control"
    
    jsonData = {"NAME":deviceName, "IP":my_ip, "PORT":my_port}
    URL = 'http://' + IP_Catalog + ':' + str(PORT_Catalog) + '/add/device'
 
    try:
        r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', key))
        r.raise_for_status()
     
    except requests.HTTPError as err:
        raise SystemExit(err)
        
    cam=CameraMQTT(IP_broker, PORT_broker, Handler, IP_Catalog, PORT_Catalog, key)
    cam.start()
    cam.Subscribe('MotionDetect')
    
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
    cherrypy.tree.mount(CameraREST(cam),'/',conf)    
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    cherrypy.config.update({'server.socket_port': my_port})
    cherrypy.engine.start()
    cherrypy.engine.block()
