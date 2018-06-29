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
import pprint
from library import xlrd
from config import config
from config import loggingImpl
import traceback
from builtins import str
"""
TODO:
get the value of xmnls:contr from the root tag, this should be used to search all the attributes
"""
from xml.dom.minidom import parse
import xml.dom.minidom
indent=0
demoList = []
counter = 1
log_path=config.project_path+"\\log\\fALU\\"

class fALUQualityOfServiceProfileParser:
    def __init__(self,input_dumpfile):
        #self.input_dir = input_dir
        self.xmlTree = None
        self.input_dumpfile = input_dumpfile
        print ("Input file name %s"%self.input_dumpfile)
        #self.xmlFileName = xmlFileName
        self.parseValues = list()
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Mapping Object OCSi for falu------********\n")
        self.f_gprs_100 = None
        self.f_gprs_102 = None
    
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
    def getFlagValuesFromTemplateSheet(self):
        workbook = xlrd.open_workbook (config.project_path +"\\templates" + "\\NSRdata_HLR_fALU.xlsm")
        worksheet = workbook.sheet_by_name(config.nokiaObjectName)
        self.f_gprs_100 = worksheet.cell_value(1,10)
        self.f_gprs_102 = worksheet.cell_value(1,12)
        #print("value of cell %s:%s"%(self.f_gprs_100,self.f_gprs_102))
                
    def parseObject(self,root):
        
        self.getFlagValuesFromTemplateSheet()
        for elem in root.iter('{sumNrm.xsd}GPacketProtocolProfileData'):
            global counter
            
            for elem in root.iter('{sumNrm.xsd}PacketDataProtocolProfile'):
                attribVal = {}
                attribVal['PacketDataProtocolProfile']  = elem.attrib['id']
                for elem1 in elem.iter('{sumNrm.xsd}delayClass'):
                    attribVal['delayClass'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}reliabilityClass'):
                    attribVal['reliabilityClass'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}precedenceClass'):
                    attribVal['precedenceClass'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}meanThroughPutClass'):
                    attribVal['meanThroughPutClass'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}trafficClass'):
                    attribVal['trafficClass'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}deliveryOrder'):
                    attribVal['deliveryOrder'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}transferDelay'):
                    attribVal['transferDelay'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}trafficHandlingPriority'):
                    attribVal['trafficHandlingPriority'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}priorityOfUmtsBearer'):
                    attribVal['priorityOfUmtsBearer'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}peakThroughPutClass'):
                    attribVal['peakThroughPutClass'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}deliveryOfErroneousSdu'):
                    attribVal['deliveryOfErroneousSdu'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}maxSduSize'):
                    attribVal['maxSduSize'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}uplinkMaxBR'):
                    attribVal['uplinkMaxBR'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}downlinkMaxBR'):
                    attribVal['downlinkMaxBR'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}residualBER'):
                    attribVal['residualBER'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}ratioSduError'):
                    attribVal['ratioSduError'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}uplinkGuaranteedBR'):
                    attribVal['uplinkGuaranteedBR'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}downlinkGuaranteedBR'):
                    attribVal['downlinkGuaranteedBR'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}hSUPAguaranteeFlag'):
                    attribVal['hSUPAguaranteeFlag'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}hSDPAguaranteeFlag'):
                    attribVal['hSDPAguaranteeFlag'] = elem1.attrib.get('name', elem1.text)
                for elem1 in elem.iter('{sumNrm.xsd}hSUPAflag'):
                    attribVal['hSUPAflag'] = elem1.attrib.get('name', elem1.text)  
                for elem1 in elem.iter('{sumNrm.xsd}hSDPAflag'):
                    attribVal['hSDPAflag'] = elem1.attrib.get('name', elem1.text)    
                attribVal['f_gprs_100'] = self.f_gprs_100
                attribVal['f_gprs_102'] = self.f_gprs_102        
                self.parseValues.append(attribVal)   
                counter +=1
            
        
    def openXML(self,path):
        self.xmlTree = ET.parse(path)
        xmlroot=self.xmlTree.getroot()
        #self.printRecur(xmlroot)
        #self.printAttributes(xmlroot)
        self.parseObject(xmlroot)
        #filename = "D://Data/demo.json"
        #filename = "D://Data/bearercapability.json" 
        #=======================================================================
        # filename = config.project_path+'/log/'+ config.nokiaObjectName + "Falu" + ".json"
        # with open(filename, 'w') as f:
        #     json.dump(self.parseValues , f , indent=4)
        #=======================================================================
        return self.parseValues
     
        
    def generateInputJson(self):
       filename = self.generateFaluQualityOfServiceProfileJson(self.input_dumpfile)
       return filename
             
            
        
    def generateFaluQualityOfServiceProfileJson(self,path):
        self.xmlTree = ET.parse(path)
        xmlroot=self.xmlTree.getroot()
        self.parseObject(xmlroot)

        filename = log_path + config.nokiaObjectName + "\\" +config.nokiaObjectName + "Falu" + ".json"
        with open(filename, 'w') as f:
            json.dump(self.parseValues , f , indent=4)
        
        return filename
if __name__ == '__main__':
        ParserObj = fALUQualityOfServiceProfileParser(sys.argv[1])
        
        parserValues = ParserObj.openXML()
        pp = pprint.PrettyPrinter(depth=6)    
        pp.pprint(parserValues)

