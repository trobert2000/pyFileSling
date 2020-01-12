#!/usr/bin/python3


import socket
import sys
import time
from threading import Thread
import re
from sys import argv
import json
import os
import Handler


PORT = Handler.PORT
PSIZE = Handler.PSIZE
LOC_IP = "127.0.0.1"
            
######################################################################################
#
#    awaits a file or directory sent by the client            
# 
#######################################################################################
class pyFileSlingServer(Thread):
    def __init__(self,port_number,name="bronson"):
        Thread.__init__(self)
        print("init")
        self.dir = dir
        self.port = PORT
        self.name = name
        
        self.cfile = r'fsling.json'
        self.config = self.loadconfig()
        #self.savejson(self.cfile,self.config)
        self.msglen = PSIZE
        self.RunFlag = True
       

    def run(self):
        s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        s.bind(("",self.port))   
        s.listen(10) # Accepts up to 10 connections.
        
        
        cnt = 0
        while self.RunFlag and cnt < 2: 
            print(cnt,"server started, waiting...")
            sc, address = s.accept()
            print("accepted ",sc,address)      
            
            h = Handler.Handler(sc,1,r'/data1/zeug')            
            h.start()
            time.sleep(3)            
            cnt += 1
            
        s.close()
        print("server end1 ",cnt)
     
    def loadconfig(self):
        try:            
            self.config = self.loadjson(self.cfile)
            print("loaded",self.config)
        except:
            print("Error loading config\n\ncreate default file\n")    
            
        
    def savejson(self,fnam,data):  
        try:      
            with open(fnam,"w") as f:
                json.dump(data,f,indent=4)
        except:
            print("Error saving",fnam)       
            
    def loadjson(self,fnam):
        data = []
        try:
            with open(fnam,"r") as f:
                data = json.load(f)
        except:
            print("Error loading",fnam)       
        return data            
    
    def makedirs(self,rdir):
        dirs = [self.config['dir1'],self.config['dir2'],self.config['dir3'],self.config['dir4']]
        
        for d in dirs:
            path = os.path.join(rdir,d)
            if not os.path.isdir(path):
                try:
                    os.mkdir(path)
                    print(path,"not found - created") 
                except:
                    print("Error creating ",path)    
    
    
    def stop(self):
        print("sling stop")
        self.RunFlag = False
        
            
if __name__ == "__main__":
    dir,port = "./data",PORT      
        
    for ar in argv:
        print(ar)        
        
    P = pyFileSlingServer(dir,port)
    P.start()   
    
    