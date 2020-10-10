# -*- coding: utf-8 -*-

"""
This script to start image recognition via Google Coral is a modification to these two following scripts:
https://github.com/tensorflow/tensorflow/blob/master/tensorflow/lite/examples/python/label_image.py
https://github.com/EdjeElectronics/TensorFlow-Lite-Object-Detection-on-Android-and-Raspberry-Pi/blob/master/TFLite_detection_webcam.py

In particular, it was necessary, with respect to the original codes:
- introduce a handler class for increasing the timer, so as to make it dynamic
- the acquisition of frames to be sent on Telegram
- sending photos on Telegram
- sending user numbers to the SMS microservice via MQTT encrypted messages
"""

import os
import cv2
import numpy as np
import time
import json
from threading import Thread
import importlib.util
import requests
from datetime import timezone
from requests.auth import HTTPDigestAuth

class VideoStream:
     
    def __init__(self, MQTT, resolution=(1080,720),framerate=30):
         
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        self.stream.set(3,resolution[0])
        self.stream.set(4,resolution[1])
        
        self.startTime = time.time()
        self.initialTime = time.time()
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

        # Variable to control when the camera is stopped
        self.stopped = False
        self.SMS_Flag = 0

        self.thread = None
        self.MQTT = MQTT
        self.key = MQTT.key
        
        # Read the json and create two lists, one for SMS and one for Telegram
        URL = 'http://' + MQTT.IP_Catalog + ':' + str(MQTT.PORT_Catalog) + '/get/userslist'
 
        try:
            r = requests.get(URL, auth=HTTPDigestAuth('TakeASmile', self.key))
            r.raise_for_status()
          
        except requests.HTTPError as err:
            raise SystemExit(err)
 
     
        self.chats = json.loads(r.text)
        
        # Filter on SMS_ON = True and number inserted 
        self.numbers = [x["PhoneNumber"] for x in self.chats["chatList"] if x["SMS_ON"] == True and x["PhoneNumber"] != ""]
        # Take all IDs with AllOk = True, otherwise a person who is not logged in but who has talked to the bot receives notifications
        self.IDs = [x["ID"] for x in self.chats["chatList"] if x["AllOk"] == True]
        
        
    def utc_to_local(self, utc_dt):
         return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)
     
    def aslocaltimestr(self, utc_dt):
         return self.utc_to_local(utc_dt).strftime('%Y-%m-%d %H:%M:%S.%f %Z%z')

    def start(self, Handler):
         
          self.thread = Thread(target=self.update,args=())
          self.thread.start()
                    
          self.startTime = time.time()        
          
          MODEL_NAME = "Sample_TFLite_model" 
                    
          GRAPH_NAME = 'edgetpu.tflite'
          LABELMAP_NAME = 'labelmap.txt'
          min_conf_threshold = float(0.5)
          resW, resH = ('1080x720').split('x')
          imW, imH = int(resW), int(resH)
        
          pkg = importlib.util.find_spec('tensorflow')
          
          if pkg is None:
              from tflite_runtime.interpreter import Interpreter
              from tflite_runtime.interpreter import load_delegate
          else:
              from tensorflow.lite.python.interpreter import Interpreter
              from tensorflow.lite.python.interpreter import load_delegate
                       
          CWD_PATH = os.getcwd()          
          PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,GRAPH_NAME)
          
          PATH_TO_LABELS = os.path.join(CWD_PATH,MODEL_NAME,LABELMAP_NAME)
          
          # Load the label map
          with open(PATH_TO_LABELS, 'r') as f:
              labels = [line.strip() for line in f.readlines()]
          
          # BUG of Tensorflow: first label is '???', which has to be removed.
          if labels[0] == '???':
              del(labels[0])
          
          # Load the Tensorflow Lite model.
          interpreter = Interpreter(model_path=PATH_TO_CKPT,
                                   experimental_delegates=[load_delegate('libedgetpu.so.1.0')])
    
          interpreter.allocate_tensors()
          
          # Get model details
          input_details = interpreter.get_input_details()
          output_details = interpreter.get_output_details()
          height = input_details[0]['shape'][1]
          width = input_details[0]['shape'][2]
          
          floating_model = (input_details[0]['dtype'] == np.float32)
          
          input_mean = 127.5
          input_std = 127.5
          
          # Initialize frame rate calculation
          frame_rate_calc = 1
          freq = cv2.getTickFrequency()        
          
          # To save each photo of every run with a different name.
          # On second boot the photos will be overwritten, in order to not consume too much space
          pic_counter = 0
          
          # Every 10 frames captured where you spot a thief, take a picture
          counter = 0

          self.SMS_Flag = 0                

          while True:
               
              # Increment time if the flag was changed to 1 
              if (Handler.getTimeFlag() == 1):
                  self.startTime = time.time()
                  Handler.setTimeFlag(0)
                  print("Time incremented")
          
              # Stops everything after 20 seconds from the last timer
              if (time.time() >= self.startTime + 20):
                  Handler.setCameraState(0, self.MQTT)
                  print("Camera STOPPED after {}".format(time.time() - self.initialTime))
                  break
          
              # Start timer (for calculating frame rate)
              t1 = cv2.getTickCount()
          
              # Grab frame from video stream
              frame1 = self.read()
          
              # Acquire frame and resize to expected shape [1xHxWx3]
              frame = frame1.copy()
              frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
              frame_resized = cv2.resize(frame_rgb, (width, height))
              input_data = np.expand_dims(frame_resized, axis=0)

              # Normalize pixel values if using a floating model (i.e. if model is non-quantized)
              if floating_model:
                  input_data = (np.float32(input_data) - input_mean) / input_std
          
              # Perform the actual detection by running the model with the image as input
              interpreter.set_tensor(input_details[0]['index'],input_data)
              interpreter.invoke()
          
              # Retrieve detection results
              boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
              classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
              scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects
              #num = interpreter.get_tensor(output_details[3]['index'])[0]  # Total number of detected objects (inaccurate and not needed)

              fakeFlag = 1

              # Loop over all detections and draw detection box if confidence is above minimum threshold
              for i in range(len(scores)):
                  if ((scores[i] > min_conf_threshold) and (scores[i] <= 1.0) and classes[i] == 0):
          
                      counter += 1
                      # Get bounding box coordinates and draw box
                      # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                      ymin = int(max(1,(boxes[i][0] * imH)))
                      xmin = int(max(1,(boxes[i][1] * imW)))
                      ymax = int(min(imH,(boxes[i][2] * imH)))
                      xmax = int(min(imW,(boxes[i][3] * imW)))
                      
                      cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (255, 0, 255), 2)
          
                      # Draw label
                      object_name = labels[int(classes[i])] # Look up object name from "labels" array using class index
                      label = '%s: %d%%' % (object_name, int(scores[i]*100)) # Example: 'person: 72%'
                      labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 1) # Get font size
                      label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
                      cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
                      cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 0), 1) # Draw label text
          
                  # Fakeflag for the promo video
                  if (fakeFlag == 0):  
                      names = ["Frame1.png", "Frame3.png", "Frame4.png", "Frame5.png", "Frame6.png"]
                      requests.post('https://api.telegram.org/YOUR_TOKEN/sendMessage', data={'chat_id': 297501031, 'text': "Attention, a human presence has been detected in the house!\nHere are the photos:"})
                      for i in range(len(names)):

                          requests.post('https://api.telegram.org/YOUR_TOKEN/sendPhoto', data={'chat_id': 297501031}, files={'photo': open('./{}'.format(names[i]), 'rb')})
                          time.sleep(2)
                      fakeFlag = 1
                      
                  # Counter for the frame that recognize a person
                  elif (counter > 5):
                       
                      print("ATTENTION, INTRUSION DETECTED!")
                      if self.SMS_Flag == 0:
                          for number in self.numbers:
                               self.MQTT.publish("SMS_ALERT_CAM", json.dumps({"number":number}))
                      self.SMS_Flag = 1
                      
                      
                      for ID in self.IDs:
                          if (pic_counter == 0):
                              requests.post('https://api.telegram.org/YOUR_TOKEN/sendMessage', data={'chat_id': ID, 'text': "ATTENTION, a human presence has been detected in the house\nHere are the photos"})
                          filename = "me_{}.jpg".format(pic_counter)
                          cv2.imwrite(filename,frame)
                          requests.post('https://api.telegram.org/YOUR_TOKEN/sendPhoto', data={'chat_id': ID}, files={'photo': open('./{}'.format(filename), 'rb')})
                      counter = 0
                      pic_counter += 1
                      
              # Draw framerate in corner of frame
              cv2.putText(frame,'FPS: {0:.2f}'.format(frame_rate_calc),(30,50),cv2.FONT_HERSHEY_SIMPLEX,1,(255,255,0),2,cv2.LINE_AA)
 
              # Calculate framerate
              t2 = cv2.getTickCount()

              time1 = (t2-t1)/freq
              frame_rate_calc= 1/time1
          
          # Clean up
          self.stop()

          cv2.destroyAllWindows()
          print("Window destroyed")
          Handler.destroyCamera()
            

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
    # Return the most recent frame
        return self.frame

    def stop(self):
    # Indicate that the camera and thread should be stopped
        self.stopped = True


if __name__ == "__main__":
     
     V = VideoStream()
