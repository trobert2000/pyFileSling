#!/usr/bin/python3
'''
Created on Jun 13, 2019

@author: od
'''

import socket
import sys
import time
from threading import Thread
import re
from sys import argv
import json
import os

PORT = 40002
PSIZE = 128
LOC_IP = "127.0.0.1"


class Handler(Thread):
    
    CMD_NOK = "47%NOK%"
    CMD_OK = "48%OK%" 
    CMD_PING = "49%PING%"
    CMD_PONG = "50%PONG%"    
    CMD_SFILE = "52%FNAM%"    
    CMD_MKDIR = "53%MKDIR%"
      
    CMD_FILE_END = "56%FEND%"  
    CMD_ENDE = "57%ENDE%"
    CMD_SHTDWN = "58%SHTDWN%"
    
    FILE_SIZE = "51%FSIZE%"
    
    HOME_DIR = 54
    FILE_START = "55%FSTART%" 
    FILE_END = 56    
    
    FILE_INFO = "59%FINFO%"
    CON_TYPE_SERVER = 1
    CON_TYPE_CLIENT = 2
    
    
    def __init__(self,sock=None,con_type=0,dirorfiletosend=""):
        Thread.__init__(self)
        
        self.sock = sock
        self.RunFlag = True
        self.SockedClosed = False
        self.CON_TYPE = con_type
        self.my_path = dirorfiletosend
        
        if dirorfiletosend == "":
            print("handler out")
            self.RunFlag = False
        
        
        
    def run_server(self):
        print("run server")
        ret_msg = self.CMD_PONG
        cnt = 0
        freccnt = 0
        while self.RunFlag:# and cnt < 50:
            ret_msg = self.CMD_NOK  
            ans = self._decmsg()
            print(freccnt,"s",ans)
            
            if ans.find(self.CMD_PING) == 0:
                print("pong")         
                ret_msg = self.CMD_PONG       
            elif ans.find(self.CMD_SFILE) == 0:                
                print("serv getf")
                ze = self._getdatafrommsg(ans)
                path = os.path.join(self.my_path,ze[2])
                myd,tail = os.path.split(path)
                print("s file rec:",myd,tail,path,ze[3])                
                if os.path.isdir(myd):
                    self._sendp(self.CMD_OK)   
                    time.sleep(0.2)  
                    self._recvfile(path,int(ze[3]))
                    ret_msg = self.CMD_OK
                    freccnt+=1
                else:
                    # no transmission
                    ret_msg = self.CMD_NOK            
            elif ans.find(self.CMD_FILE_END) == 0:
                print("s file end")
                ret_msg = self.CMD_OK
            elif ans.find(self.CMD_MKDIR) == 0:                
                ze = self._getdatafrommsg(ans)  
                self._mkdir(ze[2])                
                ret_msg = self.CMD_OK                      
            elif ans.find(self.CMD_SHTDWN) == 0:
                self.RunFlag = False  
                #ret_msg = self.CMD_OK 
                 
            else:
                print("?")
                return                     
                
            self._sendp(ret_msg)
            time.sleep(0.2)  
            
            cnt+=1
    
    def run_client(self):
        print("run client",self.my_path)
        
        fdata = self._getfilestosend(self.my_path)
        print(len(fdata))
        self.sock = self._connect()
        
        # directories before files        
        for dir in (v for _,v in fdata.items() if v['t'] == 'd'):     
            msg = self.CMD_MKDIR + dir['remp'] + "%"       
            print("cli",msg)
            self._sendp(msg) 
            time.sleep(0.1)         
            ans = self._decmsg()
            if ans.find(self.CMD_OK) == 0:
                print("rec ok")
                
                for file in (v for _,v in fdata.items() if v['t'] == 'f'):     
                    self._sendfile(file)
                    self._sendp(self.CMD_FILE_END)  
                    time.sleep(0.1)          
                    ans = self._decmsg() 
                    print("cli after fend",ans)
            
            else:
                print("rec nok break")
                break 
        #    if v['t'] == 'f':
        #        self._sendfile(v)
        
        self._sendp(self.CMD_SHTDWN)
       
    def run(self):
        print("Handler")
        if self.RunFlag == False:
            return        
                  
        if self.CON_TYPE == self.CON_TYPE_CLIENT:
            print("as client")
            self.run_client()            
        elif self.CON_TYPE == self.CON_TYPE_SERVER:
            print("as server")            
            self.run_server()  
        else:
            print("no connection type set")  
                
        self.sock.close()
        self.SockedClosed = True
        print("sock closed")
    
    def _mkdir(self,dir):  
        print("mkdir",dir,self.my_path)
        retval = False
        target_dir = self.my_path + os.path.sep + dir
        
        if not os.path.isdir(target_dir):            
            os.mkdir(target_dir)   
            
        if os.path.isdir(target_dir):          
            retval = True
        
        return retval    
        
    def _sendfile(self,finfo):
        print("sendf",finfo)  
        binpath = finfo['p']
        fsize = finfo['s']
        rempath = finfo['remp']
        msg = self.CMD_SFILE + rempath + "%" + str(fsize) + "%" 
        print("sendf msg",msg)
        self._sendp(msg) 
        time.sleep(0.1)         
        ans = self._decmsg()
        if ans.find("OK") > -1:
            print("sfile ok rec by cli")
            s = self.sock
            bcnt = 0
            with open(binpath,"rb") as fb:  
                    buf = fb.read(PSIZE)
                    bcnt = len(buf)                    
                    while buf and bcnt < int(fsize):   
                        s.send(buf)
                        buf = fb.read(PSIZE)
                        bcnt += len(buf)
                        if bcnt > fsize-PSIZE :
                            pass 
                        #print("l",len(buf)) 
                        
              
        print("end file send",binpath)                
                    
    def _recvfile(self,path,fsize):
        print("s recv f",path,fsize,self.my_path)
        s = self.sock
        bcnt = 0     
        with open(path,"wb") as fb:
            while bcnt < fsize:
                buf = s.recv(PSIZE)                
                l = len(buf)
                bcnt += l
                
                wbuf = []
                if bcnt <= fsize:
                    wbuf = buf
                else:        
                    diff = bcnt - fsize
                    wbuf = buf[:-1*diff]
                fb.write(wbuf)
                
        print("s end  recf")  
          
    
    def _getfilestosend(self,rdir):
        
        fdata = {}                
        if os.path.isdir(rdir):
            idx = rdir.rfind(os.path.sep)
            loc_dir = rdir[idx+1:]        
            #print("g1",loc_dir)
            # add the dir that has been dragged'n'dropped into window
            #fdata[loc_dir] = {'t':'d','p':'','s':0,'remp':loc_dir}
            for rd,sf,fs in os.walk(rdir):
                for f in fs:     
                    #  path to read              
                    path = os.path.join(rd,f)
                    # remote path conmplete
                    rempath = path[len(self.my_path)+1:]
                    # remote only directory
                    remdir = loc_dir+ os.path.sep + rempath[:-len(f)-1]                   
                    #                     
                    rem_file_path = loc_dir + os.path.sep + rempath
                    
                    
                    # add the directory of any file if it is not already in there                                         
                    if not remdir in fdata and len(remdir) > 0 and remdir != os.path.sep:
                        fdata[remdir] = {'t':'d','p':'','s':0,'remp':remdir}
                        
                    if os.path.isfile(path) and not rem_file_path in fdata:                        
                        fsize = os.path.getsize(path)                        
                        fdata[rem_file_path] = {'t':'f','p':path,'s':fsize,'remp':rem_file_path}
                     
        # single file                                  
        elif os.path.isfile(rdir):
            print("g3",rdir)
            fsize = os.path.getsize(rdir) 
            _,rempath = os.path.split(rdir)
            fdata['k'] = {'t':'f','p':rdir,'s':fsize,'remp':rempath}
           
        return fdata    
    
    def _decmsg(self):
        msg_b = self.sock.recv(PSIZE)
        return msg_b.decode('ascii')
    
    def _sendp(self,msg):  
        print("send",msg)      
        self.sock.send(msg.encode('ascii').ljust(PSIZE,b'0'))
        
    def _connect(self):        
        s = None        
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
        s.connect((LOC_IP, PORT))            
        ping = self.CMD_PING.encode('ascii').ljust(PSIZE,b'0')            
        s.send(ping)         
        pong = s.recv(PSIZE)           
        ans = pong.decode('ascii')                        
        print("first pong",ans)         
        return s     
        
    def _getdatafrommsg(self,msg):
        ze = re.split("%",msg)
        return ze    
    
    def _joinpath(self,p1,p2):                
        return p1.rstrip(os.path.sep) + os.path.sep + p2

        
        
