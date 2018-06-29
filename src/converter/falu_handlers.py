'''
Created on 05-Apr-2018

@author: vkhanna
'''
from config import loggingImpl
from itertools import zip_longest 


logger = loggingImpl.loggingImpl.getLogger()

#===========================================================================================================
# uplinkMaxBR
# This parameter defines the maximum bit rate for uplink delivered by UMTS and 
# to UMTS at a Service Access Point within a period of time.
#  One value in the following range values, when 
# hSUPAflag is set to false with F_GPRS_102 active, or F_GPRS_102 inactive: - 
# h'FF for 0 kbps - 
# h'01 to h'3F for 1 to 63 kbps in 1kbps increment - 
# h'40 to h'7F for 64 to 568 kbps in 8kbps increments - 
# h'80 to h'FE for 576 to 8640 kbps in 64kbps increments 
# One value in the following range values, when hSUPAflag is set to true with F_GPRS_102 active: - 
# h'01 to h'4A for 8700 to 16000 kbps in 100 kbps increment 
# The maximum rate is [8600 +(binary code value )* 100) ] - 
# h'4B to h'BA for 17 Mbps to 128 Mbps in 1 Mbps increments 
# The maximum rate is [16 Mbps + ((binary code value C 01001010) * 1) ] - 
# h'BB to h'FA for 130 Mbps to 256 Mbps in 2 Mbps increments 
# The maximum rate is [128 Mbps + ((binary code value C 10111010) * 2) ] Value h'FF corresponds to 0 kbps.
#============================================================================================================

def get_QOS_maximumBitRateForUplink_fromFalu(uplinkMaxBR, f_gprs_102,hSUPAflag=0):
    
    uplinkMaxBR = int(uplinkMaxBR)
    hSUPAflag  = int(hSUPAflag)
    nokiaVal = None
    if (hSUPAflag == 0):
        if (uplinkMaxBR == 255): nokiaVal = 0
        if (1 <= uplinkMaxBR <= 63  ): nokiaVal = uplinkMaxBR
        if (64 <= uplinkMaxBR <= 127): nokiaVal = (64 + (uplinkMaxBR - 64)* 8)
        if (128 <= uplinkMaxBR <= 254): nokiaVal=  (576 + ( uplinkMaxBR -  128) * 64)
    return nokiaVal
    
    

def get_QOS_maximumBitRateForDownlink_fromFalu(downlinkMaxBR,f_gprs_100,hSDPAflag=0):
  #  print("inside get_QOS_maximumBitRateForDownlink_fromFalu ")
    downlinkMaxBR = int(downlinkMaxBR)
    hSDPAflag = int(hSDPAflag)
    nokiaVal = None
    
    if(hSDPAflag == 0):
        if(1 <= downlinkMaxBR <= 63): nokiaVal = downlinkMaxBR
        if(64 <= downlinkMaxBR <= 127): nokiaVal = (64 + (downlinkMaxBR - 64) * 8)
        if(128 <= downlinkMaxBR <= 254): nokiaVal =  (576 +(downlinkMaxBR - 128) * 64)
    return nokiaVal 

                                              
def get_QOS_extendedMaximumBitRateForUpLink_fromFalu(uplinkMaxBR,f_gprs_102,hSUPAflag=0):
    uplinkMaxBR = int(uplinkMaxBR)
    hSUPAflag  = int(hSUPAflag)
    nokiaVal = None            
    if ((hSUPAflag == 1) and (f_gprs_102 == "Active")):
        if (1 <= uplinkMaxBR <= 74): nokiaVal = 8600 + (uplinkMaxBR * 100)
        if (75 <= uplinkMaxBR <= 186): nokiaVal =  ((16*1000)+(uplinkMaxBR-74)*1000)
        if (187 <= uplinkMaxBR <= 250): nokiaVal =  ((128*1000))+((uplinkMaxBR-186)*2000)
        if (uplinkMaxBR == 255): nokiaVal =  0
    return nokiaVal

    
