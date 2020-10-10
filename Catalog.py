# -*- coding: utf-8 -*-
"""
Here are all the functions that mainly deals with reading and modifying json appropriately.
"""

import threading
import json
import secrets
import string
from SendMail_V5 import sendMail

class Catalog:


    def __init__(self, filename, filename2, filename3, filename4):

        self.filename = filename
        self.filename2 = filename2
        self.filename3 = filename3
        self.filename4 = filename4
        self.threadLock = threading.Lock()
        
    def addDevice(self, NAME, IP, PORT):
         
        self.threadLock.acquire()

        fp = open(self.filename4, 'r')

        devices = json.loads(fp.read())
        fp.close()
       
        index = [devices["devices"].index(x) for x in devices["devices"] if x["NAME"] == str(NAME)]
        
        if (len(index) == 0):
             devices["devices"].append({"NAME":str(NAME), "IP":str(IP),"PORT":PORT})
             
             file = open(self.filename4, 'w')
             file.write(json.dumps(devices))
             file.close()
             
             self.threadLock.release()
             return "Device added"

        else: 
             self.threadLock.release()
             return "Device YET PRESENT"
       
        
    def getBroker(self):
         
        self.threadLock.acquire()

        fp = open(self.filename3, 'r')
        config = json.loads(fp.read())
        fp.close()
       
        self.threadLock.release()        
        
        return json.dumps({"IP_broker":config["IP_broker"], "PORT_broker":config["PORT_broker"]})
     
        
    def getUser(self, ID):
         
        self.threadLock.acquire()

        fp = open(self.filename, 'r')
        registered_users = json.loads(fp.read())
        fp.close()
       
        self.threadLock.release()
        
        for user in registered_users["chatList"]:
            if user['ID'] == ID:
                return json.dumps({"found": True})
        return json.dumps({"found": False})

    #This is sort of filtered getUsers   
    def getUsersList(self):
         
        self.threadLock.acquire()

        fp = open(self.filename, 'r')
        registered_users = json.loads(fp.read())
        fp.close()
        
        filteredData = {"chatList":[]}
        
        filteredData["chatList"] = [{"ID":x["ID"], "Nickname":x["Nickname"], "SMS_ON":x["SMS_ON"], "PhoneNumber":x["PhoneNumber"], "AllOk":x["AllOk"]} for x in registered_users["chatList"]]
       
        self.threadLock.release()
      
        return json.dumps(filteredData)
   
    def getUsers(self):
         
        self.threadLock.acquire()

        fp = open(self.filename, 'r')
        registered_users = json.loads(fp.read())
        fp.close()
             
        self.threadLock.release()
      
        return json.dumps(registered_users)
   
    def getDevices(self):
         
        self.threadLock.acquire()

        fp = open(self.filename4, 'r')
        registered_devices = json.loads(fp.read())
        fp.close()
             
        self.threadLock.release()
      
        return json.dumps(registered_devices)
        
    def addUser(self, data):
                
       self.threadLock.acquire()

       fp = open(self.filename, 'r')
       registered_users = json.loads(fp.read())
       fp.close()
       
       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == data["ID"]]
       
       
       if (len(index) != 0):
            self.threadLock.release()
            return "Error"
       
       else:
                      
            try:
                 registered_users["chatList"].append(data)
           
                 file = open(self.filename, 'w')
                 file.write(json.dumps(registered_users))
                 file.close()
                 self.threadLock.release()
                 return "Registration done"
       
            except:
                 self.threadLock.release()

                 return "Error"
            
    def setNickname(self, data):
                
       self.threadLock.acquire()

       fp = open(self.filename, 'r')
       registered_users = json.loads(fp.read())
       fp.close()
              
       # Mail of the current user
       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == data["ID"]][0]
       email = registered_users["chatList"][index]["mail"]
                      
       indexList = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["mail"] == str(email)]
       nicknames = [registered_users["chatList"][i]["Nickname"] for i in indexList]   
       
       if (data["Nickname"] not in nicknames):
                      
            try:
                 
                 registered_users["chatList"][index]["Nickname"] = data["Nickname"]
                 registered_users["chatList"][index]["Flag"] = 0
                 registered_users["chatList"][index]["WaitForMail"] = True
                 
                 file = open(self.filename, 'w')
                 file.write(json.dumps(registered_users))
                 file.close()
                 self.threadLock.release()
                 
                 return "Nickname added"
       
            except:
                 self.threadLock.release()

                 return "Error"
            
    def verifyBuyer(self, data):
                
       self.threadLock.acquire()

       fp = open(self.filename2, 'r')
       registered_buyers = json.loads(fp.read())
       fp.close()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       fp2.close()
              
       mailsBuyers = [x["mail"] for x in registered_buyers["buyersList"]]
       mailsCatalog = [x["mail"] for x in registered_users["chatList"]]

       if (data["Verified"] == False):
                 
                 
            if (data["mail"] in mailsBuyers):
                 
                 
                 if ((data["mail"] not in mailsCatalog and data["Admin"] == True) or (data["mail"] in mailsCatalog and data["Admin"] == False)):
                      
                      try:
                           
                          index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == data["ID"]][0]
                          
                          registered_users["chatList"][index]["mail"] = data["mail"]
                          registered_users["chatList"][index]["WaitForMail"] = False
                          registered_users["chatList"][index]["WaitForPw"] = True
                          
                          file = open(self.filename, 'w')
                          file.write(json.dumps(registered_users))
                          file.close()
                          self.threadLock.release()
                             
                          return "Mail added"
                     
                     
                      except:
                          self.threadLock.release()          
                          return "Error"
                          
                      
                      
                 elif (data["mail"] in mailsCatalog and data["Admin"] == True):
     
                          self.threadLock.release()
                          return "Buyer already registered"
                     
                 elif (data["mail"] not in mailsCatalog and data["Admin"] == False):
     
                          self.threadLock.release()
                          return "Buyer not yet registered"
                  
            else:
                 self.threadLock.release()
                 return "Buyer not in list"
       else:
          
          
            try:
                           
                      index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == data["ID"]][0]
                                 
                      registered_users["chatList"][index]["WaitForMail"] = False
                      registered_users["chatList"][index]["WaitForPw"] = True
                     
                      pw = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))
          
                      mailText = "<br>You are officially welcome to 'Take a smile'! To use the security system please enter \
                      the following password in the chat with the Take a smile bot.<br><br>Once done, you will be automatically logged in!<br><br>\
                      Pw: <b>{}</b><br><br>For any information contact the Help Desk through the channels specified on the support page. \
                      <br>--- This is an automatic message, please do not reply to this email! ---".format(pw)
          
                      registered_users["chatList"][index]["mail"] = data["mail"]
                      registered_users["chatList"][index]["pw"] = pw
                      sendMail(mailText, data["mail"])
                    
                      file = open(self.filename, 'w')
                      file.write(json.dumps(registered_users))
                      file.close()
                      self.threadLock.release()                      
                      return "Pw sent"
                     
                     
            except:
                     self.threadLock.release()
                     return "Error"

            
    def verifyPassword(self, data):
                
       self.threadLock.acquire()
       
       fp = open(self.filename2, 'r')
       registered_buyers = json.loads(fp.read())
       fp.close()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       fp2.close()
       
       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == data["ID"]][0]
       mail = registered_users["chatList"][index]["mail"]

       if (data["Verified"] == False):
            
            if (data["Admin"] == True):
                                          
               
                 pwInd = [registered_buyers["buyersList"].index(x) for x in registered_buyers["buyersList"] if x["mail"] == mail][0]
                 pw = registered_buyers["buyersList"][pwInd]["pw"]
                                       
                 if (data["pw"] != pw):
                      
                     self.threadLock.release()                      
                     return "Admin not verified - Password Error"
                   
                 else:
                      
                     index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == data["ID"]][0]
                     pw = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))
               
                     mailText = "<br>You are officially welcome to 'Take a smile'! To use the security system please enter \
                       the following password in the chat with the Take a smile bot.<br><br>Once done, you will be automatically logged in!<br><br>\
                       Pw: <b>{}</b><br><br>For any information contact the Help Desk through the channels specified on the support page. \
                       <br>--- This is an automatic message, please do not reply to this email! ---".format(pw)
               
                     sendMail(mailText, mail)
                     
                     registered_users["chatList"][index]["WaitForMail"] = False
                     registered_users["chatList"][index]["WaitForPw"] = True
                     registered_users["chatList"][index]["Verified"] = True
                     registered_users["chatList"][index]["pw"] = pw
               
                     file = open(self.filename, 'w')
                     file.write(json.dumps(registered_users))
                     file.close()
                     self.threadLock.release()                      

                     return "Admin verified"
                
            else:
                 
                 pwInd = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["mail"] == mail and x["Admin"] == True][0]
                 pw = registered_users["chatList"][pwInd]["pw"]
                 
                 if (data["pw"] != pw):
                      
                     self.threadLock.release()                      
                     return ("User NOT verified - Password Error")
                     
                 else:
               
                    
                       registered_users["chatList"][index]["Verified"] = True
                       registered_users["chatList"][index]["WaitForPw"] = False
                       registered_users["chatList"][index]["AllOk"] = True
                       
                       file = open(self.filename, 'w')
                       file.write(json.dumps(registered_users))
                       file.close()
                       self.threadLock.release()   
                                              
                       return ("User Logged")
                       
                           
       else:
            
                 if (data["pw"] == registered_users["chatList"][index]["pw"]):

                       registered_users["chatList"][index]["Flag"] = 0
                       registered_users["chatList"][index]["WaitForPw"] = False
                       registered_users["chatList"][index]["AllOk"] = True
                       

                       file = open(self.filename, 'w')
                       file.write(json.dumps(registered_users))
                       file.close()
                       self.threadLock.release()   
                                              
                       return ("User Logged")
                                                                               
                 else:
                       if (registered_users["chatList"][index]["Flag"] != 4):
                            
                            registered_users["chatList"][index]["WaitForMail"] = True
                            registered_users["chatList"][index]["WaitForPw"] = False
                                                   
                            file = open(self.filename, 'w')
                            file.write(json.dumps(registered_users))
                            file.close()
                            self.threadLock.release()   
                                              
                            return ("User NOT verified - Password Error")
                  
                       else:
                            self.threadLock.release()   
                                              
                            return ("New pw NOT verified - Password Error")
            
            
               
    def setFlag(self, data):
                
       self.threadLock.acquire()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       fp2.close()   
            
       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == str(data["ID"])][0]
       registered_users["chatList"][index]["Flag"] = data["Flag"]

       file = open(self.filename, 'w')
       file.write(json.dumps(registered_users))
       file.close()
       self.threadLock.release()   

       return ("Flag changed")    

    def removeUser(self, data):
                
       self.threadLock.acquire()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       fp2.close()   
            
       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == data["ID"]][0]
       email = registered_users["chatList"][index]["mail"]
       
       indexList = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["mail"] == str(email)]
       nicknames = [registered_users["chatList"][i]["Nickname"] for i in indexList]
       registered_users["chatList"][index]["Flag"] = 0

       
       if data["Nickname"] in nicknames:
            registered_users["chatList"].pop(nicknames.index(data["Nickname"]))

            file = open(self.filename, 'w')
            file.write(json.dumps(registered_users))
            file.close()
            
            self.threadLock.release()   
     
            return ("User removed")
       else:
            
            return ("User NOT removed") 
       
    def setSMS(self, data):
                
       self.threadLock.acquire()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       fp2.close()   
       
       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == str(data["ID"])][0]
       
       if (registered_users["chatList"][index]["PhoneNumber"] == ""):
                self.threadLock.release()   
                return ("Empty number")
           
       registered_users["chatList"][index]["SMS_ON"] = data["SMS"]
    
       file = open(self.filename, 'w')
       file.write(json.dumps(registered_users))
       file.close()
       self.threadLock.release()   

       return ("SMS setted")

    def setNumber(self, data):
                
       self.threadLock.acquire()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       fp2.close()   
       
       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == str(data["ID"])][0]
       registered_users["chatList"][index]["PhoneNumber"] = data["Number"]
       registered_users["chatList"][index]["Flag"] = 0

    
       file = open(self.filename, 'w')
       file.write(json.dumps(registered_users))
       file.close()
       self.threadLock.release()   

       return ("SMS setted")  

    def setMail(self, data):
                
       self.threadLock.acquire()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       fp2.close()   
       
       
       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == str(data["ID"])][0]
       email = registered_users["chatList"][index]["mail"]
  
       indexList = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["mail"] == str(email)]
       
       for i in indexList:                    
            registered_users["chatList"][i]["mail"] = str(data["mail"])
            
       registered_users["chatList"][index]["Flag"] = 0
       
       fp = open(self.filename2, 'r')
       registered_buyers = json.loads(fp.read())
       fp.close()
       
       index2 = [registered_buyers["buyersList"].index(x) for x in registered_buyers["buyersList"] if x["mail"] == email][0]
      
       registered_buyers["buyersList"][index2]["mail"] = str(data["mail"])
   
       file = open(self.filename2, 'w')
       file.write(json.dumps(registered_buyers))
       file.close()
        
       file = open(self.filename, 'w')
       file.write(json.dumps(registered_users))
       file.close()
       
       self.threadLock.release()   

       return ("New email setted")    
           


    def setPw(self, data):
         
       self.threadLock.acquire()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       fp2.close()   

       index = [registered_users["chatList"].index(x) for x in registered_users["chatList"] if x["ID"] == str(data["ID"])][0]
       mail = registered_users["chatList"][index]["mail"]
       pw = ''.join(secrets.choice(string.ascii_letters + string.digits + string.punctuation) for _ in range(16))

       mailText = "<br>Hello, you have requested a new pw.<br><br>Here is your new password.<br><br>\
        Pw: <b>{}</b><br><br>For any information contact the Help Desk through the channels specified on the support page. \
        <br>--- This is an automatic message, please do not reply to this email! ---".format(pw)

       sendMail(mailText, mail)
       registered_users["chatList"][index]["WaitForMail"] = False
       registered_users["chatList"][index]["WaitForPw"] = True
       registered_users["chatList"][index]["Flag"] = 4
       registered_users["chatList"][index]["pw"] = pw
       
       file = open(self.filename, 'w')
       file.write(json.dumps(registered_users))
       file.close()
       
       fp2 = open(self.filename, 'r')
       registered_users = json.loads(fp2.read())
       
       self.threadLock.release()
       
       return "Email for changing pw sent"
       
    def removeDevice(self, data):
                
        self.threadLock.acquire()

        fp = open(self.filename4, 'r')

        devices = json.loads(fp.read())
        fp.close()
       
        index = [devices["devices"].index(x) for x in devices["devices"] if x["NAME"] == str(data["NAME"])]
        
        if (len(index) == 0):
             self.threadLock.release()
             return "Sorry, this device is not present"

        else: 
             new_devices = {"devices":[x for x in devices["devices"] if x["NAME"] != data["NAME"]]}
             file = open(self.filename4, 'w')
             file.write(json.dumps(new_devices))
             file.close()
             self.threadLock.release()
             return "Device correctly removed"
