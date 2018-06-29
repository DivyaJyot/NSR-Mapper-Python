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

class fALUTCSISubscription:
    def __init__(self , listofFiles):
        self.listofFiles = listofFiles
        self.logger=loggingImpl.loggingImpl.getLogger()
        self.logger.info("\n\t********------Parser_For_Subscription_Dump------********\n")
        
    def generateFaluTCSISubscriptionJson(self):
        
        try :  
            global counter
            filename = log_path+config.nokiaObjectName+'\\fALU_TCSI_Subscription_Dump.json'
            allfiles =self.listofFiles
            frame = pd.DataFrame()
            list_ = []
            for file_ in allfiles:
                fields=['tcsiCamelGmscNotSuppDfltHandl','tcsiCamelCapabilityHandling','camelLocationRequestFlag','camelStatusRequestFlag','tcsiTermAttemptTdpScpIsdn','tcsiTermAttemptTdpServKey','tcsiTermAttemptTdpDfltCalH']
                df = pd.read_csv(file_,sep=';',skiprows=2, header=0, usecols=fields)
                list_.append(df)
            frame = pd.concat(list_)
            dict_test1 = {'tcsiCamelGmscNotSuppDfltHandl':frame['tcsiCamelGmscNotSuppDfltHandl'], 'tcsiCamelCapabilityHandling':frame['tcsiCamelCapabilityHandling'],'camelLocationRequestFlag':frame['camelLocationRequestFlag'], 'camelStatusRequestFlag':frame['camelStatusRequestFlag'],'tcsiTermAttemptTdpScpIsdn':frame['tcsiTermAttemptTdpScpIsdn'],'tcsiTermAttemptTdpServKey':frame['tcsiTermAttemptTdpServKey'],'tcsiTermAttemptTdpDfltCalH':frame['tcsiTermAttemptTdpDfltCalH']}
            data = pd.DataFrame(dict_test1)
            uni_comb=data.drop_duplicates()
            u2 = uni_comb.to_dict(orient = "records")
            # JSON Modified 
            
            for item in u2:
                var1 = item['tcsiTermAttemptTdpScpIsdn']
                var2 = item['camelLocationRequestFlag']                
                var3 = item['tcsiTermAttemptTdpServKey']
                var4 = item['camelStatusRequestFlag']
                if (var4 == 1):
                    mod_var4 = 'true'
                    item['camelStatusRequestFlag'] = mod_var4
                elif(var4 ==0):
                     mod_var4 = 'false'
                     item['camelStatusRequestFlag'] = mod_var4    
                mod_var1 = str(var1)
                mod_var3 = str(var3)
                item['tcsiTermAttemptTdpScpIsdn'] = mod_var1
                item['tcsiTermAttemptTdpServKey'] = mod_var3                
                if (var2 == 1):
                    mod_var2 = 'true'
                    item['camelLocationRequestFlag'] = mod_var2
                elif(var2 ==0):
                     mod_var2 = 'false'
                     item['camelLocationRequestFlag'] = mod_var2                    
                
                if (item['tcsiTermAttemptTdpScpIsdn']!= None):
                     item["tdpid"] = "2"
                     
                item['GsmServiceProfile'] = "TCSi_"+ str(counter) 
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

        


