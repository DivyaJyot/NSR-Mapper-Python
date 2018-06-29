'''
Created on 22-Mar-2018

@author: djyoti
'''
import re
import json
import sys
from pathlib import Path
import os
import pprint
from config import config
from config import loggingImpl
from converter import falu_handlers

class nokiaDataGenerator:
    def __init__(self, fileName,_obj_name_):
        self.datafile= fileName
        self._obj_name=_obj_name_
        self.nokiaAttrdict =   dict.fromkeys(config.nokiaAttrSet,"") 
        self.logger1=loggingImpl.loggingImpl.getLogger()
        self.logger1.info("Inside class nokiaDataGenerator--- \n")
        self.root_directory= config.project_path+'\\log\\'+config.customer+"\\"+_obj_name_+"\\"
    def generateNokiaDataSet(self):
        json_data=open(self.datafile).read()
        data = json.loads(json_data)
        result=[]
        self.logger1.info("Object name is"+config.nokiaObjectName)
        for item in data:
            itemdata=self.generateNokiaDictSet(item)
            if(len(itemdata)>0):
                result.append(itemdata)
        with open(self.root_directory+'/'+self._obj_name+'_output.json', 'w') as f:
            json.dump(result, f, indent=4) 
        return result
    def generateNokiaDictSet(self,item):
        self.logger1.info('processing item ---\n\t\t' +str(item))
        nokiacustFieldmapperDir=self.root_directory+'/'+self._obj_name+'_mapping.json'
        attributeKeyMap = json.loads(open(nokiacustFieldmapperDir).read())
        nokiadict={}
        skippedList=[]
        for data in self.nokiaAttrdict:
            self.logger1.info('\n\t\t\n fetching data---'+data+ '  from '+self.root_directory+data+'.json')
            filename= self.root_directory + "/" + data+'.json'
            if(Path(filename).exists()):
                self.logger1.info('Reading file --'+filename)
                attributeJson=json.loads(open(filename).read())
                attributeJson = {x.translate({32: None}): y for x, y in attributeJson.items()}   
                self.logger1.info("attributeJson--"+str(attributeJson))
                
                try:
                    ##Reading FalueAttribute&CharacterSet
                    attrCharactepos=attributeKeyMap[data]
                    self.logger1.debug("attrCharactepos--"+attrCharactepos)
                    attr=attrCharactepos[:int(attrCharactepos.find('<'))]
                    char=attrCharactepos[int(attrCharactepos.find('<'))+1:int(attrCharactepos.find('>'))]
                    charList=re.split(',',char)
                    self.logger1.debug("attribute and char--"+str(attr)+str(charList))
                    custAttrComplete=item.get(attr)
                    if(custAttrComplete !=None):
                        self.logger1.debug('custAttrComplete--'+str(custAttrComplete))
                        if((len(attributeJson))==1):
                            custVal=custAttrComplete
                            for key in attributeJson:
                                if(str(attributeJson[key]).startswith('handler:')):
                                    nokiaVal = falu_handlers.callHandlerFromString(item,attributeJson[key])
                                elif(key.startswith('<')):
                                    nokiaVal=custAttrComplete
                                else:
                                    nokiaVal= attributeJson.get(custVal)
                        else:
                            custVal=""
                            for i in charList:
                                if(i=='0'):
                                    custVal= custAttrComplete
                                else:
                                    if(len(custAttrComplete)>=int(i)):
                                        custVal=custVal+str(custAttrComplete[int(i)-1])
                                nokiaVal=attributeJson.get(custVal)
                                if(nokiaVal== None and custVal!=None and len(str(custVal))>0 ):								
                                    nokiaVal= attributeJson.get(str(custVal).strip())
                        self.logger1.info("custVal:"+str(custVal)+"--nokiaVal:"+str(nokiaVal))
                        nokiadict[data]=nokiaVal
                    else:
                        skippedList.append(data)
                except( Exception):
                    self.logger1.error("Exception occurred while fetching value of "+data+" Check the input file ")
                    self.logger1.error(Exception.__traceback__)
                    raise
            else:
                self.logger1.error("file not found at--"+self.root_directory+data+'.json')
        self.logger1.info('nokiaVal json:----\n'+str(nokiadict))
        self.logger1.warning(str(skippedList)+" not found, so skipping this ")
        return nokiadict
        
        
#if __name__ == '__main__':
#    
#    nokiaDataGeneratorins = nokiaDataGenerator(inputFile)
#    nokiaDataGeneratorins.generateNokiaDataSet(inputFile);
        
