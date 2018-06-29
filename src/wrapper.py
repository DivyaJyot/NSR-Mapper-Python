'''
Created on 28-Mar-2018

@author: djyoti
This is a wrapper class which instantiate parser corresponding object and trigger the generation of input Json.
For every new object this file will contains a constructor call of its parser. It contains method to call mapper.
'''
from config import config
from config import loggingImpl
from converter.NokiaMapGenerator import nokiaDataGenerator
from mapper.mapper import mapper
from parsers.erricsson.ericssonBCDparser import ErricssonBCSparser
from parsers.erricsson.ericssionqOSparser  import ErricssonQOSparser
from parsers.fALU.faluBCDParsers import fALUBCSparser
from parsers.fALU.faluOCSiParsers import fALUOCSIparser
from parsers.fALU.faluTCSiParsers import fALUTCSIparser
from parsers.fALU.faluUGCSiParsers import fALUUGCSIparser
from parsers.fALU.faluPDPContextParsers import fALUPDPCONTEXTparser
from parsers.fALU.faluQualityOfServiceProfileParser import fALUQualityOfServiceProfileParser
from parsers.fALU.faluRoamingArea import fALURoamingAreaParser
from parsers.fALU.faluSmsCsiParser import fALUSmsCSIparser
from parsers.erricsson.ericssionOCsiparser import ErricssonOCsiparser
from parsers.erricsson.ericssonSMSCsiparser import ErricssonSMSCsiparser
from parsers.erricsson.ericssonUgCsiparser import ErricssonUgCsiparser
from parsers.erricsson.ericssonRoamingAreaparser import EricssonRoamingAreaparser
from parsers.erricsson.ericssonODBPlanparser import EricssonODBPlanparser
from parsers.erricsson.ericssionSSPlanparser import EricssonSSPlanparser
from parsers.erricsson.ericssonRoamPlanparser import EricssonROAMPlanparser
from parsers.erricsson.ericssonTCSIparser import ErricssonTCsiparser
from utility.ApplicationException import ApplicationError


class wrapper:

    def __init__(self):
        self.logger = loggingImpl.loggingImpl.getLogger();
        self.logger.info("Inside wrapper")
    
    def  fetchingObect(self ,worksheet, num_rows , initial_header_row , start_column_num, last_col_num):
        validList = []
        self.logger.info("Methods Start fetchingObect to be mapped")
        for curr_row in range(initial_header_row, num_rows, 1):
                for curr_col in range(start_column_num, last_col_num, 1):
                    data = worksheet.cell_value(curr_row, curr_col)  # Read the data in the current cell
                    temp_data = worksheet.cell_value(curr_row, curr_col + 1)
                    if (temp_data == "yes"):
                        validList.append(data)           
        return validList 
       
    def mapToNokiaObject(self,_obj_name_,_input_dumpfile_,customer,inputExcel):    
            
            self.logger.info(_obj_name_ + "-Map")
            print("***************** Mapping Started for "+ _obj_name_+"*****************  \n")
            MapperObj = mapper(inputExcel, _obj_name_ + "-Map",customer)
            MapperObj.construct_MappingInfo()
            MapperObj.constructFaluAttributeSet();
            MapperObj.constructNokiaAttributeSet();
            MapperObj.storeMappingInfoInJson();
            self.logger.info("processing input dump " + _input_dumpfile_)
            self.logger.info(" **************** MappingInfo structure ********************* ")
            self.logger.info("***************************************************************")
            
            print("\n %s :: Parsing Input Dump File %s "%(config.nokiaObjectName,_input_dumpfile_))
            ParserObj = self.getInstance(_obj_name_, customer, _input_dumpfile_)
            inputFile = ParserObj.generateInputJson()
            self.logger.info("input json generated at " + inputFile)
            
            print("\n %s :: Converting to Nokia Object" % config.nokiaObjectName)
            nokiaDataGeneratorins = nokiaDataGenerator(inputFile,_obj_name_)
            result = nokiaDataGeneratorins.generateNokiaDataSet();
            if(len(result) == 0):
                self.logger.warning("NokiaDateSet is empty Nothing to write...")
                input("Empty nokiaDataSet,Nothing to write...Make sure input file is correct!! Press enter to exit the window")
                
                
                
    def getInstance(self,_obj_name,customer,_input_dumpfile_):
        '''
        Create Instance of FALUBCSparser
        :param _obj_name:
        :param customer:
        :param _input_dumpfile_:
        '''
        if(_obj_name == "BearerCapabilitySet" and customer=="ericsson"):
            return ErricssonBCSparser(_input_dumpfile_)
        elif(_obj_name == "QualityOfServiceProfile" and customer=="ericsson"):
            return ErricssonQOSparser(_input_dumpfile_)
        elif(_obj_name == "BearerCapabilitySet" and customer=="fALU"):
            return fALUBCSparser(_input_dumpfile_)
        elif(_obj_name == "QualityOfServiceProfile" and customer=="fALU"):
            return fALUQualityOfServiceProfileParser(_input_dumpfile_) 
        elif(_obj_name == "OCsi" and customer=="fALU"):
            return fALUOCSIparser(_input_dumpfile_) 
        elif(_obj_name == "TCsi" and customer=="fALU"):
            return fALUTCSIparser(_input_dumpfile_) 
        elif(_obj_name == "SmsCsi" and customer=="fALU"):
            return fALUSmsCSIparser(_input_dumpfile_)
        elif(_obj_name == "PDPContext" and customer=="fALU"):
            return fALUPDPCONTEXTparser(_input_dumpfile_)
        elif(_obj_name == "RoamingArea" and customer=="fALU"):
            return fALURoamingAreaParser(_input_dumpfile_)
        elif(_obj_name == "OCsi" and customer=="ericsson"):
            return ErricssonOCsiparser(_input_dumpfile_)
        elif(_obj_name == "TCsi" and customer=="ericsson"):
            return ErricssonTCsiparser(_input_dumpfile_)
        elif(_obj_name == "SmsCsi" and customer=="ericsson"):
            return ErricssonSMSCsiparser(_input_dumpfile_)
        elif(_obj_name == "UgCsi" and customer=="fALU"):
            return fALUUGCSIparser(_input_dumpfile_)
        elif(_obj_name == "UgCsi" and customer=="ericsson"):
            return ErricssonUgCsiparser(_input_dumpfile_)
        elif(_obj_name == "RoamingArea" and customer=="ericsson"):
            return EricssonRoamingAreaparser(_input_dumpfile_)
        elif(_obj_name == "ODBPlan" and customer=="ericsson"):
            return EricssonODBPlanparser(_input_dumpfile_);
        elif(_obj_name == "SSPlan" and customer=="ericsson"):
            return EricssonSSPlanparser(_input_dumpfile_);
        elif(_obj_name == "RoamPlan" and customer=="ericsson"):
            return EricssonROAMPlanparser(_input_dumpfile_);
