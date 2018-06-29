'''
Created on 14-May-2018

@author: vkhanna
'''
import xml.etree.ElementTree as ET
import copy
import logging
import os
import sys
import json
from config import config
from config import loggingImpl
from utility.ApplicationException import ApplicationError
"""
TODO:
get the value of xmnls:contr from the root tag, this should be used to search all the attributes
"""
indent=0
log_path=config.project_path+"\\log\\fALU\\"
class fALUPDPCONTEXTparser:
    def __init__(self,xmlFileName):
        self.xmlFileName = xmlFileName
        self.xmlTree = None
        self.parseValues = list()
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("Inside file faluBCDParsers--- \n")
    
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
                self.printAttributes(elem)
            
    def parseObject(self,root):
        for elem in root.iter('{sumNrm.xsd}PacketDataProtocolProfile'):
            attribVal = {} 
            valueList = []
            attribVal['PacketDataProtocolProfile']  = "PDP"+ elem.attrib['id'] 
            
            for elem1 in elem.iter('{sumNrm.xsd}vplmnAddressAllowedFlag'):
                attribVal['vplmnAddressAllowedFlag'] = elem1.attrib.get('name', elem1.text)
            for elem2 in elem.iter('{sumNrm.xsd}accessPointName'):
                attribVal['accessPointName'] = elem2.attrib.get('name', elem2.text)   
            for elem3 in elem.iter('{sumNrm.xsd}pdpType'):
                attribVal['pdpType'] = elem3.attrib.get('name', elem3.text) 
                if (elem3.attrib.get('name', elem3.text) == "IPV4V6"):
                    attribVal['extType'] = "5"
                    attribVal['pdpType'] = "NA"
                elif (elem3.attrib.get('name', elem3.text) != "IPV4V6"):    
                    attribVal['extType'] = "NA"
            for elem4 in elem.iter('{sumNrm.xsd}pdpChargingCharacteristic'):
                valueList.append(elem4.attrib.get('name', elem4.text))
                if(len(valueList) >= 1):
                    attribVal['pdpChargingCharacteristic'] = ",".join(str(item) for item in valueList[:] )   
            
            if (attribVal['PacketDataProtocolProfile'] != None):   
                attribVal['chargingCharacteristicsBehavior'] = "0"
                                    
            self.parseValues.append(attribVal)   
            
        
    def openXML(self):
        self.xmlTree = ET.parse(self.xmlFileName)
        xmlroot=self.xmlTree.getroot()
        self.parseObject(xmlroot)
        filename = log_path+config.nokiaObjectName+"\\PDPContextFalu" + ".json"
        with open(filename, 'w') as f:
            json.dump(self.parseValues , f , indent=4)
        return self.parseValues
        """
        DOMTree = xml.dom.minidom.parse(self.xmlFileName)
        collection = DOMTree.documentElement
        print collection
        if collection.hasAttribute("contr:ServiceCodeMnemonic"):
            print "inside"
            ident = collection.getElementsByTagName("contr:ServiceCodeMnemonic")
        """
    def generateInputJson(self):
        filename = log_path+config.nokiaObjectName+'\\fALU_PDPContext.json'
        try:
            parserValues = self.openXML()
            with open(filename, 'w') as f:
                json.dump(parserValues , f , indent=4)
        except(Exception):
            self.logger.error("Input file missing:-"+self.xmlFileName)
            raise ApplicationError("Input file missing for object:-  "+config.nokiaObjectName)
        return filename
#===============================================================================
# if __name__ == '__main__':
#         ParserObj = fALUPDPCONTEXTparser(sys.argv[1])
#         
#         parserValues = ParserObj.openXML()
#         pp = pprint.PrettyPrinter(depth=6)    
#         pp.pprint(parserValues)
#===============================================================================
    