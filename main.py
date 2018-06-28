import sys
import os as os
print("Inside main--"+ sys.path[0])
main_path = sys.path[0]
src_path = main_path+"\\src\\"
sys.path.append(src_path)
from writer.writer import writer
from config import config
from config import loggingImpl
from library import xlrd
from wrapper import wrapper
from utility import JSONUtil
from utility import FileUtil
import logging
from utility.ApplicationException import ApplicationError

if __name__ == '__main__':
	logger = loggingImpl.loggingImpl.getLogger()
	
	#===========================================================================
	#customer = "ericsson"
	#inputExcel = "D:/userdata/djyoti/Desktop/2018/SDM/Code/svn/0405/templates/NSRdata_HLR_ericsson.xlsm"
	#===========================================================================
	
	#===========================================================================
	# _input_dumpfile_ = sys.argv[1]
	# logger.info("processing input dump " + _input_dumpfile_)
	#===========================================================================
	#===========================================================================
	customer = sys.argv[2]
	inputExcel = sys.argv[1]
	#===========================================================================
	
	logger.info("input data found for customer " + customer + " excel path is " + inputExcel)
	wb = xlrd.open_workbook(inputExcel)
	config.customer=customer
	
	
	worksheet = wb.sheet_by_name("Contents")
	
	num_rows = worksheet.nrows 
	num_cols = worksheet.ncols 
	initial_header_row = 2 
	start_column_num = 1
	last_col_num = 2
	_inputFile_Address_Col =10

	wrap = wrapper()
	### Getting list of Object to be processed
	demoList = wrap.fetchingObect(worksheet, num_rows, initial_header_row, start_column_num, last_col_num)
	logger.info("Mains-start---"+str(demoList))
	try:
		for _obj_name_ in demoList[:]:
			logger.info("config.project_path---"+config.project_path)
			d=config.project_path+"\\log\\"+customer+"\\"+_obj_name_
			if not os.path.exists(d):
				os.makedirs(d)
			logger.info(_obj_name_)
			if (_obj_name_ == "BearerCapabilitySet" or "OCsi" or "TCsi" or "SMSCsi" or "QualityOfServiceProfile" or "UgCsi"  or "PDPContext" or "RoamingArea" or "RoamPlan"):
				logger.info(_obj_name_)
				x = FileUtil.FileUtil.getCellPositionWithString(worksheet, _obj_name_, initial_header_row, 56, start_column_num, 2)
				logger.debug(x)
				fileName=worksheet.cell_value(x[0],x[1]+2)
				defaultFileName=config.project_path+"\\inputFiles\\"+customer+"\\"+fileName	
				logger.debug("default path--"+defaultFileName)
				try:
					_input_dumpfile_ = worksheet.cell_value(x[0], x[1]+8)
				except(Exception):
					_input_dumpfile_=defaultFileName
					logging.exception("taking default value")
				logger.debug("_input_dumpfile_---"+_input_dumpfile_)
				#_input_dumpfile_="D://Data/Roam-Plan/code/inputFiles/ericsson/HLR2 DUMP_16JUN17.log"
				wrap.mapToNokiaObject(_obj_name_,_input_dumpfile_,customer,inputExcel)
			
		else : 
			print("#######################")
		print( "\n %s:: Writing values to Planning Sheet" %config.nokiaObjectName)
		writerObj = writer(inputExcel, demoList)
		writerObj.writeValues()
		input ( "\n\n******  Mapping Successful!! Press Enter to exit  ******" )
	except ApplicationError as e:
		input("\n\n ---\t Failed!!!--"+e.msg)
	except(Exception):
		logging.exception("error!!!!")	
		input("error occured, Check Log for details, press enter to exit!!!!")
