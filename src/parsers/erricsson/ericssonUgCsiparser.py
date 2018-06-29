'''
Created on 25-Apr-2018

@author: djyoti
'''
import json
import logging
import re
from config import config
from config import loggingImpl
from utility import FileUtil
from utility import JSONUtil
from utility.ApplicationException import ApplicationError
from builtins import str
from config.csvGenerator import CSVgenerator



_PAP_start_word_="<HGPAP:USRF=ALL;"
_NSP_start_word_="<HGNSP;"
_XAP_start_word_="<HGXAP:ENAP=ALL; "
_terminate_word_="END"
_obj_name_='UgCsi'
_input_directory_= config.project_path+'/log/'+"ericsson/"+_obj_name_+'/'
fieldList=['USRF','ONSA','HGNSP_ONSA','HGNSP_CHAR','HGNSP_NS','HGXAP_ENAP','HGXAP_EADD']
keyField='ONSA'

class ErricssonUgCsiparser:
    def __init__(self, fileName):
        self.file= fileName
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Mapping Object UgCsi------********\n")
        ## enapList contains all ENAP3SC & ENAP2SC Objects
        self.enapList=[]
    
    def parseAndGenerateInputMap(self,indexdict):
        f = open(self.file, 'r+')
        lines = f.readlines( )  
        
        ##Identify Objects PAP,NSP & XAP
        papdict=self.generatePAPDict(lines,indexdict)
        nsplist=self.generateNSPDict(lines,indexdict,papdict)
        
        xapdict=self.generateXAPDict(lines,indexdict,nsplist)
        dataList=[]
        for item in nsplist:
            nokiaObj={}
            identifier=item["NS"]
            ENAPID= self.getENAPIDforIdentifier(identifier,nsplist)
            GT=self.getGTforIdentifier(ENAPID,xapdict)
            if(item["CHAR"].startswith("USSDSTR")):
                if identifier[0]== "*":
                    self.logger.info("removing---"+ identifier[0])
                    start=1
                else:
                    start=0
                if(identifier[len(identifier)-1]=="#"):
                    end=len(identifier)-1
                    self.logger.info("removing---"+ identifier[len(identifier)-1])
                else:
                    end=  len(identifier)  
                identifier=identifier[start:end]
            nokiaObj["identifier"]=int(identifier)
            nokiaObj["gsmServiceControlFunctionAddress"]=GT
            dataList.append(nokiaObj)
        self.logger.info("Output Json---"+ str(dataList))    
        return dataList


    def getENAPIDforIdentifier(self,identifier,nsplist):
        for item in nsplist:
            if(item["NS"]==str(identifier)):
                char=item["CHAR"]
                type=re.split('-',char)[0]
                enapid=re.split('-',char)[1]
                if(type.startswith("USSDSTR") or len(enapid)==4):
                    ENAPNS= enapid
                    enapid=self.getENAPIDforIdentifier(ENAPNS,self.enapList)
                elif type.startswith("USSDSC"):
                    
                    enapid=re.split('-',char)[1]
                return enapid
    def getGTforIdentifier(self,enapid,xapdict):
        for item in xapdict:
            if(item==enapid):
                eAdd=xapdict[item]
                gt=enapid=re.split('-',eAdd)[1]
                return gt
        return ""
    def generatePAPDict(self,lines,indexdict):
        PAPStartLine= FileUtil.FileUtil.getLineNumWithStatement(self.file, _PAP_start_word_,0)
        PAPEndLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _terminate_word_,PAPStartLine)
        lineObj={}
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
                    #lineObj={}
                    USRF= dataString[USRFStartPos:USRFLastPos].strip()
                    #if(USRF=="USSDSC" or USRF=="ENAP3SC" or USRF=="ENAP2SC" or USRF=="USSDSTR") :  ## TODO
                    if(USRF=="ENAP3SC" or USRF=="ENAP2SC" or USRF=="USSDSTR") :
                        ONSA=dataString[ONSAStartPos:ONSALastPos].strip()
                        lineObj[USRF]=ONSA
                    #datalist.append(lineObj)
            self.logger.debug("PAP Dict"  + str(lineObj))
            return lineObj
        except(Exception):
            raise
    def generateNSPDict(self,lines,indexdict,papdict):
        NSPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _NSP_start_word_,0)
        NSPEndLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _terminate_word_,NSPStartLine)
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGNSP_ONSA")
        ONSAStartPos=int(d.get('startIndex'))-1
        ONSALastPos=int(d.get('endIndex'))

        nsplist=[]
        currLine= NSPStartLine+2
        try:
                while(currLine>NSPStartLine and currLine<NSPEndLine):
                    dataString= lines[currLine]
                    if(len(dataString.strip())>0):
                        ONSA=dataString[ONSAStartPos:ONSALastPos].strip()
                        if(ONSA in iter(papdict.values())):
                            self.logger.debug("fetching data for ONSA=="+str(ONSA))
                            datalist,x=self.getdataListforONSA(lines,currLine,NSPEndLine,indexdict)
                            if(datalist ==None or len(datalist)>0 ):
                                nsplist=nsplist+datalist
                                self.logger.debug("fetched data for ONSA=="+str(datalist))
                            currLine=x
                        else:
                            currLine=currLine+1
                    else:
                        currLine=currLine+1
                self.logger.debug("nsplist--\n\n\t"+str(nsplist))
        except(Exception):
            logging.exception(Exception)
            raise
        return nsplist
    def getdataListforONSA(self,lines,currLine,EndLine,indexdict):
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGNSP_ONSA")
        ONSAStartPos=int(d.get('startIndex'))-1
        ONSALastPos=int(d.get('endIndex'))
        ONSA=lines[currLine][ONSAStartPos:ONSALastPos].strip()
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGNSP_CHAR")
        CHARStartPos=int(d.get('startIndex'))-1
        CHARLastPos=int(d.get('endIndex'))
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGNSP_NS")
        NSStartPos=int(d.get('startIndex'))-1
        NSLastPos=int(d.get('endIndex'))
        datalist=[]
        lineObj={}
        lineObj["ONSA"]=ONSA
        CHAR=lines[currLine][CHARStartPos:CHARLastPos].strip()
        lineObj["CHAR"]=CHAR
        lineObj["NS"]=lines[currLine][NSStartPos:NSLastPos].strip()
        if CHAR.startswith("ENAP"):
            self.enapList.append(lineObj)
        if(len(lines[currLine][NSStartPos:NSLastPos].strip())<=3) or CHAR.startswith("USSDSTR") :
            datalist.append(lineObj)
        for line in range(currLine+1,EndLine):
            currLine=currLine+1
            dataString= lines[line]
            if((dataString is not None) and len(dataString)>0 and len(dataString[ONSAStartPos:ONSALastPos].strip())==0): 
                lineObj={}
                lineObj["ONSA"]=ONSA
                CHAR=dataString[CHARStartPos:CHARLastPos].strip()
                lineObj["CHAR"]=CHAR
                lineObj["NS"]=dataString[NSStartPos:NSLastPos].strip()
                if(len(dataString[NSStartPos:NSLastPos].strip())<=3 or "USSDSTR"in CHAR):
                    datalist.append(lineObj)
                if CHAR.startswith("ENAP"):
                    self.enapList.append(lineObj)   
                    
            else:
                return datalist,line   
        return datalist,line 
    
    def generateXAPDict(self,lines,indexdict,nspdict):
        XAPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _XAP_start_word_,0)
        XAPEndLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _terminate_word_,XAPStartLine)
        d1= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGXAP_ENAP")
        ENAPStartPos=int(d1.get('startIndex'))-1
        ENAPLastPos=int(d1.get('endIndex'))
        d2= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "HGXAP_EADD")
        EADDStartPos=int(d2.get('startIndex'))-1
        EADDLastPos=int(d2.get('endIndex'))
        lineObj={}
        try:
            for line in range(XAPStartLine+4,XAPEndLine):
                dataString= lines[line]
                if(len(dataString.strip())>0):
                    ENAPID=dataString[ENAPStartPos:ENAPLastPos].strip()
                    lineObj[ENAPID]=dataString[EADDStartPos:EADDLastPos].strip()
            self.logger.debug("XAP Dict\n"  + str(lineObj))
            JSONUtil.JSONUtil.writeDictInJsonFile(lineObj,_input_directory_+"XAP.json")
            return lineObj
        except(Exception):
            raise
        
    def generateInputJson(self):
        try:
                        #Generate Index configuration file
            csvgen= CSVgenerator(self.file,_PAP_start_word_,keyField,fieldList)
            csvFile=_input_directory_+"UgCsi.csv"
            indexInfoList=csvgen.generateIndexDict(self.file, _PAP_start_word_, keyField)
            indexInfoList2=csvgen.generateIndexDict(self.file, _NSP_start_word_, keyField)
            csvgen.addPrefixTokey(indexInfoList2,"HGNSP")
            indexInfoList3=csvgen.generateIndexDict(self.file, _XAP_start_word_, "EADD")
            csvgen.addPrefixTokey(indexInfoList3,"HGXAP")
            indexInfoList=indexInfoList+indexInfoList2+indexInfoList3
            csvgen.writeDictToCSV(csvFile, indexInfoList)
            indexdict=indexInfoList
            # End Dynamic Index Generation code
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
    #_index_csv_=config.project_path + '/log/ericsson/UgCsi/UgCsi.csv'
    _input_dumpfile_=config.project_path+"/inputFiles/ericsson/HLR1 DUMP_16JUN17.log"
    textparser1 = ErricssonUgCsiparser(_input_dumpfile_)
    inputJson=textparser1.generateInputJson();
    print("done")

      
