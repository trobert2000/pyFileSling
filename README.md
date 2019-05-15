# pyFileSling
Deployment tool for sending files over the network to up to four clients.

Regularly programming the raspberry pi I needed at tool to easily send a new version of my code file to the raspi. Therefore I created a tool where I can drag and drop a file onto a GUI and this sends the file to the raspi where it can be executed. 

The GUI part is created with PyQt5 and can be configured to send the file to up to four receiving stations. 
The receiving part is a python socket server.   
