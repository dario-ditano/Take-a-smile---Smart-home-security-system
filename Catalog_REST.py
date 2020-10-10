# -*- coding: utf-8 -*-

"""
This is the catalog, and it's the reference for all the microservices and for the bot.
Each microservice knows its ip and its port. Only the catalog knows the broker's ip and the broker's port,
and provides them to all other actors.
At startup, the devices json is empty, and each microservice, turning on, will automatically register, 
populating the json. Later, the bot, at startup, will ask for the list of connected devices, 
which can still be updated in runtime using the /UpdateDevices command.
In general, for security reasons, we preferred to adopt the POST rather than the GET,
and for this reason most of the calls are POST
"""

import cherrypy
import json
from Catalog import *
from cherrypy.lib import auth_digest

class REST_Catalog(object):

    exposed=True
    
    def __init__(self):
         
        self.catalog = Catalog("Catalog.json", "Buyers.json", "configCatalog.json", "devices.json")
        
    def GET(self, *uri, **params):
         
          
        if (len(uri) == 2 and uri[0] == 'get' and uri[1] == 'users'):
             
            return self.catalog.getUsers()
       
        elif (len(uri) == 2 and uri[0] == 'get' and uri[1] == 'userslist'):
             
            return self.catalog.getUsersList()

        elif (len(uri) == 2 and uri[0] == 'get' and uri[1] == 'broker'):
              
            return self.catalog.getBroker()
       
        elif (len(uri) == 2 and uri[0] == 'get' and uri[1] == 'devices'):
              
            return self.catalog.getDevices()

        
    def POST(self, *uri):
        

        if len(uri) == 0:
            raise cherrypy.HTTPError(400)

        mybody = cherrypy.request.body.read()

        try:
            data = json.loads(mybody)
        except:
            raise cherrypy.HTTPError(400)


        #%% Register device
        if (len(uri) == 2 and uri[0] == 'add' and uri[1] == 'device'):
             
            return self.catalog.addDevice(data["NAME"], data["IP"], data["PORT"])
        
          
        #%% Get user
        if (len(uri) == 2 and uri[0] == 'get' and uri[1] == 'user'):
             
            return self.catalog.getUser(data["ID"])


        #%% Add user
        if (len(uri) == 2 and uri[0] == 'add' and uri[1] == 'user'):
          
            out = self.catalog.addUser(data)
            if out == "Error":
                raise cherrypy.HTTPError(400)
            else:
                return out
                
                
        #%% Set nickname            
        elif (len(uri) == 2 and uri[0] == 'set' and uri[1] == 'nickname'):
             
            out = self.catalog.setNickname(data)
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out
           
               
        #%% verify buyer            
        elif (len(uri) == 2 and uri[0] == 'verify' and uri[1] == 'buyer'):
            
            out = self.catalog.verifyBuyer(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out
           
               
        #%% verify buyer            
        elif (len(uri) == 2 and uri[0] == 'verify' and uri[1] == 'pw'):
            
            out = self.catalog.verifyPassword(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out
               
               
        #%% set flag                             
        elif (len(uri) == 2 and uri[0] == 'set' and uri[1] == 'flag'):
            
            out = self.catalog.setFlag(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out   
            
               
         #%% remove user                             
        elif (len(uri) == 2 and uri[0] == 'remove' and uri[1] == 'user'):
            
            out = self.catalog.removeUser(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out      


         #%% set SMS                            
        elif (len(uri) == 2 and uri[0] == 'set' and uri[1] == 'sms'):
            
            out = self.catalog.setSMS(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out   
            
               
         #%% set number                            
        elif (len(uri) == 2 and uri[0] == 'set' and uri[1] == 'number'):
            
            out = self.catalog.setNumber(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out 


         #%% set new mail               
        elif (len(uri) == 2 and uri[0] == 'set' and uri[1] == 'mail'):
            
            out = self.catalog.setMail(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out                
               
               
         #%% set new pw               
        elif (len(uri) == 2 and uri[0] == 'set' and uri[1] == 'pw'):
            
            out = self.catalog.setPw(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out
            
        elif (len(uri) == 2 and uri[0] == 'remove' and uri[1] == 'device'):
            
            out = self.catalog.removeDevice(data)
            
            if out == "Error":
                raise cherrypy.HTTPError(400)     
            else:
                return out  
           
               
if __name__ == '__main__':
     

    # Clean devices json at the startup
    empty_devices = {"devices":[]}
     
    file = open("devices.json", 'w')
    file.write(json.dumps(empty_devices))
    file.close()
         
    fp = open("configCatalog.json", 'r')
    config = json.loads(fp.read())
    fp.close()
    
    key = config["DigestKey"]
    my_ip = config["IP_catalog"]
    my_port = config["PORT_catalog"]
    
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
                
    cherrypy.tree.mount(REST_Catalog(),'/',conf)    
    cherrypy.config.update({'server.socket_host': my_ip})
    cherrypy.config.update({'server.socket_port': my_port})
    cherrypy.engine.start()
    cherrypy.engine.block()
