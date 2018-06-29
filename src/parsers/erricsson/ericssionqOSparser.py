'''
Created on 26-Mar-2018

@author: djyoti
'''
# mypath should be the complete path for the directory containing the input text files
import json
import logging
import re

from config import config
from config import loggingImpl
from utility import FileUtil
from utility import JSONUtil
from utility.ApplicationException import ApplicationError
from config.csvGenerator import CSVgenerator


###Variables
_obj_name_='QualityOfServiceProfile'
_start_word_="HLR LA EXTENDED QUALITY OF SERVICE DATA"
_terminate_word_="END"
_root_dir_=config.project_path
_input_directory_= config.project_path+'/log/'+"ericsson/"+_obj_name_+'/'
keyField="EQOSID"
fieldList=['EQOSID', 'TC', 'ARP', 'DO', 'SDU', 'MBRU', 'MBRD', 'THP' , 'TD' , 'GBRU'] 


class ErricssonQOSparser:
    
    
    def __init__(self, fileName):
        self.file= fileName
        self.logger1=loggingImpl.loggingImpl.getLogger()
        self.counterdict={}
        self.logger1.info("\n\t********------Mapping Object QualityOfServiceProfile------********\n")
        
        
    def  parseAndGenerateInputMap(self,indexdict):
        '''Parse the input text file and create a dict'''
        f = open(self.file, 'r+')
        lines = f.readlines()
        datalist=[]
        hline= self.getHeaderLine(self.file);
        tline= self.getTerminatingLine(self.file)
        keys=re.split('\s+', lines[hline]) 
        keys[:] = filter(None, keys) 
         
        mline= self.getHeaderLine(self.file)+1;
        keys1 = re.split('\s+', lines[mline])    
        keys1[:] = filter(None, keys1) 
        keys[:] = keys+keys1
        
        self.logger1.info('keys--'+str(keys))
        for line in range(hline+2,tline):
            dataString= lines[line]
            dataStringLatest = lines[line+1]
            if(len(dataString.strip())>0):
                lineObj={}
                self.logger1.info(dataString)
                for key in range(0,len(keys)):
                        val= keys[key]
                        if(val!=None and len(val)>0):
                            self.logger1.info("processing--"+val)
                            if val != "GBRD" and val !="GBRU":
                                d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', val)                            
                                startIndex=int(d.get('startIndex'))-1
                                lastIndex=int(d.get('endIndex'))-1
                                if val == "SDU":
                                     val= dataString[startIndex:lastIndex]
                                     if(len(val.strip())>0):
                                         l = val.split("-")
                                         lineObj["SDU-desdu"] = l[0]
                                         lineObj["SDU-rber"] = l[2]
                                         lineObj["SDU-sduer"] = l[3]  
                                     else:
                                         lineObj["SDU-desdu"] = ""
                                         lineObj["SDU-rber"] = ""
                                         lineObj["SDU-sduer"] = ""  
                                          
                                                                       
                                else:    
                                    val= dataString[startIndex:lastIndex] 
                                    lineObj[keys[key].strip()]=val.strip() 
                                
                            elif val == "GBRU" and len(dataString.strip())>1 : 
                                d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', val)  
                                startIndex=int(d.get('startIndex'))-1
                                lastIndex=int(d.get('endIndex'))-1
                                val= dataString[startIndex:lastIndex]
                                lineObj[keys[key].strip()]=val.strip()
                                     
                            elif val == "GBRD" :
                                startIndex=int(d.get('startIndex'))-1
                                lastIndex=int(d.get('endIndex'))-1
                                if len(dataStringLatest.strip())==1 : 
                                    val= dataStringLatest[startIndex:lastIndex]
                                    lineObj[keys[key].strip()]=val.strip()
                                else : 
                                    lineObj[keys[key].strip()]=""  
                         
            if (all(x=="" for x in lineObj.values()) == False):                                             
                datalist.append(lineObj)            
        return datalist
            
    def getHeaderLine(self,_input_dumpfile_):
        x=FileUtil.FileUtil.getLineNumWithWord(_input_dumpfile_, _start_word_,0)
        return x+2 ### TODO

    def getTerminatingLine(self,_input_dumpfile_):
        x=FileUtil.FileUtil.getLineNumWithWord(_input_dumpfile_, _terminate_word_,3)
        return x

    def generateInputJson(self):
        try:
            #Generate CSV File
            csvgen= CSVgenerator(self.file,_start_word_,keyField,fieldList)
            csvFile=_input_directory_+"qos.csv"
            indexInfoList=csvgen.generateIndexDict(self.file, _start_word_, keyField)
            csvgen.writeDictToCSV(csvFile, indexInfoList)
            self.logger1.info("csv updated---"+csvFile)
            indexdict=indexInfoList
            
            inputJson=self.parseAndGenerateInputMap(indexdict);
            filename =_input_directory_+"ericsson_"+_obj_name_+".json"
            with open(filename, 'w') as f1:
                json.dump(inputJson, f1, indent=4)
            self.logger1.info("Json generated after parsing Input file ---"+str(inputJson))
        except(FileNotFoundError):
            self.logger1.error("Input file missing:-"+self.file)
            raise
        except(Exception):
            self.logger1.error("Error while parsing input dump, check for the correct format")
            raise
        return filename
