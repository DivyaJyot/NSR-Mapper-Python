'''
Created on 28-Mar-2018

@author: djyoti
'''
import json

class JSONUtil:
    @staticmethod
    def writeDictInJsonFile(inputdict,filepath):
        with open(filepath, 'w') as f:
            json.dump(inputdict, f, indent=4) 
     
    @staticmethod       
    def getJsonObjectWithVal(inputlist,key,val):
        for obj in inputlist:
            if (obj[key] == val):
                return obj
                
        