#!/usr/bin/python3
# -*- coding: utf-8 -*-



import sys
from PyQt5.QtWidgets import (QWidget, QAction, QLabel,QMenuBar, QMenu,qApp,QPushButton,
                            QFrame, QLineEdit, QGridLayout, QApplication,QListWidgetItem,QListWidget)
from PyQt5.QtGui import QColor, QFont, QPainter ,QIcon 
from PyQt5 import QtWidgets 
from PyQt5.Qt import QStatusBar, QMainWindow, QDialog
from threading import Thread
import socket
import time
import os
import re
import Handler


PORT = Handler.PORT
PSIZE = Handler.PSIZE
LOC_IP = "127.0.0.1"
NOK = "47%OK"
OK = "48%OK%" 
PING = "49%PING%"
PONG = "50%PONG%"
ENDE = "57%ENDE%"
FILE_SIZE = "51%FSIZE%"
FILE_NAME = "52%FNAM%"
DIR_NAME = "53%DNAM%"
HOME_DIR = "54%HDIR%"
FILE_START = "55%FSTART%"
FILE_END = "56%FEND%"
SHUT_DOWN = "58%SHTDWN%"
FILE_INFO = "59%FINFO%"


class SendingHandler(Thread):
    def __init__(self,parent,fileordir,pad):
        Thread.__init__(self)
        self.parent = parent
        self.s = socket        
        self.f = fileordir
        self.d = pad
        self.RunFlag = True
        self.SockClosed = False
        
    def connectit(self):
        s = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)            
            s.connect((LOC_IP, PORT))            
            ping = PING.encode('ascii').ljust(PSIZE,b'0')            
            s.send(ping)      
            pong = s.recv(PSIZE)           
            ans = pong.decode('ascii')                        
            print("first pong",ans) 
        except:
            print("No socket connection possible")
            s.close()
            s = None
        return s    
        
        
    def run(self):
        s = self.connectit()
        if s == None:
            return            
        print("run Sending handler")
        
        time.sleep(2)
        
        s.close() 
        self.SockClosed = True
        
 

class XFrame(QFrame):
      
    def __init__(self,parent):
        super().__init__(parent)
        self.name = "Jeff"
        self.par = parent
        self.setAcceptDrops(True)
        self.path_str = "no_init"
        self.standard_bgcol = self.backgroundRole() 
        
        self.pad_data={'name':self.name,'port':PORT,'ip':"",'dir':""}
        
        self.msglen = PSIZE
        self.colordirtable = {'Red':'dir1','Blue':'dir2','Green':'dir3','Yellow':'dir4'}
        self.hands = []
   
       
    def start_con(self,fnam1):
        print("gui send :"+fnam1+":")
                
        # for each interaction a new handler ist stored in the list
        h = Handler.Handler(None,2,fnam1)
        h.start()     
        self.hands.append(h)
        
        # remove old handlers
        #self.hands = list(filter(lambda x: x.SockClosed == False,self.hands))
         
     
    def dragEnterEvent(self, e):      
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore() 

    def dropEvent(self, e): 
        mycol = self.name
        
        pstr = e.mimeData().text().rstrip(" \r\n")     
        
        if "file://" in pstr:
            pstr = pstr[len("file://"):]   
                   
        self.path_str = pstr 
        print(e.mimeData().text(),mycol)
        self.repaint()  
              
        self.start_con(self.path_str)
                
    def paintEvent(self, event):
        qp = QPainter()
        qp.begin(self)
        self.draw_rect(event, qp)
        qp.end()
        
    def draw_rect(self,event, qp):
        #Black Rectangle
        col = QColor("White")
        col.setNamedColor("White")
        qp.setPen(col)

        qp.setBrush(QColor("White"))
        qp.drawRect(5,40,80,13)

        #formato
        qp.setPen(QColor("Black"))
        qp.setFont(QFont('Helvetica', 10))
        qp.drawText(10, 50, self.name)#path_str) 
        
    def contextMenuEvent(self, event):       
        cmenu = QMenu(self)        
        cmenu.setStyleSheet("QWidget { background-color: gray; color: black;selection-background-color: #f0f0f0 }" )
          
        setAct = cmenu.addAction("Settings")
        #opnAct = cmenu.addAction("Open")
        quitAct = cmenu.addAction("Quit")
        action = cmenu.exec_(self.mapToGlobal(event.pos()))
       
        if action == quitAct:
            qApp.quit()  
        elif action == setAct:
            print("settings of",self.name)
            
            pdialog = PadDialog(self.par,)
            if pdialog.exec_() == QDialog.Accepted: 
                self.pad_data = pdialog.GetValue()
                
  
                  
    

