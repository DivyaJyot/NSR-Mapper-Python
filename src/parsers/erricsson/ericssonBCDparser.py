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
_obj_name_='BearerCapabilitySet'
_start_word_="HLR PLMN BEARER CAPABILITY DATA"
_terminate_word_="END"
_root_dir_=config.project_path
_input_directory_= _root_dir_+'/log/ericsson/'+_obj_name_+'/'
## Input for CSV generation
keyField="ACCST"
fieldList=['BC', 'ADDNUM', 'ITC', 'RC', 'ACC', 'ACCST', 'ITN', 'BS'] 

class ErricssonBCSparser:
    
    
    def __init__(self, fileName):
        self.file= fileName
        self.logger1=loggingImpl.loggingImpl.getLogger()
        self.counterdict={}
        self.logger1.info("\n\t********------Mapping Object BearerCapabilitySet------********\n")
        
        
    def  parseAndGenerateInputMap(self,indexdict):
        '''Parse the input text file and create a dict'''
        f = open(self.file, 'r+')
        lines = f.readlines()
        datalist=[]
        hline= self.getHeaderLine(self.file);
        tline= self.getTerminatingLine(self.file)
        keys=re.split('\s+', lines[hline])
        self.logger1.info('keys--'+str(keys))
        try:
            for line in range(hline+1,tline):
                dataString= lines[line]
                if(len(dataString.strip())>0):
                    lineObj={}
                #lineArr= re.split('\s+', lines[line])
                    self.logger1.info(dataString)
                    for key in range(0,len(keys)):
                            val= keys[key]
                            if(val!=None and len(val)>0):
                                self.logger1.debug("processing--"+val)
                                d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', val)
                                startIndex=int(d.get('startIndex'))-1
                                lastIndex=int(d.get('endIndex'))
                                value= dataString[startIndex:lastIndex]
                                if(val=="BS"):
                                    value=dataString[startIndex:dataString.find(" ",startIndex)].strip()
                                    if( self.counterdict.get(value)!=None):
                                        self.logger1.debug(value+" found again ")
                                        self.counterdict[value]= self.counterdict.get(value)+1
                                        value=value+"_"+str(self.counterdict.get(value))
                                #validate(keys[key].strip(),val.strip())//compare with allowed values
                                    else:
                                        self.counterdict[value]= 0
                                        self.logger1.debug("Added "+value)
                                lineObj[keys[key].strip()]=value.strip()
                    datalist.append(lineObj)
        except(Exception):
                logging.exception("Error while parsing input dump, Check for the xml format")  
                raise
                
        return datalist
            
    def getHeaderLine(self,_input_dumpfile_):
        x=FileUtil.FileUtil.getLineNumWithWord(_input_dumpfile_, _start_word_,0)
        infile=open(self.file, 'r')
        lines = infile.readlines()
        header=FileUtil.FileUtil.getNextDataLine(lines, x)
        return header 

    def getTerminatingLine(self,_input_dumpfile_):
        x=FileUtil.FileUtil.getLineNumWithWord(_input_dumpfile_, _terminate_word_,0)
        return x

    def generateInputJson(self):
        try:
                    #Generate Index configuration file
            csvgen= CSVgenerator(self.file,_start_word_,keyField,fieldList)
            csvFile=_input_directory_+"bearer.csv"
            indexInfoList=csvgen.generateIndexDict(self.file, _start_word_, keyField)
            csvgen.writeDictToCSV(csvFile, indexInfoList)
            self.logger1.info("csv updated---"+csvFile)
            indexdict=indexInfoList
                    # parse input file and generate customerJson
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
#===============================================================================
# if __name__ == '__main__':
#     _input_dumpfile_="D:/userdata/djyoti/Desktop/2018/SDM/Code/svn/12-06-18/inputFiles/ericsson/ER_BCS.log"
#     _index_csv_ = config.project_path + '/log/ericsson/BearerCapabilitySet/bearer.csv'
#     textparser1 = ErricssonBCSparser(_input_dumpfile_,_index_csv_)
#     inputJson=textparser1.generateInputJson();
#     print(inputJson)
#     j = json.dumps(inputJson)
#     with open(_input_directory_+_obj_name_+".json", 'w') as f1:
#         json.dump(inputJson, f1, indent=4)
#       
#===============================================================================
