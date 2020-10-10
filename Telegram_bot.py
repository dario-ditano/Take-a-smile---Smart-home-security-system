# -*- coding: utf-8 -*-

"""
This is the telegram bot, and it is the most important interface for the user. 
The user is divided into purchaser (called admin for convenience) and secondary user. 
To log in, the purchaser will use a temporary pw that Take A Smile gave him upon purchase, 
and immediately afterwards a new password will be sent to him via email. 
This password, if communicated to roommates or relatives, can also make them use the bot, 
albeit with some limited function. For example, if a roommate leaves home, the purchaser (and only him)
could remove it from users. This possibility of sharing the bot has been designed to be able to have greater 
security, in the event that the purchaser is not looking at the phone during an intruder detection 
or a fire detection.
At the startup, the bot only know the ip and port of the Catalog, and will ask for the list of devices.
This list can be easily updated, allowing to add or remove devices.
The only condition is that the device has "cam" or "gas" in the name, so that it can be recognized and 
classified appropriately.
"""

import time
import telepot
import json
import re
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.loop import MessageLoop
import requests
import emojis
import sys
from requests.auth import HTTPDigestAuth


class MyBot:

    def __init__(self, IP_Catalog, IP_Port, token, devices, key):


        self.token = token
        self.bot = telepot.Bot(token=str(self.token))
        
        self.catalogIP = IP_Catalog
        self.catalogport = str(IP_Port)
        self.key = key

        MessageLoop(self.bot, {'chat': self.on_chat_message,'callback_query': self.on_callback_query}).run_as_thread()

        print ('Listening ...')
        
        Names = [x["NAME"] for x in devices["devices"]]
        self.cam_list = []
        self.gas_list = []
        
        for name in Names:
             
             # Create lists of devices
             if (re.search('cam', name, re.IGNORECASE)):
                 self.cam_list.append(([x for x in devices["devices"] if x["NAME"] == name])[0])
             elif (re.search('gas', name, re.IGNORECASE)):
                 self.gas_list.append(([x for x in devices["devices"] if x["NAME"] == name])[0])
                 
        print("Partito")
        while True:
              time.sleep(10)

    def on_callback_query(self, msg):
         
         query_id, chat_id, query_data = telepot.glance(msg, flavor='callback_query')
         print('Callback Query:', query_id, chat_id, query_data)
         
#%% Start now - yes / no
         if query_data=='yes':

            reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                        [InlineKeyboardButton(text="I just bought it", callback_data='admin'),InlineKeyboardButton(text="I have a password", callback_data='relative')]], resize_keyboard=True, one_time_keyboard=True)

            self.bot.sendMessage(chat_id, text="Perfect! Have you purchased the Take a smile system or do you have a password to share a subscription?",reply_markup=reply_markup)

         elif query_data=='nope':
            self.bot.sendMessage(chat_id, "As you prefer, but remember that until you register you cannot use the app!")

#%% He's a purchaser
         elif query_data=='admin':
          
           jsonData = {"ID":str(chat_id), "Nickname":"", "Flag":2, "PhoneNumber":"", "SMS_ON":False, "Admin":True, "Verified":False, "WaitForMail":False, "WaitForPw":False, "AllOk":False, "mail":"", "pw":""}
           URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/add/user'
           
           try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
           except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'An error happened. Try again.')
               print (err)

           self.bot.sendMessage(chat_id, "Perfect, now choose a nickname for this app, for example 'Jon Snow'")
           
#%% He's a secondary user
         elif query_data=='relative':
              
              
           jsonData = {"ID":str(chat_id), "Nickname":"", "Flag":2, "PhoneNumber":"", "SMS_ON":False, "Admin":False, "Verified":False, "WaitForMail":False, "WaitForPw":False, "AllOk":False, "mail":"", "pw":""}
           URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/add/user'
           
           try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
           except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'An error happened. Try again.')
               print (err)

           self.bot.sendMessage(chat_id, "Perfect, now choose a nickname for this app, for example 'Jon Snow'")

#%% Set telephone number              
         elif query_data=='number':
              
            jsonData = {"ID":chat_id, "Flag":1}
            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/flag'
           
            try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'Setting number failed')
               print (err)
              
            self.bot.sendMessage(chat_id, "Please write the number the SMS should reach", parse_mode= 'Markdown')
            
