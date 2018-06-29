'''
Created on 16-Apr-2018

@author: djyoti
'''
import json
import logging
import re
from config import loggingImpl
from config import config
from utility import FileUtil
from utility import JSONUtil
from utility.ApplicationException import ApplicationError
from config.csvGenerator import CSVgenerator

_start_word_="HLR CAMEL SUBSCRIPTION PROFILE DATA"
_terminate_word_="END"
_obj_name_='TCsi'
_input_directory_= config.project_path+'/log/'+"ericsson/"+_obj_name_+'/'
_object_start_="CSP"
_object_end_="CAMEL SUBSCRIPTION OPTIONS"
fieldList=['TDPTYPE','TDP','SK','GSA','DEH','CCH','I','DIALNUM' ]
keyField='TDPTYPE'
class ErricssonTCsiparser:
    
    def __init__(self, fileName):
        self.file= fileName
        self.logger1=loggingImpl.loggingImpl.getLogger()
        self.logger1.info("\n\t********------Mapping Object TCsi------********\n")
 
    def  parseAndGenerateInputMap(self,indexdict):
        '''Parse the input text file and create a dict'''
        f = open(self.file, 'r+')
        lines = f.readlines()
        datalist=[]
        CSPDict={}
        topLine= FileUtil.FileUtil.getLineNumWithStatement(self.file, _start_word_,0)
        endLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _terminate_word_,topLine)
        
        
        hline=FileUtil.FileUtil.getLineNumWithWord(self.file, _object_start_,topLine)
        currLine= hline
        tline= FileUtil.FileUtil.getLineNumWithStatement(self.file, _object_end_,hline)
        
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "TDPTYPE")
        tdpTypeStartPos=int(d.get('startIndex'))-1
        tdpTypeLastPos=int(d.get('endIndex'))-1
        self.logger1.debug("hline--tline--topLine"+str(hline)+"=="+str(tline)+"=="+str(topLine))
        counter=1
        while(hline>0 and currLine<endLine and tline>1):
        
            self.logger1.debug("header line and terminating line --:"+str(hline)+"---"+str(tline))
            cspkey=lines[hline].strip()
            val=lines[hline+1].strip()
            CSPDict[cspkey]=val
            self.logger1.debug('csp cspkey--'+str(CSPDict))
            cspDataline=FileUtil.FileUtil.getNextDataLine(lines, hline)#hline+3
            keyline=FileUtil.FileUtil.getNextDataLine(lines, cspDataline)
            keys=re.split('\s+',lines[keyline])
            self.logger1.debug('keys--'+str(keys))
            try:
                for line in range(hline+1,tline):
                    dataString= lines[line]
                    currLine=line
                    tdptype= dataString[tdpTypeStartPos:tdpTypeLastPos].strip()
                    if(tdptype=="TCTDP"):
                        self.logger1.debug('csp tdptype--'+tdptype)
                        self.logger1.debug("processing  "+ dataString)
                        if(len(dataString.strip())>0):
                            lineObj={}
                            for key in range(0,len(keys)):
                                val=keys[key]
                                if(val!=None and len(val)>0):
                                    d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', val)
                                    startIndex=int(d.get('startIndex'))-1
                                    lastIndex=int(d.get('endIndex'))-1
                                    if(val=="TDPTYPE"):
                                        value="TCSI_"+CSPDict["CSP"]
                                        if(counter>0):
                                            value= value+"_"+str(counter)
                                    else:     
                                        value= dataString[startIndex:lastIndex]
                                    self.logger1.debug("key value is  "+ val + "   "+value)
                                    lineObj[val]=value.strip()
                            # Read SSLO After CAMEL SUBSCRIPTION OPTIONS
                            keyName="SSLO"
                            sSLOHeaderLine=  FileUtil.FileUtil.getLineNumWithWord(self.file, keyName,tline) 
                            ssloDataString=lines[sSLOHeaderLine]
                            ssloValString=lines[sSLOHeaderLine+1]
                            ssloVal=ssloValString[ssloDataString.find('SSLO')-1:ssloDataString.find('SSLO')+4].strip()
                            lineObj[keyName]=ssloVal
                            datalist.append(lineObj)
                            counter=counter+1        
                        else:
                            self.logger1.debug('csp tdptype--'+tdptype) 
            except(Exception):
                    logging.exception("Error while parsing input dump, Check for the xml format")  
                    raise
            hline=FileUtil.FileUtil.getLineNumWithWord(self.file, _object_start_,tline)
            counter=1
            tline=FileUtil.FileUtil.getLineNumWithWord(self.file, _object_end_,hline)
                
        return datalist    
     
    def generateInputJson(self):
        try:
                        #Generate Index configuration file
            csvgen= CSVgenerator(self.file,_start_word_,keyField,fieldList)
            csvFile=_input_directory_+"Tcsi.csv"
            indexInfoList=csvgen.generateIndexDict(self.file, _start_word_, keyField)
            indexInfoList2=csvgen.generateIndexDict(self.file, _start_word_, _object_start_)
            indexInfoList=indexInfoList2+indexInfoList
            csvgen.writeDictToCSV(csvFile, indexInfoList)
            self.logger1.info("csv updated---"+csvFile)
            indexdict=indexInfoList
            # End Dynamic Index Generation code
            inputJson=self.parseAndGenerateInputMap(indexdict);
            filename =_input_directory_+"ericsson_"+_obj_name_+".json"
            with open(filename, 'w') as f1:
                json.dump(inputJson, f1, indent=4)
            self.logger1.info("Json generated after parsing Input file ---"+str(inputJson))
        except(FileNotFoundError):
            self.logger1.error("Input file missing:-"+self.file)
            raise ApplicationError("Input file missing for object:- "+config.nokiaObjectName+" Add input files & retry")
        except(Exception):
            self.logger1.error("Error while parsing input dump, check for the correct format")
            raise
        return filename   
    
    
            
    def getHeaderLine(self,_input_dumpfile_):
        x=FileUtil.FileUtil.getLineNumWithWord(_input_dumpfile_, _start_word_,3)
        return x ### TODO

    def getTerminatingLine(self,_input_dumpfile_):
        x=FileUtil.FileUtil.getLineNumWithWord(_input_dumpfile_, _terminate_word_,4)
        return x
    
    
if __name__ == '__main__':
    file_name="D:/userdata/djyoti/Desktop/2018/SDM/Code/svn/TCsiLatest/tool/inputFiles/ericsson/TCsi_Dump.txt"
    TCsiparser= ErricssonTCsiparser(file_name)
    inputJson=TCsiparser.generateInputJson()
    print(inputJson)
    j = json.dumps(inputJson)
    with open(_input_directory_+_obj_name_+".json", 'w') as f1:
        json.dump(inputJson, f1, indent=4)
      
