'''
Created on 14-Jun-2018

@author: djyoti
This file contains utility methods to generate configuration csv
'''
import csv
from utility import FileUtil
class CSVgenerator:
    def __init__(self,_input_dumpfile_,_start_word_,key,fieldList):
        self._input_dumpfile_= _input_dumpfile_
        self._start_word_=_start_word_
        self.key=key
        self.fieldList=fieldList
        
    # Write dict to CSV
    def writeDictToCSV(self, csvFile, indexInfoList):
        with open(csvFile, 'w', newline='') as csvfile:
            fieldnames = ['Attribute', 'startIndex', 'endIndex']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(indexInfoList)
        csvfile.close()     
        return csvfile

    def generateIndexDict(self,_input_dumpfile_,_start_word_,key):
        startLine= FileUtil.FileUtil.getLineNumWithWord(_input_dumpfile_, _start_word_,0)
        hLine=FileUtil.FileUtil.getLineNumWithWord(_input_dumpfile_, key,startLine)
        f = open(_input_dumpfile_, 'r+')
        lines = f.readlines()
        keyString=lines[hLine]
        
        indexInfoList=[]
        currentIndex=0
        while(currentIndex<=len(keyString)):
            while( currentIndex<len(keyString) and keyString[currentIndex]==" "):
                currentIndex=currentIndex+1
            startIndex= currentIndex
            currentIndex=currentIndex+1
            while( currentIndex<len(keyString) and keyString[currentIndex]!=" " ):
                    currentIndex=currentIndex+1
            while( currentIndex<len(keyString) and keyString[currentIndex]==" "):
                currentIndex=currentIndex+1
            endIndex=currentIndex
            if(currentIndex>=len(keyString)-1):
                endIndex=-1
            
            field=keyString[startIndex:endIndex].strip()
            if(len(field)>0):
                indexInfo={}  
                indexInfo["Attribute"]=field
                indexInfo["startIndex"]=startIndex+1
                indexInfo["endIndex"]=endIndex
                indexInfoList.append(indexInfo) 
        return indexInfoList
    
    
    def addPrefixTokey(self,indexInfoList,prefix):
        for d in indexInfoList:
            d.update((k1, prefix+"_"+v) for k1, v in d.items() if k1 == "Attribute")
            
#===============================================================================
# if __name__== '__main__': 
#     _input_dumpfile_="D:/userdata/djyoti/Desktop/2018/SDM/Code/svn/12-06-18/inputFiles/ericsson/ER_BCS.log"
#     _start_word_="HLR PLMN BEARER CAPABILITY DATA"
#     key="ACCST"
#     fieldList=['BC', 'ADDNUM', 'ITC', 'RC', 'ACC', 'ACCST', 'ITN', 'BS']      
#     csvgen= CSVgenerator(_input_dumpfile_,_start_word_,key,fieldList)
#     csvgen.generateIndexDict(_input_dumpfile_, _start_word_, key, fieldList)
#===============================================================================