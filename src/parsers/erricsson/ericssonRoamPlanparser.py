'''
Created on 26-Mar-2018

@author: vivek
'''
# mypath should be the complete path for the directory containing the input text files

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


###Variables
_obj_name_='RoamPlan'
_start_word_="<HGRAP;"
wordforidentified = "RSA"
_terminate_word_="END"
_obj_name_Ref_SS = 'SS_Reference_File'
_obj_name_Ref_ODB = 'ODB_Reference_File'
_input_directory_= config.project_path+'/log/'+"ericsson/"+_obj_name_+'/'
counter = 1
keyField="RSP"
fieldList=['RAID', 'RSP' , 'SRR' , 'RSIP']
_start_word_Dynamic_G_="HLR ROAMING SERVICE AREA DATA"

class EricssonROAMPlanparser:
    
    
    def __init__(self, fileName):
        self.file= fileName
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Mapping Object Roam Plan------********\n")   
        
        
        
    def findARDExistenceorNot(self):
        f = open(self.file, 'r+')
        lines = f.readlines()
        dataList=[]
        demoList = ['ARD-1','ARD-2']
        _RPP_start_word_="<HGRPP;"
        RPPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _RPP_start_word_,0)
        endline=FileUtil.FileUtil.getLineNumWithStatement(self.file,_terminate_word_,RPPStartLine)
        hLine=RPPStartLine+2
        while (hLine>0 and hLine<endline):
            temp_dict={}
            start=self.getRSPorRSIPNextLine(lines,hLine,endline)
            end=self.getRSPorRSIPNextLine(lines,start+1,endline)
            if(end==-1):
                end=endline
            SUDline=FileUtil.FileUtil.getLineNumWithStatementBetweenLines(self.file, "SUD",start,end)
            if(start>0 and SUDline>0 and end>0):
                var1 = self.getSUDdata(lines, SUDline, end)
                if(var1 ==['ARD-1'] or var1 ==['ARD-2']):
                    #temp_dict["SUDVAL"] = var1
                    temp_dict["SUDVAL"] = ",".join(str(item) for item in var1[:] )
                    temp_dict['treatment']=lines[start].strip()
                    temp_dict['treatment_val'] = lines[start+1].strip()
                    dataList.append(temp_dict)  
                    hLine = end  
                else:
                    hLine = end
                    
            hLine=end
        return dataList    
    
    
    def getRSPorRSIPNextLine(self,lines,hLine,endline):
        for i in range(hLine,endline):
            if(lines[i].strip()=="RSP" or lines[i].strip()=="RSIP"):
                return i
        return -1
        
    def getSUDdata(self,lines,SUDline,end):
        currLine=SUDline+1
        sudList=[]
        #end=FileUtil.FileUtil.getLineNumWithStatementBetweenLines(self.file,_terminate_word_,currLine,end)
        while (currLine<end):
            dataString= lines[currLine].strip()
            if(len(dataString)>0):
                sudList.append(dataString)
            currLine= currLine+1
                  
        return sudList    
            
    def  fetchUniqueCombination(self , indexdict):
        '''Parse the input text file and create a dict'''
        f = open(self.file, 'r+')
        lines = f.readlines()
        datalist=[]
        
        RPPStartLine=self.getLineNumWithStatement(self.file, _start_word_,0)
        tline=self.getLineNumWithStatement(self.file,_terminate_word_,RPPStartLine)
        
        for line in range (RPPStartLine ,tline):        
            hline=self.getRSAline(self.file, wordforidentified, RPPStartLine, tline)
            eline = self.getRSAline(self.file, wordforidentified, hline+1, tline)
            RPPStartLine = eline
            keys=re.split('\s+', lines[hline]) 
            keys[:] = filter(None, keys) 
            mline = hline + 3
            keys1 = re.split('\s+', lines[mline])    
            keys1[:] = filter(None, keys1) 
            keys[:] = keys+keys1        
            self.logger.info('keys--'+str(keys))
            if(eline==-1):
                eline=tline
            temp_val = ""   
            for line in range(hline+1,eline):
                dataString= lines[line]
                if (lines[line-1].strip()=="RSA"):
                    dataStringLatest = lines[line+3]
                else:
                    dataStringLatest = lines[line+1]
                        
                    
                if (dataString.strip().replace(" ", "")!="RAIDRSPSRRRSIP" and len(dataString.strip())>0 and len(dataStringLatest.strip())>0):                
                    #dataStringLatest = lines[line+3]
                    if(len(dataString.strip())>0):
                        lineObj={}
                        temp={}
                        self.logger.info(dataString)
                        for key in range(0,len(keys)):
                                val= keys[key]
                                if(val!=None and len(val)>0):
                                    self.logger.info("processing--"+val)
                                    if val == "RSA":
                                            d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', val)                            
                                            startIndex=0
                                            lastIndex=5
                                            if (lines[line-1].strip()=="RSA"):
                                                temp_val= dataString[0:5]                                
                                            #validate(keys[key].strip(),val.strip())//compare with allowed values
                                            lineObj[keys[key].strip()]=temp_val.strip()   
                                            
                                    elif val != "RSA" and len(dataStringLatest.strip())>1 : 
                                            d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', val)  
                                            startIndex=int(d.get('startIndex'))-1
                                            lastIndex=int(d.get('endIndex'))
                                            val= dataStringLatest[startIndex:lastIndex]
                                            lineObj[keys[key].strip()]=val.strip() 
                                            
                                            
                        #temp['RSA'] =lineObj.get('RSA')                   
                        temp['RSP'] = lineObj.get('RSP') 
                        temp['SRR'] = lineObj.get('SRR')  
                        temp['RSIP'] = lineObj.get('RSIP')                     
                                 
                    if (all(x=="" for x in lineObj.values()) == False):                                             
                        #datalist.append(lineObj) 
                        if(temp not in datalist): 
                            datalist.append(temp)                    
        return datalist
    
    
    def trimDictValues(self , dict):
        dictList = []
        for k,v in dict.items():
            dictList.append(v)
        return dictList
    
    
    def parseAndGenerateInputMap(self,indexdict):
        global counter
        fullList = []
        ardList = []
        uniqueCombList=self.fetchUniqueCombination(indexdict)
        SSPlanReference_FilePath = _input_directory_+"ericsson_"+_obj_name_Ref_SS+".json"
        ODBPlanReference_FilePath = _input_directory_+"ericsson_"+_obj_name_Ref_ODB+".json"
        
        try:
        
            with open(SSPlanReference_FilePath) as f:
                data_SSPlan = json.load(f)
                #print(data_SSPlan)
            
            with open(ODBPlanReference_FilePath) as f:
                data_ODBPlan = json.load(f)
                #print(data_ODBPlan)    
                
        except(FileNotFoundError):
            self.logger.error("Missing Execution of SSPlan or ODBPlan")
            logging.exception(FileNotFoundError)
            raise ApplicationError("SSPlan and ODBPlan should be executed compulsory before execution of RoamPlan")
                
            
        ardList = self.findARDExistenceorNot()            
        for item in uniqueCombList:
            uniqueCombValues = []
            for k,v in item.items():
                new_dict = {}                
                val1 = self.getJsonObjectWithVal(data_SSPlan, 'treatment', k, 'treatment_Value', v)
                val2 = self.getJsonObjectWithVal(data_ODBPlan, 'treatment', k, 'treatment_Value', v)
                val3 = self.getARDSETValue(ardList, 'treatment', k, 'treatment_val', v)
                if (val3 !=[] and k=='RSP'):
                    new_dict['ARD'] = ",".join(str(item) for item in val3[:] )
                    new_dict['ADD_Treatment'] = 'RSP'
                elif (val3 !=[] and k=='RSIP'):
                    new_dict['ARD'] = ",".join(str(item) for item in val3[:] )
                    new_dict['ADD_Treatment'] = 'RSIP'
                else:
                    new_dict['ARD'] = ""
                    new_dict['ADD_Treatment'] = ""    
                if (val1 !=[] or val2 !=[]):
                    if (val1 !=[]):
                        new_dict['ref_ssPlanName'] = ",".join(str(item) for item in val1[:] )
                    else:
                        new_dict['ref_ssPlanName'] = ""
                    if (val2 !=[]):
                        new_dict['ref_odbPlanName'] = ",".join(str(item) for item in val2[:] )
                    else:
                        new_dict['ref_odbPlanName'] = ""   
                        
                else:
                    new_dict['ref_ssPlanName'] = ""
                    new_dict['ref_odbPlanName'] = ""
                     
                if (val1 !=[] or val2 !=[] or val3 !=[]):
                    listdict = []
                    new_dict['identifier'] = "RoamPlan_"+ str(counter)
                    listdict = self.trimDictValues(item)
                    new_dict['Unique_Comb_Info'] = ",".join(str(item) for item in listdict[:] )
                    #counter+=1  
                    uniqueCombValues.append(new_dict)
                                        
                if (all(x=="" for x in new_dict.values()) == False):                
                    fullList.append(new_dict) 
            if(uniqueCombValues !=[]):
                counter+=1
                    
        
        return fullList
        
    def getRSAline(self,inputFilePath,word,startIndex,endIndex):
        infile=open(inputFilePath, 'r')
        lines = infile.readlines()
        for i in range(startIndex,endIndex):
            if(word.strip()==lines[i].strip()):
                return i
        return -1
    
    def getJsonObjectWithVal(self ,inputlist,key1,val1,key2,val2):
        listTemp = []
        for obj in inputlist:
            if (obj[key1] == val1 and obj[key2] == val2):
                s = obj.get('identifier')
                listTemp.append(s)
        return listTemp
    
    
    def getARDSETValue(self ,inputlist,key1,val1,key2,val2):
        listTemp = []
        for obj in inputlist:
            if (obj[key1] == val1 and obj[key2] == val2):
                s = obj.get('SUDVAL')
                listTemp.append(s)
        return listTemp
        
    
    def getLineNumWithStatement(self , inputFilePath,word,startIndex):   
        '''
        return index of line(0 for line1)
        :param inputFilePath: file in which word as to be searched
        :param word: word to be searched
        :param startIndex:
        '''
        infile=open(inputFilePath, 'r')
        lines = infile.readlines()
        for i in range(startIndex,len(lines)):
            if(word.strip()==lines[i].strip()):
                return i
        return -1
          
          
          
    def generateInputJson(self):
        try:
            # Start Dynamic Generation code 
            csvgen= CSVgenerator(self.file,_start_word_Dynamic_G_,keyField,fieldList)
            csvFile=_input_directory_+"RoamPlan.csv"
            indexInfoList=csvgen.generateIndexDict(self.file, _start_word_Dynamic_G_, keyField)
            csvgen.writeDictToCSV(csvFile, indexInfoList)
            self.logger.info("csv updated---"+csvFile)
            indexdict=indexInfoList
            #End of Dynamic Generation COde 
            
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
