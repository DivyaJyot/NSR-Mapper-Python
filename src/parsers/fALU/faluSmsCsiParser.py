'''
Created on 14-May-2018

@author: vivek
'''
import xml.etree.ElementTree as ET
import logging
import os
import json
from config import config
from config import loggingImpl
from builtins import str
from utility.ApplicationException import ApplicationError
from parsers.fALU.falusmscsiSubscription import fALUSMSCSISubscription
"""
TODO:
get the value of xmnls:contr from the root tag, this should be used to search all the attributes
"""
indent=0
log_path=config.project_path+"/log/fALU/"
demoList = []
counter = 1


class fALUSmsCSIparser:
    def __init__(self,input_dumpfile):
        #self.input_dir = input_dir
        self.xmlTree = None
        self.input_dumpfile = input_dumpfile
        print ("Input file name %s"%self.input_dumpfile)
        #self.xmlFileName = xmlFileName
        self.parseValues = list()
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Mapping Object SmsCsi for falu------********\n")
        
    
    def printRecur(self,root):
        global indent
        print (' '*indent + '%s: %s' % (root.tag.title(), root.attrib.get('name', root.text)))
        indent += 4
        for elem in root.getchildren():
            self.printRecur(elem)
        indent -= 4

    def printAttributes(self,root):
        self.logger.debug ("Inside printAttributes %s " % root.tag.title())
        if root.tag.title() == "{Sumnrm.Xsd}Attributes":
            self.logger.debug ("returning from here")
            return root
        else:
            for elem in root.getchildren():
                #print "%s: %s" % ( elem.tag.title() , elem.attrib.get('name', root.text))
                self.printAttributes(elem)
            
    def parseObject(self,root):
        for elem in root.iter('{sumNrm.xsd}GsmServiceProfile'):
            attribVal = {}
            global counter 
            valueList = []
            attribVal['GsmServiceProfile']  = "SmsCSI_"+ str(counter) 
            
            for elem1 in elem.iter('{sumNrm.xsd}smocsiCollectedInfoTdpScpIsdn'):
                attribVal['smocsiCollectedInfoTdpScpIsdn'] = elem1.attrib.get('name', elem1.text)
            for elem2 in elem.iter('{sumNrm.xsd}smocsiCollectedInfoTdpServKey'):
                attribVal['smocsiCollectedInfoTdpServKey'] = elem2.attrib.get('name', elem2.text)   
            for elem3 in elem.iter('{sumNrm.xsd}RoamingRestrictionType'):
                attribVal['RoamingRestrictionType'] = elem3.attrib.get('name', elem3.text) 
            for elem4 in elem.iter('{sumNrm.xsd}smocsiCollectedInfoTdpScpIsdn'):
                attribVal['smocsiCollectedInfoTdpScpIsdn'] = elem4.attrib.get('name', elem4.text)
                if (elem4.attrib.get('name', elem4.text) != None):
                    attribVal['triggerDetectionPoint'] = "2"
            for elem5 in elem.iter('{sumNrm.xsd}smocsiCollectedInfoTdpDfltCalH'):
                attribVal['smocsiCollectedInfoTdpDfltCalH'] = elem5.attrib.get('name', elem5.text)  
            for elem7 in elem.iter('{sumNrm.xsd}smocsiCamelCapabilityHandling'):
                attribVal['smocsiCamelCapabilityHandling'] = elem7.attrib.get('name', elem7.text)
            self.parseValues.append(attribVal)   
            counter +=1
            
        
    def openXML(self,path):
        self.xmlTree = ET.parse(path)
        xmlroot=self.xmlTree.getroot()
        
        self.parseObject(xmlroot)
        filename = log_path+config.nokiaObjectName+"\\SmsCsiFalu" + ".json"
        with open(filename, 'w') as f:
            json.dump(self.parseValues , f , indent=4)
        return self.parseValues
   
   
    def iterateCSV(self):
        listofCSVFiles = []
        for root, dirs, filenames in os.walk(self.input_dumpfile):
            for f1 in filenames:                
                if (f1.endswith(".csv")):
                    listofCSVFiles.append(self.input_dumpfile + "//" + str(f1))
        return listofCSVFiles   
                    
    def generateInputJson(self):
        self.logger.debug("Input selected is---"+self.input_dumpfile )
        if(os.path.isfile(self.input_dumpfile)):
            path =self.input_dumpfile
            if(".csv" in path):
                listFiles = []
                listFiles.append(path)
                SubscriptionObj = fALUSMSCSISubscription(listFiles)
                inputFile=SubscriptionObj.generateFaluSMSCSISubscriptionJson()
            else:    
                inputFile=self.generateFaluOCSIJson(path)
        else:
            listFiles = []
            for root, dirs, filenames in os.walk(self.input_dumpfile):
                listFiles = self.iterateCSV()            
                if (len(listFiles) != 0 ):
                    #logic written here 
                    SubscriptionObj = fALUSMSCSISubscription(listFiles)
                    inputFile=SubscriptionObj.generateFaluSMSCSISubscriptionJson()             
                else:    
                    for f1 in filenames:                                  
                        path = self.input_dumpfile + "//" + str(f1)        
                        inputFile=self.generateFaluOCSIJson(path)
        return inputFile            
           
    def generateFaluOCSIJson(self,path):
        filename = log_path+config.nokiaObjectName+'\\fALU_SmsCsi.json'
        try:
            parserValues = self.openXML(path) 
            latestdict = {}
            
            for i in parserValues:
                for k, v in i.items():
                    latestdict[k] = v            
            demoList.append(latestdict)
            
            with open(filename, 'w') as f:
                json.dump(demoList , f , indent=4)
        except(FileNotFoundError):
            self.logger.error("Input file missing:-"+self.xmlFileName)
            raise ApplicationError("Input file missing for object:-  "+config.nokiaObjectName)
        except(Exception):
            logging.exception("Error while parsing input dump, check for the correct format")  
            raise
        return filename
