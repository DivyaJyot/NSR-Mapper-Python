'''
Created on 14-May-2018

@author: djyoti
'''
import json
import logging
import os
from config import config
from config import loggingImpl
from utility import FileUtil
from utility import JSONUtil
from utility.ApplicationException import ApplicationError
from config.csvGenerator import CSVgenerator

_RPP_start_word_="<HGRPP;"
_RAP_start_word_="<HGRAP;"
_terminate_word_="END"
_obj_name_='ODBPlan'
_obj_name_Ref_='RoamPlan'
_obj_name_Ref_Copy='ODB_Reference_File'
_object_start_="RSA"
_input_directory_= config.project_path+'/log/'+"ericsson/"+_obj_name_+'/'
_input_directory_Ref_= config.project_path+'/log/'+"ericsson/"+_obj_name_Ref_+'/'
# list of valid odbId
obdIdList=["OBO","OBI","OBR","OBOPRE","OBOPRI","OBSSM","OSB1","OSB2","OSB3","OSB4","OBP","ECT","SRR"]
keyField="RSP"
fieldList=['RSA', 'RSP', 'SRR' , 'RSIP']
_start_word_="HLR ROAMING SERVICE AREA DATA"
_object_start_="RSA"


class EricssonODBPlanparser:
    
    def __init__(self, fileName):
        self.file= fileName
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Mapping Object ODB Plan------********\n")   
  
    def parseAndGenerateInputMap(self,indexdict):
        f = open(self.file, 'r+')
        lines = f.readlines( )
        tempList = []
        rpplist=self.generateRPPDict(lines,indexdict,tempList)
        if self.isSRRExist(lines,indexdict):
            lineobj2={}
            rpp_dict={'identifier':'ODBSRR2','odbId':'SRR','odbTreatment':'RSIP', 'SUD':'SRR-2'}
            lineobj2['identifier']='ODBSRR2'
            lineobj2["treatment_Value"]='2'
            lineobj2["treatment"]='SRR'
            tempList.append(lineobj2)
            rpplist.append(rpp_dict) 
            
        self.logger.info("RPPDict--"+str(rpplist))
        if (tempList != []):
            tempList = list({v['identifier']:v for v in tempList}.values())
            if not os.path.exists(_input_directory_Ref_):
                    os.makedirs(_input_directory_Ref_)
            ODBReference_File =_input_directory_Ref_+"ericsson_"+_obj_name_Ref_Copy+".json"
            with open(ODBReference_File, 'w') as fout:
                json.dump(tempList, fout)      
        
        return rpplist
    
    def isSRRExist(self,lines,indexdict): 
        self.logger.debug("checking for SRR-")
        RPPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _RAP_start_word_,0)
        if RPPStartLine>0:
            endline=FileUtil.FileUtil.getLineNumWithStatement(self.file,_terminate_word_,RPPStartLine)
            currLine=RPPStartLine
            d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "RAP_SRR")
            SRRStartPos=int(d.get('startIndex'))-1
            SRRLastPos=int(d.get('endIndex'))-1
            d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "RAP_RSP")
            RSPStartPos=int(d.get('startIndex'))-1
            RSPLastPos=int(d.get('endIndex'))-1
            d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "RAP_RSIP")
            RSIPStartPos=int(d.get('startIndex'))-1
            RSIPLastPos=int(d.get('endIndex'))-1
            sRRList=[]
            while(currLine<endline):
                RSAStart= FileUtil.FileUtil.getLineNumWithStatement(self.file, "RSA", currLine)
                if(RSAStart>0):
                    attr_header=FileUtil.FileUtil.getLineNumWithWord(self.file, "SRR", RSAStart)
                    RSPEnd= FileUtil.FileUtil.getLineNumWithStatement(self.file, "RSA", attr_header)
                    if(RSPEnd==-1):
                        RSPEnd= endline
                    for line in range(attr_header+1,RSPEnd):
                        currLine=line
                        srrVal= lines[currLine][SRRStartPos:SRRLastPos].strip()
                        rspVal= lines[currLine][RSPStartPos:RSPLastPos].strip()
                        rsipVal= lines[currLine][RSIPStartPos:RSIPLastPos].strip()
                        #self.logger.debug("srrVal---"+srrVal)
                        if(srrVal=='2'):
                            self.logger.debug("rsp ="+rspVal +"  SRR= "+srrVal +" and RSIP= "+rsipVal)
                        if(len(srrVal)>0 and srrVal not in sRRList ):
                            sRRList.append(srrVal)
                else:
                    self.logger.info("Finished reading RAP Object. SRR List is :"+ str(sRRList))
                    break;
            if('2' in sRRList):
                return True    
        else:
            return False    
        return False;
    def generateRPPDict(self,lines,indexdict,tempList=[]):
        dataList=[]
        
        RPPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _RPP_start_word_,0)
        endline=FileUtil.FileUtil.getLineNumWithStatement(self.file,_terminate_word_,RPPStartLine)
        hLine=RPPStartLine+2
        while (hLine>0 and hLine<endline):
            start=self.getRSPorRSIPNextLine(lines,hLine,endline)
            end=self.getRSPorRSIPNextLine(lines,start+1,endline)
            if(end==-1):
                end=endline
            SUDline=FileUtil.FileUtil.getLineNumWithStatementBetweenLines(self.file, "SUD",start,end)
            if(start>0 and SUDline>0 and end>0):
                ValueofRSPorRSIP = self.getValueRSIPorRSP(self.file, start+1, end)
                treatment=lines[start].strip()
                sudList=self.getSUDdata(lines,SUDline,end)
                self.logger.debug("SUDList for RSP--"+ lines[start+1] +"is--"+str(sudList))
                for item in sudList:
                        dataArr=item.split('-')
                        odbId=dataArr[0]
                        odbValue=dataArr[1]
                        if odbId in obdIdList:
                            lineobj={}
                            lineobj1={}
                            lineobj['identifier']="ODB"+item
                            lineobj1['identifier']="ODB"+item
                            lineobj1["treatment_Value"]=ValueofRSPorRSIP
                            lineobj1["treatment"]=treatment
                            lineobj["odbId"]=odbId
                            lineobj["odbTreatment"]=treatment
                            lineobj["odbValue"]=odbValue
                            lineobj["SUD"]=item
                            dataList.append(lineobj)
                            tempList.append(lineobj1)
            hLine=end
        #=======================================================================
        # if (tempList != []):
        #         tempList = list({v['identifier']:v for v in tempList}.values())
        #         ODBReference_File =_input_directory_Ref_+"ericsson_"+_obj_name_Ref_Copy+".json"
        #         with open(ODBReference_File, 'w') as fout:
        #             json.dump(tempList, fout)      
        #=======================================================================
        return dataList    
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
            
    def generateRAPDict(self,lines,indexdict):
        RAPStartLine=FileUtil.FileUtil.getLineNumWithStatement(self.file, _RAP_start_word_,0)
        d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "RAP_RSA")
        RSAStartPos=int(d.get('startIndex'))-1
        RSALastPos=int(d.get('endIndex'))-1
        hline=FileUtil.FileUtil.getLineNumWithWord(self.file, _object_start_,RAPStartLine)
        endline=FileUtil.FileUtil.getLineNumWithStatement(self.file,_terminate_word_,RAPStartLine)
        currLine= hline
        rap_dict={}
        while(hline>0 and hline<endline):
            self.logger.debug("At line "+lines[hline])
            RSA=lines[hline+1][RSAStartPos:RSALastPos]
            identifier= "RSA_"+str(RSA)
            #rap_dict["identifier"]=identifier
            currLine=currLine+1
            tline=FileUtil.FileUtil.getLineNumWithWord(self.file, _object_start_,currLine)
            d= JSONUtil.JSONUtil.getJsonObjectWithVal(indexdict, 'Attribute', "SRR")
            SRRStartPos=int(d.get('startIndex'))-1
            SRRLastPos=int(d.get('endIndex'))-1
            datalist=[]
            for row in range(currLine+1,tline-1):
                dataString=lines[row]
                currLine=currLine+1
                if(len(str(dataString).strip())>0 and "SRR" not in dataString):
                    SRR=dataString[SRRStartPos:SRRLastPos].strip()
                    datalist.append(SRR)
            
            rap_dict[identifier]=datalist
            hline=tline
        JSONUtil.JSONUtil.writeDictInJsonFile(rap_dict,_input_directory_+"RAP.json")
        return rap_dict
            
    def getRSPorRSIPNextLine(self,lines,hLine,endline):
        for i in range(hLine,endline):
            if(lines[i].strip()=="RSP" or lines[i].strip()=="RSIP"):
                return i
        return -1
        
           
    def generateInputJson(self):
        try:
            # Start Dynamic Generation code 
            csvgen= CSVgenerator(self.file,_start_word_,keyField,fieldList)
            csvFile=_input_directory_+"ODBPlan.csv"
            indexInfoList=csvgen.generateIndexDict(self.file, _start_word_, keyField)
            indexInfoList2=csvgen.generateIndexDict(self.file, _start_word_, _object_start_)
            indexInfoList=indexInfoList2+indexInfoList
            csvgen.addPrefixTokey(indexInfoList , 'RAP')
            csvgen.writeDictToCSV(csvFile, indexInfoList)
            self.logger.info("csv updated---"+csvFile)
            indexdict=indexInfoList            
            #End Dynamic Generation code             
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
    
    
    def getValueRSIPorRSP(self ,inputFilePath,startIndex,endIndex): 
        
        infile=open(inputFilePath, 'r')
        lines = infile.readlines()
        for i in range(startIndex,endIndex):
            if(lines[i].strip()!=None):
                return lines[i].strip()            
        return -1    
    
    
if __name__ == '__main__':
    _index_csv=config.src_path+"/config/ODBPlan.csv"
    _input_dumpfile_=config.project_path+"/inputFiles/ericsson/TNHLR1_HGRPP.log"
    indexdict=FileUtil.FileUtil.dumpCsvIndict(_index_csv,_input_directory_+_obj_name_+"_index.json")
    textparser1 = EricssonODBPlanparser(_input_dumpfile_,_index_csv)
    inputJson=textparser1.generateInputJson();
    print("done")