#%% Set SMS ON              
         elif query_data=='sms_on': 
              
            jsonData = {"ID":chat_id, "SMS":True}
            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/sms'
           
            try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'Set SMS ON failed')
               print (err)
    
            if (r.text == "SMS setted"):
                 self.bot.sendMessage(chat_id, "Ok, now you will receive also SMS alert notifications!")
                 
            elif (r.text == "Empty number"):
                 self.bot.sendMessage(chat_id, "Please insert the phone number first!") 
            
#%% Set SMS OFF          
         elif query_data=='sms_off':

            jsonData = {"ID":chat_id, "SMS":False}
            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/sms'
           
            try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'Setting SMS OFF failed')
               print (err)
    
            if (r.text == "SMS setted"):
                 self.bot.sendMessage(chat_id, "Ok, now you will NOT receive also SMS alert notifications!")
                 
            elif (r.text == "Empty number"):
                 self.bot.sendMessage(chat_id, "Please insert the phone number first!") 
#%% Change email           
         elif query_data=='new_email':
              
              
            jsonData = {"ID":chat_id, "Flag":3}
            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/flag'
           
            try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'Changing email failed')
               print (err)
                           
            self.bot.sendMessage(chat_id, "Please write the new email", parse_mode= 'Markdown')    
            
 #%% Change pw           
         elif query_data=='new_pw':
              
              
            jsonData = {"ID":chat_id}
            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/pw'
           
            try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'Change pw failed')
               print (err)
                            
            self.bot.sendMessage(chat_id, "We have sent you an email with the new pw, write it here to log in!", parse_mode= 'Markdown') 

#%% Users list      
         elif query_data=='list_users':
              
            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/get/users'
           
            try:
               r = requests.get(URL, auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'An error happened. Try again.')
               print (err)
               
            chats = json.loads(r.text)
            
            # Take mail of current user
            index = [chats["chatList"].index(x) for x in chats["chatList"] if x["ID"] == str(chat_id)][0]
            email = chats["chatList"][index]["mail"]
            nickname = chats["chatList"][index]["Nickname"]
            
            # Index where mail is the same (so they are secondary users or one is the purchaser)
            indexList = [chats["chatList"].index(x) for x in chats["chatList"] if x["mail"] == str(email)]
            nicknames = [chats["chatList"][i]["Nickname"] for i in indexList]
            
            nicknames.remove(nickname)
            
            if len(nicknames) == 0:
                 self.bot.sendMessage(chat_id, "You are the only user associated with the email {}".format(email), parse_mode= 'Markdown')   
            else:
                 self.bot.sendMessage(chat_id, "The other users associated with this email are:\n\n- " + "\n- ".join(nicknames), parse_mode= 'Markdown')   
              
         elif query_data=='back':
            self.bot.sendMessage(chat_id, 'Feel free to choose from one of the available commands:\n/TakeAPic\n/TakeLastGas\n/TakeGasTreshold\n/SetGasTreshold\n/TakeMyFreeboard\n/UpdateDevices\n/DevicesList\n/CurrentSettings\n/Settings')                               

