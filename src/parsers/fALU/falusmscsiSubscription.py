'''
Created on 14-May-2018

@author: vivek
'''
import pandas as pd
import glob
import xml.etree.ElementTree as ET
import logging
import os
import json
from config import config
from config import loggingImpl
from builtins import str
from utility.ApplicationException import ApplicationError



log_path=config.project_path+"/log/fALU/"
counter = 1

class fALUSMSCSISubscription:
    def __init__(self , listofFiles):
        self.listofFiles = listofFiles
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Parser_For_Subscription_Dump------********\n")
        
    def generateFaluSMSCSISubscriptionJson(self):
        
        try :  
            global counter
            filename = log_path+config.nokiaObjectName+'\\fALU_SMSCSI_Subscription_Dump.json'
            allfiles =self.listofFiles
            frame = pd.DataFrame()
            list_ = []
            for file_ in allfiles:
                fields=['smocsiCollectedInfoTdpDfltCalH','smocsiCollectedInfoTdpServKey','smocsiCollectedInfoTdpScpIsdn','smocsiCamelCapabilityHandling','RoamingRestrictionType']
                df = pd.read_csv(file_,sep=';',skiprows=2, header=0, usecols=fields)
                list_.append(df)
            frame = pd.concat(list_)
            dict_test1 = {'smocsiCollectedInfoTdpDfltCalH':frame['smocsiCollectedInfoTdpDfltCalH'], 'smocsiCollectedInfoTdpServKey':frame['smocsiCollectedInfoTdpServKey'],'smocsiCollectedInfoTdpScpIsdn':frame['smocsiCollectedInfoTdpScpIsdn'], 'smocsiCamelCapabilityHandling':frame['smocsiCamelCapabilityHandling'],'RoamingRestrictionType':frame['RoamingRestrictionType']}
            data = pd.DataFrame(dict_test1)
            uni_comb=data.drop_duplicates()
            u2 = uni_comb.to_dict(orient = "records")
            # JSON Modified 
            
            for item in u2:
                var1 = item['smocsiCollectedInfoTdpScpIsdn']              
                var3 = item['smocsiCollectedInfoTdpServKey']
                mod_var1 = str(var1)
                mod_var3 = str(var3)
                item['tcsiTermAttemptTdpScpIsdn'] = mod_var1
                item['tcsiTermAttemptTdpServKey'] = mod_var3                                
                
                if (item['smocsiCollectedInfoTdpScpIsdn']!= None):
                     item["triggerDetectionPoint"] = "2"
                     
                item['GsmServiceProfile'] = "SmsCSi_"+ str(counter) 
                counter+=1     
                    
            
            JSONFiles = u2
            self.logger.info("Parsing of Subscription dum completed ")
            
            
            with open(filename, 'w') as f:
                    json.dump(JSONFiles , f , indent=4)
        except(FileNotFoundError):
                self.logger.error("Input file missing:-")
                raise ApplicationError("Input file missing for object:-  "+config.nokiaObjectName)
        except(Exception):
                logging.exception("Error while parsing input dump, check for the correct format")  
                raise                   
        return filename

        


