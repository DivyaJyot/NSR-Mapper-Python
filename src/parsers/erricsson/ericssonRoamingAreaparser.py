'''
Created on 01-May-2018

@author: djyoti
'''

import json
import logging
from config import config
from config import loggingImpl
from utility import FileUtil
from utility import JSONUtil
from utility.ApplicationException import ApplicationError
from config.csvGenerator import CSVgenerator


_NSP_start_word_="<HGNSP;"
_RAP_start_word_="<HGRAP;"
_terminate_word_="END"
_obj_name_='RoamingArea'
_object_start_="RSA"
_input_directory_= config.project_path+'/log/'+"ericsson/"+_obj_name_+'/'
_PAP_start_word_="<HGPAP:USRF=ALL;"
_start_word_1_="HLR NUMBER SERIES PRE-ANALYSIS DATA"
_start_word_2_="HLR ROAMING SERVICE AREA DATA"
_start_word_3_="HLR NUMBER SERIES ANALYSIS DATA"
keyField_1="USRF"
keyField_2_a_="RSA"
keyField_2_b_="RAID"
keyField_3="ONSA"
fieldList=['RAID', 'RSP' , 'SRR' , 'RSIP']


class EricssonRoamingAreaparser:

    def __init__(self, fileName):
        self.file= fileName
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Mapping Object Roaming Area------********\n")   
  
    def parseAndGenerateInputMap(self,indexdict):
        f = open(self.file, 'r+')
        lines = f.readlines( )
        raplist=self.generateRAPDict(lines,indexdict)
        onsa=self.getRAIDONSA(lines, indexdict)
        nsplist=self.getNSPdict(lines, indexdict, onsa)
        resultset=[]
        for item in raplist:
            valList=raplist[item]
            for val in valList:
                if("RAID-"+val in nsplist):
                    for entry in nsplist["RAID-"+val]:
                        nokiaObj={}
                        nokiaObj["identifier"]=item.strip()
                        nokiaObj["isAllowed"]="true"
                        nokiaObj["isdnNumber"]=  entry.strip()
                        resultset.append(nokiaObj)
        self.logger.info("Roam Area data--\n:"+str(resultset))
        return resultset
    def generateRAPDict(self,lines,indexdict):
        RAPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _RAP_start_word_,0)
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "RAP_RSA")
        RSAStartPos=int(d.get('startIndex'))-1
        RSALastPos=int(d.get('endIndex'))
        d1= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "RAP_RAID")
        RAIDStartPos=int(d1.get('startIndex'))-1
        RAIDLastPos=int(d1.get('endIndex'))
        hline=FileUtil.FileUtil.getLineNumWithWord(self.file, _object_start_,RAPStartLine)
        endline=FileUtil.FileUtil.getLineNumWithStatement(self.file,_terminate_word_,RAPStartLine)
        currLine= hline
        rap_dict={}
        while(hline>0 and hline<endline):
            self.logger.debug("At line "+lines[hline])
            RSA=lines[hline+1][RSAStartPos:RSALastPos]
            identifier= "RSA_"+str(RSA).strip()
            #rap_dict["identifier"]=identifier
            currLine=currLine+1
            tline=FileUtil.FileUtil.getLineNumWithWord(self.file, _object_start_,currLine)
            datalist=[]
            for row in range(currLine+1,tline-1):
                dataString=lines[row]
                currLine=currLine+1
                if(len(str(dataString).strip())>0 and "RAID" not in dataString):
                    RAID=dataString[RAIDStartPos:RAIDLastPos].strip()
                    datalist.append(RAID)
            
            rap_dict[identifier]=datalist
            hline=tline
        JSONUtil.JSONUtil.writeDictInJsonFile(rap_dict,_input_directory_+"RAP.json")
        return rap_dict
    
    
    def getNSPdict(self,lines,indexdict,raid_onsa):
        NSPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _NSP_start_word_,0)
        NSPEndLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _terminate_word_,NSPStartLine)
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGNSP_ONSA")
        ONSAStartPos=int(d.get('startIndex'))-1
        ONSALastPos=int(d.get('endIndex'))
        d1= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGNSP_CHAR")
        CHARStartPos=int(d1.get('startIndex'))-1
        CHARLastPos=int(d1.get('endIndex'))
        d2= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGNSP_NS")
        NSStartPos=int(d2.get('startIndex'))-1
        NSLastPos=int(d2.get('endIndex'))
        nspdict={}
        currLine= NSPStartLine+2
        try:
                while(currLine>NSPStartLine and currLine<NSPEndLine):
                    currLine=currLine+1
                    dataString= lines[currLine]
                    if(len(dataString.strip())>0):
                        ONSA=dataString[ONSAStartPos:ONSALastPos].strip()
                        if(ONSA ==raid_onsa):
                            self.logger.debug("fetching data for ONSA=="+str(ONSA))
                            for line in range(currLine,NSPEndLine):
                                dataString= lines[line]
                                NS=dataString[NSStartPos:NSLastPos]
                                CHAR=dataString[CHARStartPos:CHARLastPos].strip()
                                if(CHAR in nspdict):
                                    datalist=nspdict[CHAR]
                                else:
                                    datalist=[]
                                datalist.append(NS)
                                nspdict[CHAR]=datalist
                self.logger.debug("nsplist--\n\n\t"+str(nspdict))
        except(Exception):
            logging.exception(Exception)
            raise
        JSONUtil.JSONUtil.writeDictInJsonFile(nspdict,_input_directory_+"NSP.json")
        return nspdict
 
    def getRAIDONSA(self,lines,indexdict):
        PAPStartLine= FileUtil.FileUtil.getLineNumWithStatement(self.file, _PAP_start_word_,0)
        PAPEndLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _terminate_word_,PAPStartLine)
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "USRF")
        USRFStartPos=int(d.get('startIndex'))-1
        USRFLastPos=int(d.get('endIndex'))
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "ONSA")
        ONSAStartPos=int(d.get('startIndex'))-1
        ONSALastPos=int(d.get('endIndex'))
        try:
            for line in range(PAPStartLine+1,PAPEndLine):
                dataString= lines[line]
                if(len(dataString.strip())>0):
                    USRF= dataString[USRFStartPos:USRFLastPos].strip()
                    #if(USRF=="USSDSC" or USRF=="ENAP3SC" or USRF=="ENAP2SC" or USRF=="USSDSTR") :  ## TODO
                    if(USRF=="RAID") :
                        ONSA=dataString[ONSAStartPos:ONSALastPos].strip()
                        self.logger.debug("RAID ONSA="  + str(ONSA))
                        return ONSA
            return -1
        except(Exception):
            raise        
        
        
    def generateInputJson(self):
        try:
            #Generate Index Configuration File 
            csvgen= CSVgenerator(self.file,_start_word_1_,keyField_1,fieldList)
            csvFile=_input_directory_+"RoamingArea.csv"
            indexInfoList_1=csvgen.generateIndexDict(self.file, _start_word_1_, keyField_1)
            indexInfoList_2_a=csvgen.generateIndexDict(self.file, _start_word_2_, keyField_2_a_)
            indexInfoList_2_b=csvgen.generateIndexDict(self.file, _start_word_2_, keyField_2_b_)
            indexInfoList_2=indexInfoList_2_a+indexInfoList_2_b
            csvgen.addPrefixTokey(indexInfoList_2,'RAP') 
            indexInfoList_3=csvgen.generateIndexDict(self.file, _start_word_3_, keyField_3)
            csvgen.addPrefixTokey(indexInfoList_3 , 'HGNSP')
            indexInfoList = indexInfoList_1+indexInfoList_2+indexInfoList_3            
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
    
if __name__ == '__main__':
    _index_csv=config.src_path+"/config/RoamingArea.csv"
    _input_dumpfile_=config.project_path+"/inputFiles/ericsson/HLR1 DUMP_16JUN17.log"
    indexdict=FileUtil.FileUtil.dumpCsvIndict(_index_csv,_input_directory_+_obj_name_+"_index.json")
    textparser1 = EricssonRoamingAreaparser(_input_dumpfile_,_index_csv)
    inputJson=textparser1.generateInputJson();
    print("done")