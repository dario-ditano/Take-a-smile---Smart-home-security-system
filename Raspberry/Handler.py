# -*- coding: utf-8 -*-

"""
This class is used to support the camera logic, so that image recognition is not continually invoked 
when it is already active
"""

from TFLite_detection_webcam import VideoStream

class HandlerClass(object):
     
    def __init__(self):
         
         self.cameraON = 0
         
         self.timeFlag = 0
         self.number = 0

         self.V = None
         
    def getCameraState(self):
         return self.cameraON
    
    def getTimeFlag(self):
         return self.timeFlag
    
    def destroyCamera(self):
         print("Camera destroyed")
         self.V = None
         
    def setTimeFlag(self, n):
         self.timeFlag = n
    
    def setCameraState(self, n, MQTT):
         
         # If I have to turn the camera on and it was off, call the program, which will immediately 
         # start the timer         
         if (n == 1 and self.cameraON == 0):
              self.cameraON = 1
              self.V = VideoStream(MQTT)
              self.V.start(self)

         # If the camera was already on, set the time flag so that it starts counting again
         elif (n == 1 and self.cameraON == 1):
              self.setTimeFlag(1)
              
         # If the camera just turned off, set everything to 0
         elif (n == 0):
             self.cameraON = 0
             self.timeFlag = 0
              
         
if __name__ == "__main__":
     
     Handler = HandlerClass()
          
              