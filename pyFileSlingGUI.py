#!/usr/bin/python3
# -*- coding: utf-8 -*-



import sys
from PyQt5.QtWidgets import (QWidget, QAction, QMenuBar, QMenu,qApp,
                            QFrame, QGridLayout, QApplication)
from PyQt5.QtGui import QColor, QFont, QPainter ,QIcon
from PyQt5 import QtWidgets 
from PyQt5.Qt import QStatusBar, QMainWindow

class XFrame(QFrame):
      
    def __init__(self,parent,name):
        super().__init__(parent)
        self.name = name
        self.setAcceptDrops(True)
        self.path_str = "no_init"
        self.standard_bgcol = self.backgroundRole() 
                                

    def dragEnterEvent(self, e):
      
        if e.mimeData().hasFormat('text/plain'):
            e.accept()
        else:
            e.ignore() 

    def dropEvent(self, e):       
        
        mycol = self.name
        self.path_str = e.mimeData().text()
        print(e.mimeData().text(),mycol)
        self.repaint()
                
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
                  
    

class Pads(QWidget):
    
    def __init__(self,parent):
        super().__init__()
        
        self.parent = parent
        self.version = "v 0.1"
        
        self.initUI()
        
        
    def initUI(self):
        
        grid = QGridLayout()
        self.setLayout(grid)        
        
        names = ['Red', 'Blue', 'Green', 'Yellow']
        
        positions = [(i,j) for i in range(2) for j in range(2)]
        
        for position, name in zip(positions, names):
            
            if name == '':
                continue
            
            square = XFrame(self,name)
            square.setGeometry(10, 10, 100, 100)
           
            square.setStyleSheet("QWidget { background-color: %s }" % name )           
            
            grid.addWidget(square, *position)
            
        #self.move(300, 150)
        self.setGeometry(300, 150, 800, 800)
        self.setWindowTitle('PyDrop ' + self.version)
        
        
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
        
        
        pads = Pads(self)        
        self.setCentralWidget(pads)       
        
        
        # MenuBar
        exitAct = QAction(QIcon('exit.png'), '&Exit', self)        
        exitAct.setShortcut('Ctrl+Q')
        exitAct.setStatusTip('Exit application')
        exitAct.triggered.connect(qApp.quit)

        self.statusBar()

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('&File')
        fileMenu.addAction(exitAct)
        
        self.statusBar().showMessage('Ready')
        
        self.setGeometry(100, 100, 500, 500)
        self.setWindowTitle('Simple menu')    
        self.show()        
   
        
if __name__ == '__main__':
    
    app = QApplication(sys.argv)
    ex = MainWin()
    sys.exit(app.exec_())