#%% Remove user
         elif query_data=='remove_user':
              
            jsonData = {"ID":chat_id, "Flag":5}
            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/flag'
           
            try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'Remove user failed')
               print (err)
                       
            self.bot.sendMessage(chat_id, "Please enter the nickname of the user you would like to remove\nRemember that the action is *irreversible*", parse_mode= 'Markdown')  
  
         elif query_data=='remove_device':
              
            jsonData = {"ID":chat_id, "Flag":7}
            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/flag'
           
            try:
               r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'Remove device failed')
               print (err)
                       
            self.bot.sendMessage(chat_id, "Please enter the name of the device you would like to remove\nRemember that the action is *irreversible*", parse_mode= 'Markdown')  
                          
    def on_chat_message(self, msg):

         content_type, chat_type, chat_id = telepot.glance(msg)
         chat_id = str(chat_id)
         
         if content_type == 'text':

            URL = 'http://' + self.catalogIP + ':' + str(self.catalogport) + '/get/users'
           
            try:
               r = requests.get(URL, auth=HTTPDigestAuth('TakeASmile', self.key))
               r.raise_for_status()
               
            except requests.HTTPError as err:
               self.bot.sendMessage(chat_id, 'An error happened. Try again.')
               print (err)
               
            chats = json.loads(r.text)
            
            IDs = [x["ID"] for x in chats["chatList"]]
            
            if (str(chat_id) not in IDs):
          
                     reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                  [InlineKeyboardButton(text='Yes, immediately', callback_data='yes'),InlineKeyboardButton(text='Maybe later', callback_data='nope')]
                              ], one_time_keyboard=True)

                     self.bot.sendMessage(chat_id, text=emojis.encode('Hello, welcome to the bot\n*Take a Smile* :camera:\n\nIt looks like you are not registered yet, would you like to register now?'),reply_markup=reply_markup, parse_mode= 'Markdown')


            else:
                 index = [chats["chatList"].index(x) for x in chats["chatList"] if x["ID"] == str(chat_id)][0]
                              

                 # If WaitForPw = TRUE, i'm waiting for the pw
                 if (chats["chatList"][index]["WaitForPw"] == True):
                      
                           mail = chats["chatList"][index]["mail"]

                           pw = msg["text"]
                           # Try to set the mail
                           jsonData = {"ID":chat_id, "mail":mail, "Admin":chats["chatList"][index]["Admin"], "Verified":chats["chatList"][index]["Verified"], "pw":pw}
                           URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/verify/pw'
                          
                           try:
                              r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                              r.raise_for_status()
                              
                           except requests.HTTPError as err:
                              self.bot.sendMessage(chat_id, 'Purchaser not valid.\nSorry, but your email is not listed')
                              print (err)
               

                           if (r.text == "Admin not verified - Password Error"):
                                    self.bot.sendMessage(chat_id, "Sorry but the temporary password does not match!")
                           elif (r.text == "Admin verified"):
                                    self.bot.sendMessage(chat_id, "Everything is going well, we have sent you an email with the new pw, write it here to log in!")
                           elif (r.text == "User NOT verified - Password Error"):
                                    self.bot.sendMessage(chat_id, "Sorry but the purchaser's password doesn't match!")
                           elif (r.text == "User Logged"):                          
                                 self.bot.sendMessage(chat_id, "Thank you very much, you are now logged in and allowed to use the Take a smile app!\n\nHere is the list of available commands:\n/TakeAPic\n/TakeLastGas\n/TakeGasTreshold\n/SetGasTreshold\n/TakeMyFreeboard\n/UpdateDevices\n/DevicesList\n/CurrentSettings\n/Settings")
                           elif (r.text == "New pw NOT verified - Password Error"):
                                 self.bot.sendMessage(chat_id, "Mm something went wrong, please try again to enter the password sent by email")



#%% Verify mail

                 # If WaitForMail = TRUE, i'm waiting for the mail
                 elif (chats["chatList"][index]["WaitForMail"] == True):

                      # Mail control
                      if (re.search("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",msg['text'])):

                           print("Mail accettata: {}".format(msg['text']))
                           mail = msg["text"]

                                  
                           # Try to set mail
                           jsonData = {"ID":chat_id, "mail":mail, "Admin":chats["chatList"][index]["Admin"], "Verified":chats["chatList"][index]["Verified"]}
                           URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/verify/buyer'
                          
                           try:
                              r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                              r.raise_for_status()
                              
                           except requests.HTTPError as err:
                              self.bot.sendMessage(chat_id, 'Purchaser not valid.\nSorry, but your email is not listed')
                              print (err)
                           
                           if (r.text == "Mail added"):
                                if (chats["chatList"][index]["Admin"] == True):
                                    self.bot.sendMessage(chat_id, "The mail has found a match, now please write the temporary password received during the purchase")
                                else:
                                    self.bot.sendMessage(chat_id, "The mail has found a match, now please write the password that was given to you by the purchaser")

                           elif (r.text == "Buyer already registered"):
                                    self.bot.sendMessage(chat_id, "Sorry but there is already an account with this email")
                           elif (r.text == "Buyer not yet registered"):
                                    self.bot.sendMessage(chat_id, "Sorry but the purchaser hasn't registered yet")
                           elif (r.text == "Pw sent"):                          
                                 self.bot.sendMessage(chat_id, "The mail has found a match, now please write the temporary password received during the purchase")
                           elif (r.text == "Buyer not in list"):
                                    self.bot.sendMessage(chat_id, "Sorry but it seems that your email is not in our database, please try to contact support")
                      else:
                            self.bot.sendMessage(chat_id, "Invalid mail, please try to rewrite it!")
                            
