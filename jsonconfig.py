'''
Created on Jan 19, 2020

@author: od
'''
import json


def savejson(fnam, data):  
    try:      
        with open(fnam, "w") as f:
            json.dump(data, f, indent=4)
    except:
        print("Error saving", fnam)       

            
def loadjson(fnam):
    data = []
    try:
        with open(fnam, "r") as f:
            data = json.load(f)
    except:
        print("Error loading", fnam)       
    return data       