def get_QOS_extendedMaxBitRateForDownlink_fromFalu(downlinkMaxBR,f_gprs_100,hSDPAflag=0):
    downlinkMaxBR = int(downlinkMaxBR)
    hSDPAflag = int(hSDPAflag)
    nokiaVal = None
    if ((hSDPAflag == 1) and (f_gprs_100 == "Active")):
        if (1 <= downlinkMaxBR <= 74): nokiaVal = 8600 + (downlinkMaxBR * 100)
        if (75 <= downlinkMaxBR <= 186): nokiaVal =  ((16*1000)+(downlinkMaxBR-74)*1000)
        if (187 <= downlinkMaxBR <= 250): nokiaVal =  ((128 * 1000))+((downlinkMaxBR-186)*2000)
        if(downlinkMaxBR == 255): nokiaVal = 0
    return nokiaVal
    
    
       
def get_QOS_TransferDelay_fromFalu(transferDelay=0):
#===============================================================================
#  "- h'01 to h'0F   from 10 to 150ms in 10ms increments
# - h'10 to h'1F   from 200 to 950ms in 50ms increments
# - h'20 to h'3E   from 1000 to 4000ms in 100 ms increments</description>"
#===============================================================================
    transferDelay = int(transferDelay)
    nokiaVal = None
    if (1 <= transferDelay <= 15 ): nokiaVal = transferDelay * 10
    elif (16 <= transferDelay <= 31): nokiaVal =  200 + (transferDelay - 16) * 50
    elif (32 <= transferDelay <= 62 ): nokiaVal = 1000 + (transferDelay - 32) * 100
    return nokiaVal
     
        
def get_QOS_guranteedBitRateForUplink_fromFalu(uplinkGuaranteedBR,f_gprs_102,hSUPAguaranteeFlag=0):
    uplinkGuaranteedBR = int(uplinkGuaranteedBR)
    hSUPAguaranteeFlag  = int(hSUPAguaranteeFlag)
    nokiaVal = None
    if (hSUPAguaranteeFlag == 0):
        if (uplinkGuaranteedBR == 255): nokiaVal = 0
        if (1 <= uplinkGuaranteedBR <= 63  ): nokiaVal = uplinkGuaranteedBR
        if (64 <= uplinkGuaranteedBR <= 127): nokiaVal = (64 + (uplinkGuaranteedBR - 64)* 8)
        if (128 <= uplinkGuaranteedBR <= 254): nokiaVal=  (576 + ( uplinkGuaranteedBR -  128) * 64)
    return nokiaVal
      
def get_QOS_extendedGuranteedBitRateForUplink_fromFalu(uplinkGuaranteedBR,f_gprs_102,hSUPAguaranteeFlag=0):
    uplinkGuaranteedBR = int(uplinkGuaranteedBR)
    hSUPAguaranteeFlag  = int(hSUPAguaranteeFlag)
    nokiaVal = None            
    if ((hSUPAguaranteeFlag == 1) and (f_gprs_102 == "Active")):
        if (1 <= uplinkGuaranteedBR <= 74): nokiaVal = 8600 + (uplinkGuaranteedBR * 100)
        if (75 <= uplinkGuaranteedBR <= 186): nokiaVal =  ((16*1000)+(uplinkGuaranteedBR-74)*1000)
        if (187 <= uplinkGuaranteedBR <= 250): nokiaVal =  ((128*1000))+((uplinkGuaranteedBR-186)*2000)
        if (uplinkGuaranteedBR == 255): nokiaVal =  0
    return nokiaVal     

def get_QOS_guranteedBitRateForDownlink_fromFalu(downlinkGuaranteedBR,f_gprs_100,hSDPAguaranteeFlag=0):
    downlinkGuaranteedBR = int(downlinkGuaranteedBR)
    hSDPAguaranteeFlag = int(hSDPAguaranteeFlag)
    nokiaVal = None
    
    if(hSDPAguaranteeFlag == 0):
        if(1 <= downlinkGuaranteedBR <= 63): nokiaVal = downlinkGuaranteedBR
        if(64 <= downlinkGuaranteedBR <= 127): nokiaVal = (64 + (downlinkGuaranteedBR - 64) * 8)
        if(128 <= downlinkGuaranteedBR <= 254): nokiaVal =  (576 +(downlinkGuaranteedBR - 128) * 64)
    return nokiaVal 

