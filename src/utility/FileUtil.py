'''
Created on 28-Mar-2018

@author: djyoti
'''
import csv

from utility import JSONUtil

class FileUtil:
    @staticmethod
    def dumpCsvIndict(inputFilePath,outputFilePath):
        '''
        This method reads a csv file and return a dictionary.First,line of csv should contains keys separated by comma
        '''
        infile=open(inputFilePath, 'r')
        reader1 = csv.reader(infile)
        reader=list(reader1)
        resultdict =[]
        for i in range(1,len(reader)):
            d = {}
            length=len(reader[0])
            for j in range(0,length):
                d[reader[0][j]]= reader[i][j]
            resultdict.append(d)
        if(outputFilePath!= None and len(outputFilePath)>0):
            JSONUtil.JSONUtil.writeDictInJsonFile(resultdict,outputFilePath)
        infile.close()
        return resultdict
    
    @staticmethod
    def getLineNumWithWord(inputFilePath,word,startIndex):   
        '''
        return index of line(0 for line1)
        :param inputFilePath: file in which word as to be searched
        :param word: word to be searched
        :param startIndex:
        '''
        infile=open(inputFilePath, 'r')
        lines = infile.readlines()
        for i in range(startIndex,len(lines)):
            if(word in lines[i]):
                return i
        return -1
    @staticmethod       
    def getCellPositionWithString(sheet,matchString,startrow,endrow,startcol,endcol): 
        for rowidx in range(startrow,endrow):
            for colidx in range(startcol,endcol):
                if (sheet.cell(rowidx,colidx).value == matchString) :
                    return (rowidx, colidx)

    @staticmethod
    def getLineNumWithStatement(inputFilePath,word,startIndex):   
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
    
    @staticmethod
    def getLineNumWithStatementBetweenLines(inputFilePath,word,startIndex,endIndex): 
        
        infile=open(inputFilePath, 'r')
        lines = infile.readlines()
        for i in range(startIndex,endIndex):
            if(word.strip()==lines[i].strip()):
                return i
        return -1    
    
    @staticmethod
    def getNextDataLine(lines,startLineIndex):
        dataLine=startLineIndex+1
        while(len(lines[dataLine].strip())==0):
            dataLine=dataLine+1
        return dataLine
        