class Pads(QWidget):
    
    def __init__(self,parent):
        # Pads contains the four Frames/Squares 
        super().__init__()        
        self.parent = parent  
        
        self.initUI()        
        
    def initUI(self):
        
        grid = QGridLayout()
        self.setLayout(grid)        
        
        cols = ['Red', 'Blue', 'Green', 'Yellow']
        
        positions = [(i,j) for i in range(2) for j in range(2)]
        
        for position, col in zip(positions,cols):
            
            if col == '':
                continue
            
            square = XFrame(self)
            square.setGeometry(10, 10, 100, 100)
           
            square.setStyleSheet("QWidget { background-color: %s }" % col )           
            
            grid.addWidget(square, *position)
            
        #self.move(300, 150)
        self.setGeometry(300, 150, 800, 800)
        #self.setWindowTitle('PyDrop ' + self.version)
        
        
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)
        
        self.show()
       
     
class MainWin(QMainWindow):
    
    def __init__(self):
        super().__init__()        
        self.initUI()              
        
    def initUI(self):               
        # MainWindows has the status bar and the menu strip 
        
        # pads contains the four squares
        pads = Pads(self)        
        self.setCentralWidget(pads)  
        
        # MenuBar
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        
        self.statusBar().showMessage('Ready')
        
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle('PyFileSling v0.1')    
        self.show()        
        
   
   
class PadDialog(QDialog):
    def __init__(self, parent=None,pad_data={'name':'Jeff'}):
        super(PadDialog, self).__init__(parent)
        self.result = ""
        self.name = pad_data['name']
            
            
        layout = QGridLayout()       
        row=0
        
        l_ip = QLabel("Name:")  
        layout.addWidget(l_ip,row,0)
        self.namefield = QLineEdit(self.name)
        layout.addWidget(self.namefield,row,1)
        
        row += 1
        l_ip = QLabel("IP-Address:")  
        layout.addWidget(l_ip,row,0)
        self.ipfield = QLineEdit("127.0.0.1")
        layout.addWidget(self.ipfield,row,1)
        
        row += 1
        l_port = QLabel("Port:")  
        layout.addWidget(l_port,row,0)
        self.portfield = QLineEdit(str(PORT))
        layout.addWidget(self.portfield,row,1)
        
        row += 1
        l_port = QLabel("Directory:")  
        layout.addWidget(l_port,row,0)
        self.dirfield = QLineEdit("/home/augusta/...")
        layout.addWidget(self.dirfield,row,1)     
        
        #================================================= ===============================
        # OK, Cancel
        #================================================= ===============================
        row +=1
        self.but_ok = QPushButton("OK")
        layout.addWidget(self.but_ok ,row,2)
        self.but_ok.clicked.connect(self.OnOk)
        
        self.but_cancel = QPushButton("Cancel")
        layout.addWidget(self.but_cancel ,row,3)
        self.but_cancel.clicked.connect(self.OnCancel)
        
        #================================================= ===============================
        #
        #================================================= ===============================
        self.setWindowTitle('PyFileSling v0.1')   
        self.setLayout(layout)
        self.setGeometry(300, 200, 460, 350)
        
    
    def OnOk(self):
        print("onok")
        
        name = self.namefield.text()
        ip = self.ipfield.text()
        port = self.portfield.text()
        dir  = self.dirfield.text()  
        
        self.pad_data = {'name':name,'port':port,'dir':dir,'ip':ip}        
            
        self.close()        
        return "OK"
        
    def OnCancel(self):
        self.close()    
    
    def GetValue(self):
        return self.pad_data 
            
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MainWin()
    sys.exit(app.exec_())
    
    #hx = Handler.Handler(None,2,r'/home/od/zeug/test/')
    #hx.start()
    
    
    
