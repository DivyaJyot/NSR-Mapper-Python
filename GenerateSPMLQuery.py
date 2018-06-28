
import copy
import logging
import sys 
import os
main_path = sys.path[0]
src_path = main_path+"\\src\\"
sys.path.append(src_path)
from wrapper import wrapper
from library import xlrd
def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)
sys.excepthook = show_exception_and_exit

skipWorksheet = ['General Info' , 'Contents' , 'LogErrors']
class SPMLQueryGenerator:
	nsr_workbook_name = ""
	def __init__(self,worksheetName,outputDir,timestamp):
		print ("Inside init")
		print (worksheetName)
		self.nsr_workbook_name = worksheetName
		print(" %s" % self.nsr_workbook_name)
		self.workbook = xlrd.open_workbook (self.nsr_workbook_name )
		self.outputDir  = outputDir
		self.timestamp = timestamp
##############
		worksheet = self.workbook.sheet_by_name("Contents")
	
		num_rows = worksheet.nrows 
		num_cols = worksheet.ncols 
		initial_header_row = 2 
		start_column_num = 1
		last_col_num = 2
		_inputFile_Address_Col =10

		wrap = wrapper()
	### Getting list of Object to be processed
		demoList = wrap.fetchingObect(worksheet, num_rows, initial_header_row, start_column_num, last_col_num)
		#logger.info("Mains-start---"+str(demoList))
		print( demoList)
		_obj_name_ = ""
		for _obj_name_ in demoList[:]:
			if ((_obj_name_ in skipWorksheet) or (self.isMapSheet(_obj_name_) == True)):
				print("Skip %s"%_obj_name_)
			else:
				print ("Creating SPML Query for %s"%_obj_name_)
				self.createSPMLGetQuery(_obj_name_, self.timestamp)
#############
	def isMapSheet(self,worksheetname):
		if (worksheetname[-4:] == '-Map' ):
			return True		
		else:
			return False	
	def createSPMLGetQuery(self,objectName,timestamp):
		# Create a file in the inbox directory
		
		# Change directory to inbox
		inbox_path = os.path.abspath(self.outputDir)
		print (self.outputDir)
		spmlQueryFileName = os.path.join(inbox_path,objectName+ timestamp + ".xml")
		spmlQueryFileObj  = open(spmlQueryFileName,'w')
		spmlQueryFileObj.write('<spml:searchRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:spml="urn:siemens:names:prov:gw:SPML:2:0\n')
		spmlQueryFileObj.write('xmlns:subscriber="urn:siemens:names:prov:gw:HLR_SUBSCRIBER:4:5"> <version>HLR_NSR_v21</version>\n')
		spmlQueryFileObj.write('       <base>\n')
		spmlQueryFileObj.write('            <objectclass>%s</objectclass>\n'%objectName)
		spmlQueryFileObj.write('       </base>\n')	
		spmlQueryFileObj.write('</spml:searchRequest>')


if __name__ == '__main__':
    SPMLQueryGenerator_obj = SPMLQueryGenerator(sys.argv[1], sys.argv[2], sys.argv[3])
   
    #===========================================================================
    # for SPMLQueryGenerator_obj.worksheet in SPMLQueryGenerator_obj.workbook.sheets():
    #     wname = SPMLQueryGenerator_obj.worksheet.name
    #     if ((wname in skipWorksheet) or (SPMLQueryGenerator_obj.isMapSheet(wname) == True)):
    #     	print("Skip %s"%wname)
    #     else:	
    #     	print ("Creating SPML Query for %s"%wname)
    #     	SPMLQueryGenerator_obj.createSPMLGetQuery(wname)
    #===========================================================================