#%% Set number

                 elif (chats["chatList"][index]["Flag"] == 1):
                      
                       number = str(msg["text"])
                       
                       if (len(number) <= 11 and len(number) >= 9 and number.isdigit()):
                       
                            jsonData = {"ID":chat_id, "Number":number}
                            URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/number'
                          
                            try:
                                r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                                r.raise_for_status()
                              
                            except requests.HTTPError as err:
                                print (err)
                                 
                                self.bot.sendMessage(chat_id, 'Set number failed')

                            self.bot.sendMessage(chat_id, "Ok, the number {} has been saved".format(number))
                                    
                       else:
                            self.bot.sendMessage(chat_id, "Sorry, the number {} is invalid".format(number))  
                     
                 
                 #%% Choose nickname
                 elif (chats["chatList"][index]["Flag"] == 2):

                      nickname = msg["text"]
                
                      if (len(nickname) <= 30 and len(nickname) > 1):
                           
                           # Try to set the nickname
                           jsonData = {"ID":str(chat_id), "Nickname":nickname}
                           URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/nickname'
                          
                           try:
                              r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                              r.raise_for_status()
                              
                           except requests.HTTPError as err:
                              self.bot.sendMessage(chat_id, 'Nickname not valid.')
                              print (err)

                           self.bot.sendMessage(chat_id, "Ok, the nickname {} has been saved".format(nickname)) 
                           
                           if (chats["chatList"][index]["Admin"] == True):
                          
                                self.bot.sendMessage(chat_id, "Please write the email with which you purchased the Take a smile system")
                           else:
                                self.bot.sendMessage(chat_id, "Please write the purchaser's email")

                      else:
                           self.bot.sendMessage(chat_id, "Sorry, the nickname {} is invalid or not available.\n Remember that the nickname must contain between 2 and 30 characters\nPlease try again".format(nickname))  




                 elif (chats["chatList"][index]["Flag"] == 3):

                      new_mail = msg["text"]

                      if (re.search("^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$",new_mail)):
                           
                           print("Mail accettata: {}".format(new_mail))
                           
                           jsonData = {"ID":str(chat_id), "mail":new_mail}
                           URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/mail'
                          
                           try:
                              r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                              r.raise_for_status()
                              
                           except requests.HTTPError as err:
                              self.bot.sendMessage(chat_id, 'Sorry, mail not valid.')
                              print (err) 
                           
                           self.bot.sendMessage(chat_id, "Ok, the new mail {} has been saved".format(new_mail)) 
                           
                      else:
                           self.bot.sendMessage(chat_id, "Sorry, the mail {} is invalid\nPlease try again".format(new_mail))  
                           

                 elif (chats["chatList"][index]["Flag"] == 5):

                      nickname = msg["text"]
                      
                      # Try to set mail
                      jsonData = {"ID":chat_id, "Nickname":nickname}
                      URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/remove/user'
                     
                      try:
                         r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                         r.raise_for_status()
                         
                      except requests.HTTPError as err:
                         self.bot.sendMessage(chat_id, 'Remove user failed')
                         print (err)
                    
                      if (r.text == "User removed"):
                           self.bot.sendMessage(chat_id, "The user {} has been removed".format(nickname), parse_mode= 'Markdown')   
                      elif(r.text == "User NOT removed"):
                           self.bot.sendMessage(chat_id, "Sorry, there is no user with the nickname {}".format(nickname), parse_mode= 'Markdown')   
                        
                 elif (chats["chatList"][index]["Flag"] == 6):


                       treshold = int(msg["text"])
                       data = {"treshold":treshold}
                       jsonData = json.dumps(data)
                           
                       for gas in self.gas_list:
                           
                           print(self.gas_list)
                           print(gas)
                                                          
                           url = 'http://' + str(gas["IP"]) + ':' + str(gas["PORT"]) + '/set/treshold'
                           try:                               
                                r = requests.post(url, data = jsonData, auth=HTTPDigestAuth('TakeASmile', self.key))
                                r.raise_for_status()
                                self.bot.sendMessage(chat_id, r.text, parse_mode= 'Markdown')
                           except requests.HTTPError as err:
                                self.bot.sendMessage(chat_id, 'Setting treshold failed')
                                print (err)
                                 
                                     
                       # Set flag to 0
                       jsonData = {"ID":chat_id, "Flag":0}
                       URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/flag'
                     
                       try:
                           r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                           r.raise_for_status()
                         
                       except requests.HTTPError as err:
                           self.bot.sendMessage(chat_id, 'Remove user failed')
                           print (err)
                      
                 elif (chats["chatList"][index]["Flag"] == 7):

                       found = 0
                       device = msg["text"]
                       
                       cam_names = [x["NAME"] for x in self.cam_list]
                       gas_names = [x["NAME"] for x in self.gas_list]
                       
                       if (device in cam_names):
                          new_cams = [x for x in self.cam_list if x["NAME"] != device]
                          self.cam_list = new_cams
                          found = 1
                          
                       elif (device in gas_names):
                          new_gas = [x for x in self.gas_list if x["NAME"] != device]
                          self.gas_list = new_gas
                          found = 1  
                          
                       if (found == 1):
                            
                           data = {"NAME":device}
                           jsonData = json.dumps(data)
                           
                                                          
                           url = 'http://' + self.catalogIP + ':' + str(self.catalogport) + '/remove/device'

                           # Manda richiesta al Web Service
                           req = requests.post(url, data = jsonData, auth=HTTPDigestAuth('TakeASmile', self.key))
                           # Stampa risposta del Web Service
                           self.bot.sendMessage(chat_id, req.text, parse_mode= 'Markdown')
                       else:
                           self.bot.sendMessage(chat_id, "Sorry, this device is not present!", parse_mode= 'Markdown') 
                       # Rimetto flag a 0
                       jsonData = {"ID":chat_id, "Flag":0}
                       URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/flag'
                     
                       try:
                           r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                           r.raise_for_status()
                         
                       except requests.HTTPError as err:
                           self.bot.sendMessage(chat_id, 'Remove user failed')
                           print (err)

                 else:
                           command = msg['text']

                           if command == '/TakeAPic':
                                data = {"IDchat":chat_id}
                                jsonData = json.dumps(data)
                                
                                if (len(self.cam_list) >= 1):
                                
                                    for cam in self.cam_list:
                                                                    
                                         url = 'http://' + cam["IP"] + ':' + str(cam["PORT"]) + '/get/pic'
     
                                         try:
                                              req = requests.post(url, jsonData, auth=HTTPDigestAuth('TakeASmile', self.key))
                                              req.raise_for_status()
                                         except requests.HTTPError as err:
                                              self.bot.sendMessage(chat_id, 'Take a pic failed')
                                              print (err) 
                                         
                                else:
                                    self.bot.sendMessage(chat_id, "Sorry, there is no camera connected", parse_mode= 'Markdown')
                 

                           elif command == '/TakeLastGas':
                               
                                if (len(self.gas_list) >= 1):

                                
                                    for gas in self.gas_list:
                                         
                                         print(self.gas_list)
                                         print(gas)
                                                                        
                                         url = 'http://' + str(gas["IP"]) + ':' + str(gas["PORT"]) + '/get/gas'
         
                                         try:                                              
                                              req = requests.get(url, auth=HTTPDigestAuth('TakeASmile', self.key))
                                              req.raise_for_status()
                                              self.bot.sendMessage(chat_id, req.text, parse_mode= 'Markdown')
                                         except requests.HTTPError as err:
                                              self.bot.sendMessage(chat_id, 'Take last detection failed')
                                              print (err)                                                
                                else:
                                    self.bot.sendMessage(chat_id, "Sorry, no gas detector is connected", parse_mode= 'Markdown')

                           elif command == '/TakeGasTreshold':
                               
                                if (len(self.gas_list) >= 1):
                                
                                    for gas in self.gas_list:
                                         
                                         print(self.gas_list)
                                         print(gas)
                                                                        
                                         url = 'http://' + str(gas["IP"]) + ':' + str(gas["PORT"]) + '/get/treshold'
         
                                         try:
                                              req = requests.get(url, auth=HTTPDigestAuth('TakeASmile', self.key))
                                              req.raise_for_status()
                                              self.bot.sendMessage(chat_id, req.text, parse_mode= 'Markdown')
                                         except requests.HTTPError as err:
                                               self.bot.sendMessage(chat_id, 'Take treshold failed')
                                               print (err)                                             
                                         
                                else:
                                    self.bot.sendMessage(chat_id, "Sorry, no gas detector is connected", parse_mode= 'Markdown')
                                     
                           elif command == '/SetGasTreshold':
                               
                               if (len(self.gas_list) >= 1):
                                                                                                
                                   jsonData = {"ID":chat_id, "Flag":6}
                                   URL = 'http://' + self.catalogIP + ':' + self.catalogport + '/set/flag'
                                   
                                   try:
                                       r = requests.post(URL, data = json.dumps(jsonData), auth=HTTPDigestAuth('TakeASmile', self.key))
                                       r.raise_for_status()
                                       
                                   except requests.HTTPError as err:
                                       self.bot.sendMessage(chat_id, 'Remove user failed')
                                       print (err)
                                   
                                   self.bot.sendMessage(chat_id, 'Please insert an integer for the treshold')
                                   
                               else:
                                    self.bot.sendMessage(chat_id, "Sorry, no gas detector is connected", parse_mode= 'Markdown')
                               
                           elif command == '/TakeMyFreeboard':
                               self.bot.sendMessage(chat_id, 'Here is the link for your dashboard: \n{}'.format('https://freeboard.io/board/x5gqGh'))


                           elif command == '/UpdateDevices':
                                
                                
                               # Chiedo devices al catalog
                               URL = 'http://' + self.catalogIP + ':' + str(self.catalogport) + '/get/devices'
                          
                               try:
                                   r = requests.get(URL, auth=HTTPDigestAuth('TakeASmile', self.key))
                                   r.raise_for_status()
                              
                               except requests.HTTPError as err:
                                   print (err)
                         
                               devices = json.loads(r.text)
                                                             
                               devices_list = [x for x in devices["devices"]]                              
                               old_devices = self.cam_list + self.gas_list
                               # If a new device is different ...
                               new_devices = [x for x in devices_list if x not in old_devices]
                                                               
                               Names = [x["NAME"] for x in new_devices if x["NAME"]]
                               
                               new_cam = 0
                               new_gas = 0
                                 
                               for name in Names:
                                      
                                   if (re.search('cam', name, re.IGNORECASE)):
                                       self.cam_list.append(([x for x in new_devices if x["NAME"] == name])[0])
                                       new_cam += 1
                                   elif (re.search('gas', name, re.IGNORECASE)):
                                       self.gas_list.append(([x for x in new_devices if x["NAME"] == name])[0])
                                       new_gas += 1
                                                                                                            
                               if (new_cam == 1 and new_gas == 0):
                                    self.bot.sendMessage(chat_id, "Update completed, a new camera has been found, try it now with the /TakeAPic command!")
                               elif (new_cam == 0 and new_gas == 1):
                                    self.bot.sendMessage(chat_id, "Update completed, a new gas sensor has been found, try it now with the /TakeLastGas command!")
                               elif (new_cam == 1 and new_gas == 1):
                                    self.bot.sendMessage(chat_id, "A new camera and a new gas sensor have been found, try them now with the /TakeAPic and /TakeLastGas commands!")
                               elif (new_cam == 0 and new_gas == 0):
                                    self.bot.sendMessage(chat_id, "Update completed, no new device was found")
                               else:
                                    self.bot.sendMessage(chat_id, "More than 2 new sensors have been found, try them now!")
                                   
                           elif command == '/DevicesList':
                                    devicesList = self.cam_list + self.gas_list
                                    self.bot.sendMessage(chat_id, "Here is the list of current devices:\n- " + "\n- ".join(x["NAME"] for x in devicesList))
                                   
                           elif command == '/CurrentSettings':
                                    index = [chats["chatList"].index(x) for x in chats["chatList"] if x["ID"] == str(chat_id)][0]
                                    SMS_ON = chats["chatList"][index]["SMS_ON"]
                                    PhoneNumber = chats["chatList"][index]["PhoneNumber"]
                                    activated = {"True":"Activated", "False": "Not activated"}
                                    if (PhoneNumber == ""):
                                         self.bot.sendMessage(chat_id, "SMS alert: {}\nPhone number: Not setted".format(activated[str(SMS_ON)]))
                                    else:     
                                         self.bot.sendMessage(chat_id, "SMS alert: {}\nPhone number: {}".format(activated[str(SMS_ON)], PhoneNumber))
                                        
                           elif command == '/Settings':
                                
                               if (chats["chatList"][index]["Admin"] == True):
 
                                    reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                                 [InlineKeyboardButton(text='Set phone number', callback_data='number')],
                                                 [InlineKeyboardButton(text='Set SMS ON', callback_data='sms_on')],
                                                 [InlineKeyboardButton(text='Set SMS OFF', callback_data='sms_off')],
                                                 [InlineKeyboardButton(text='Change email', callback_data='new_email')],
                                                 [InlineKeyboardButton(text='Change password', callback_data='new_pw')],
                                                 [InlineKeyboardButton(text='List of users', callback_data='list_users')],
                                                 [InlineKeyboardButton(text='Remove user', callback_data='remove_user')],   
                                                 [InlineKeyboardButton(text='Remove device', callback_data='remove_device')],                                                   
                                                 [InlineKeyboardButton(text='Back to command list', callback_data='back')]
                                             ], one_time_keyboard=True)
                               else:
                                         reply_markup = InlineKeyboardMarkup(inline_keyboard=[
                                                 [InlineKeyboardButton(text='Set phone number', callback_data='number')],
                                                 [InlineKeyboardButton(text='Set SMS ON', callback_data='sms_on')],
                                                 [InlineKeyboardButton(text='Set SMS OFF', callback_data='sms_off')],
                                                 [InlineKeyboardButton(text='List of users', callback_data='list_users')], 
                                                 [InlineKeyboardButton(text='Back to command list', callback_data='back')]
                                             ], one_time_keyboard=True)
          
                               self.bot.sendMessage(chat_id, text=emojis.encode('Welcome to the *settings panel* :wrench: \nHere you have settings related to your account'),reply_markup=reply_markup, parse_mode= 'Markdown')

                           elif command == "/start":
                               self.bot.sendMessage(chat_id, 'Hello, feel free to choose from one of the available commands:\n/TakeAPic\n/TakeLastGas\n/TakeGasTreshold\n/SetGasTreshold\n/TakeMyFreeboard\n/UpdateDevices\n/DevicesList\n/CurrentSettings\n/Settings')                               

                           else:
                               self.bot.sendMessage(chat_id, 'The command you typed does not exist, here is the list of available commands:\n/TakeAPic\n/TakeLastGas\n/TakeGasTreshold\n/SetGasTreshold\n/TakeMyFreeboard\n/UpdateDevices\n/DevicesList\n/CurrentSettings\n/Settings')


if __name__ == '__main__':
     
    file = open("configBot.json","r")
    data = json.loads(file.read())

    IP_Catalog = data["IP_catalog"]
    IP_Port = data["PORT_catalog"]
    token = data["token"]
    key = data["DigestKey"]

    file.close()
    
    # Ask devices to the catalog
    URL = 'http://' + IP_Catalog + ':' + str(IP_Port) + '/get/devices'
 
    try:
       r = requests.get(URL, auth=HTTPDigestAuth('TakeASmile', key))
       r.raise_for_status()
     
    except requests.HTTPError as err:
       print (err)
       sys.exit()

    devices = json.loads(r.text)

    TAS_Bot = MyBot(IP_Catalog, IP_Port, token, devices, key)