#Written handler for UGCSi 
def get_UGCSI_identifier_fromFalu(globalServiceCode):
    globalServiceCode = str(globalServiceCode)
    nokiaVal = None
    
    args = [iter(globalServiceCode)] * 2
    y = [''.join(k) for k in zip_longest(*args)]
    demoList = [] 
    x=[]
    for i in y[:]:
        if (i =="2A"):
            i = "*"
        elif (i == "23"):
            i = "#"
        elif i.startswith("3") and len(i)>=2 and (i != "23") :
            i= i.replace("3", "",1).strip()          
        demoList.append(i)
        nokiaVal = "".join(demoList) 
    return nokiaVal 

#Written handler for UGCSI
def get_UGCSI_gsmServiceControlFunctionAddress_fromFalu(globalUcsiScpAddress):
    globalUcsiScpAddress = str(globalUcsiScpAddress)
    nokiaVal = None
    
    args = [iter(globalUcsiScpAddress)] * 1
    y = [''.join(k) for k in zip_longest(*args)]
    for i in y[:2]:
        y.remove(i)
    nokiaVal = "".join(y) 
    
    return nokiaVal 



def get_QOS_extendedGuranteedBitRateForDownlink_fromFalu(downlinkGuaranteedBR,f_gprs_100,hSDPAguaranteeFlag=0):
    downlinkGuaranteedBR = int(downlinkGuaranteedBR)
    hSDPAguaranteeFlag = int(hSDPAguaranteeFlag)
    nokiaVal = None
    if ((hSDPAguaranteeFlag == 1) and (f_gprs_100 == "Active")):
        if (1 <= downlinkGuaranteedBR <= 74): nokiaVal = 8600 + (downlinkGuaranteedBR * 1000)
        if (75 <= downlinkGuaranteedBR <= 186): nokiaVal =  ((16*1000)+(downlinkGuaranteedBR-74)*1000)
        if (187 <= downlinkGuaranteedBR <= 250): nokiaVal =  ((128 * 1000))+((downlinkGuaranteedBR-186)*2000)
        if(downlinkGuaranteedBR == 255): nokiaVal = 0
    return nokiaVal
def  get_QOS_maximumDataUnitSize_fromFalu(maxSduSize=0):
    maxSduSize = int(maxSduSize)
    return maxSduSize * 10
    
falu_handler_list=[
    get_QOS_maximumBitRateForUplink_fromFalu,
    get_QOS_maximumBitRateForDownlink_fromFalu,
    get_QOS_extendedMaximumBitRateForUpLink_fromFalu,
    get_QOS_extendedMaxBitRateForDownlink_fromFalu,
    get_QOS_TransferDelay_fromFalu,
    get_QOS_guranteedBitRateForUplink_fromFalu,
    get_QOS_guranteedBitRateForDownlink_fromFalu,
    get_QOS_extendedGuranteedBitRateForUplink_fromFalu,
    get_QOS_extendedGuranteedBitRateForDownlink_fromFalu,
    get_QOS_maximumDataUnitSize_fromFalu,
    get_UGCSI_identifier_fromFalu,
    get_UGCSI_gsmServiceControlFunctionAddress_fromFalu    
]




def callHandlerFromString(item, handlerString):
  #  print("function callHandlerFromString handlerstring %s "%handlerString)
    #print(item)
    retVal  = None
    handler=handlerString.split(':')[1]
    #print("handler %s"%handler)
    handlerName=(handler.split('(')[0]).strip()
   # print ("handler name %s"%handlerName)
    arguments = handler.split('(')[1]
   # print (arguments)
    temp = arguments.split(')')[0]
    actualArguments = temp.split(',')
 #   print("*****actualArguments %s"%actualArguments)
    kwargs={}
    for arg in actualArguments:
        try:
            kwargs[arg.strip()] = item[arg.strip()]
        except KeyError:
            logger.info("Key Not Present")
            pass    
        
#    print (kwargs)    
#    print (handlerName)
    if (eval(handlerName) in falu_handler_list):
            
          retVal =   falu_handler_list[falu_handler_list.index(eval(handlerName))](**kwargs)
    else:
            print("handler %s  not defined for this"%handlerName)
            
    return retVal        
    
    
    
    
def get_QOS_extendedGuranteedBitRateForDown(**kwargs):
    print("inside get_QOS_maximumBitRateForUplink_fromFalu ")
    for key in kwargs:
        print ("another keyword arg: %s: %s" % (key, kwargs[key]))    