'''
Created on 14-May-2018

@author: vivek
'''
import json
import os
import re
import logging
from config import config
from config import loggingImpl
from utility import FileUtil
from utility import JSONUtil
from utility.ApplicationException import ApplicationError
from numpy.distutils.fcompiler import none
from config.csvGenerator import CSVgenerator

_RPP_start_word_="<HGRPP;"
_terminate_word_="END"
_obj_name_='SSPlan'
_obj_name_Ref_='RoamPlan'
_obj_name_Ref_Copy="SS_Reference_File"
_object_start_="RSA"
counter = 0  
_input_directory_= config.project_path+'/log/'+"ericsson/"+_obj_name_+'/'
_input_directory_Ref_= config.project_path+'/log/'+"ericsson/"+_obj_name_Ref_+'/'
keyField="BSG"
fieldList=['SUD', 'BSG']
_start_word_="HLR ROAMING SERVICE PROFILE DATA"



class EricssonSSPlanparser:
    
    def __init__(self, fileName):
        self.file= fileName
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Mapping Object ODB Plan------********\n")   
      
    def  parseAndGenerateInputMap(self,indexdict):
        '''Parse the input text file and create a dict'''
        global counter 
        datalist=[]
        demoList=[]
        tempList=[]
        f = open(self.file, 'r+')
        lines = f.readlines()        
        RPPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _RPP_start_word_,0)
        endline=FileUtil.FileUtil.getLineNumWithStatement(self.file,_terminate_word_,RPPStartLine)
        hLine=RPPStartLine+2
        
        while (hLine>0 and hLine<endline):
            start=self.getRSPorRSIPNextLine(lines,hLine,endline)
            end=self.getRSPorRSIPNextLine(lines,start+1,endline)
            if(end==-1):
                end=endline
            #SUDline=FileUtil.FileUtil.getLineNumWithMultipleStatementBetweenLines(self.file, "SUD",start,end)
            SUDline=self.getLineNumWithMultipleStatementBetweenLines(self.file, "SUD",start,end)
            if(start>0 and SUDline>0 and end>0):
                ValueofRSPorRSIP = self.getValueRSIPorRSP(self.file, start+1, end)
                keys=re.split('\s+', lines[SUDline])
                keys[:] = filter(None, keys) 
                
                try:
                    SUDval=""
                    treatment=""
                    for line in range(SUDline+1,end):
                        dataString= lines[line]
                        if(len(dataString.strip())>0):
                            self.logger.info(dataString)
                            lineObj={}
                            lineObj1 = {}
                            for key in range(0,len(keys)):
                                    val= keys[key]
                                    if(val=="SUD"):
                                        self.logger.debug("processing--"+val)
                                        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', val)
                                        startIndex=int(d.get('startIndex'))-1
                                        lastIndex=int(d.get('endIndex'))
                                        value= dataString[startIndex:lastIndex]
                                        if (len(value.strip())>0):
                                            SUDval=value.strip() 
                                            treatment=lines[start].strip()   
                                            counter+=1
                                        #lineObj[keys[key].strip()]=SUDval
                                      
                                        
                                    elif (val=="BSG"):
                                        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', val)
                                        startIndex=int(d.get('startIndex'))-1
                                        lastIndex=int(d.get('endIndex'))
                                        value= dataString[startIndex:lastIndex]
                                        lineObj['treatment']=treatment
                                        lineObj["SUD"]= SUDval
                                        lineObj["identifier"] = "SSPlan_"+ str(counter) 
                                        lineObj1['treatment']=treatment
                                        lineObj1['treatment_Value'] = ValueofRSPorRSIP
                                        lineObj1["identifier"] = "SSPlan_"+ str(counter) 
                                        lineObj[keys[key].strip()]=value.strip() 
                                          
                                                                                
                            datalist.append(lineObj)
                            tempList.append(lineObj1)
                        demoList = datalist
                except(Exception):
                        logging.exception("Error while parsing input dump, Check for the xml format")  
                        raise
            hLine=end 
            
            if (tempList != []):
                tempList = list({v['identifier']:v for v in tempList}.values())
                if not os.path.exists(_input_directory_Ref_):
                    os.makedirs(_input_directory_Ref_)
                SSReference_File =_input_directory_Ref_+"ericsson_"+_obj_name_Ref_Copy+".json"
                with open(SSReference_File, 'w') as fout:
                    json.dump(tempList, fout)    
                       
        return demoList               
              
    def getRSPorRSIPNextLine(self,lines,hLine,endline):
        for i in range(hLine,endline):
            if(lines[i].strip()=="RSP" or lines[i].strip()=="RSIP"):
                return i
        return -1
        
           
    def generateInputJson(self):
        try:
            #Generate Index Configuration File 
            csvgen= CSVgenerator(self.file,_start_word_,keyField,fieldList)
            csvFile=_input_directory_+"SSPlan.csv"
            indexInfoList=csvgen.generateIndexDict(self.file, _start_word_, keyField)
            csvgen.writeDictToCSV(csvFile, indexInfoList)
            self.logger.info("csv updated---"+csvFile)
            indexdict=indexInfoList
            # End Dynamic Generation Code
            inputJson=self.parseAndGenerateInputMap(indexdict);
            filename =_input_directory_+"ericsson_"+_obj_name_+".json"
            with open(filename, 'w') as f1:
                json.dump(inputJson, f1, indent=4)
            self.logger.info("Json generated after parsing Input file ---"+str(inputJson))
        except(FileNotFoundError):
            self.logger.error("Input file missing:-")
            logging.exception(FileNotFoundError)
            raise ApplicationError("Input file missing for object:- "+config.nokiaObjectName+" Add input files & retry")
        except(Exception):
            self.logger.error("Error while parsing input dump, check for the correct format")
            raise
        return filename 
    
    
    def getLineNumWithMultipleStatementBetweenLines(self ,inputFilePath,word,startIndex,endIndex): 
        
        infile=open(inputFilePath, 'r')
        lines = infile.readlines()
        for i in range(startIndex,endIndex):
            if(lines[i].strip().replace(" ", "")=="SUDBSG"):
                return i            
        return -1    
    
    
    
    def getValueRSIPorRSP(self ,inputFilePath,startIndex,endIndex): 
        
        infile=open(inputFilePath, 'r')
        lines = infile.readlines()
        for i in range(startIndex,endIndex):
            if(lines[i].strip()!=None):
                return lines[i].strip()            
        return -1    
    
