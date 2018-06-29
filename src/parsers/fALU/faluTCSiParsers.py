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
from parsers.fALU.falutcsiSubscription import fALUTCSISubscription
"""
TODO:
get the value of xmnls:contr from the root tag, this should be used to search all the attributes
"""
indent=0
log_path=config.project_path+"/log/fALU/"
demoList = []
counter = 1


class fALUTCSIparser:
    def __init__(self,input_dumpfile):
        #self.input_dir = input_dir
        self.xmlTree = None
        self.input_dumpfile = input_dumpfile
        print ("Input file name %s"%self.input_dumpfile)
        #self.xmlFileName = xmlFileName
        self.parseValues = list()
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Mapping Object OCSi for falu------********\n")
        
    
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
            attribVal['GsmServiceProfile']  = "TCSi_"+ str(counter) 
            
            for elem1 in elem.iter('{sumNrm.xsd}tcsiCamelGmscNotSuppDfltHandl'):
                attribVal['tcsiCamelGmscNotSuppDfltHandl'] = elem1.attrib.get('name', elem1.text)
            for elem2 in elem.iter('{sumNrm.xsd}camelLocationRequestFlag'):
                attribVal['camelLocationRequestFlag'] = elem2.attrib.get('name', elem2.text)   
            for elem3 in elem.iter('{sumNrm.xsd}camelStatusRequestFlag'):
                attribVal['camelStatusRequestFlag'] = elem3.attrib.get('name', elem3.text) 
            for elem4 in elem.iter('{sumNrm.xsd}tcsiTermAttemptTdpScpIsdn'):
                attribVal['tcsiTermAttemptTdpScpIsdn'] = elem4.attrib.get('name', elem4.text)
                if (elem4.attrib.get('name', elem4.text) != None):
                    attribVal['tdpid'] = "12"
            for elem5 in elem.iter('{sumNrm.xsd}tcsiTermAttemptTdpServKey'):
                attribVal['tcsiTermAttemptTdpServKey'] = elem5.attrib.get('name', elem5.text)  
            for elem6 in elem.iter('{sumNrm.xsd}tcsiTermAttemptTdpDfltCalH'):
                attribVal['tcsiTermAttemptTdpDfltCalH'] = elem6.attrib.get('name', elem6.text) 
            for elem7 in elem.iter('{sumNrm.xsd}tcsiCamelCapabilityHandling'):
                valueList.append(elem7.attrib.get('name', elem7.text))
                if (len(valueList) >= 1):
                    #attribVal['ocsiCamelCapabilityHandling'] = valueList  
                    attribVal['tcsiCamelCapabilityHandling'] = ",".join(str(item) for item in valueList[:] )    
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
        #filename = config.project_path+'/inputFiles/'+"TCsiFalu" + ".json"
        filename = log_path+config.nokiaObjectName+"\\TCsiFalu" + ".json"
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
                SubscriptionObj = fALUTCSISubscription(listFiles)
                inputFile=SubscriptionObj.generateFaluTCSISubscriptionJson()
            else:    
                inputFile=self.generateFaluOCSIJson(path)
        else:        
            listFiles = []
            for root, dirs, filenames in os.walk(self.input_dumpfile):
                listFiles = self.iterateCSV()            
                if (len(listFiles) != 0 ):
                    #logic written here 
                    SubscriptionObj = fALUTCSISubscription(listFiles)
                    inputFile=SubscriptionObj.generateFaluTCSISubscriptionJson()             
                else:    
                    for f1 in filenames:                                  
                        path = self.input_dumpfile + "//" + str(f1)        
                        inputFile=self.generateFaluOCSIJson(path)
        return inputFile         
        
    def generateFaluOCSIJson(self,path):
        #filename = "D://Data/falu_bearercapability.json" 
        #filename = config.project_path+'/inputFiles/fALU_TCsi.json'
        filename = log_path+config.nokiaObjectName+'\\fALU_TCsi.json'
        
        
        try:
            parserValues = self.openXML(path) 
            latestdict = {}
            
            for i in parserValues:
                for k, v in i.items():
                    latestdict[k] = v            
            demoList.append(latestdict)
            #===================================================================
            # TempList=[]
            # TempList.append(parserValues)
            #===================================================================
            #===================================================================
            # with open(filename, 'w') as f:
            #     json.dump(parserValues , f , indent=4)
            #===================================================================
            
            with open(filename, 'w') as f:
                json.dump(demoList , f , indent=4)
            #self.logger.debug(" ****************************** fALUAttributeSet structure %d ***************"%len(parserValues))
            #pp = pprint.PrettyPrinter(depth=6)    
        
            #pp.pprint(parserValues)
        
            #print("***************************************************************")
        except(FileNotFoundError):
            self.logger.error("Input file missing:-"+self.xmlFileName)
            raise ApplicationError("Input file missing for object:-  "+config.nokiaObjectName)
        except(Exception):
            logging.exception("Error while parsing input dump, check for the correct format")  
            raise
        return filename
#if __name__ == '__main__':
#        ParserObj = parser(sys.argv[1])
        
#        parserValues = ParserObj.openXML()
#        pp = pprint.PrettyPrinter(depth=6)    
#        pp.pprint(parserValues)

