'''
Created on 05-Apr-2018

@author: vkhanna
'''
from library import xlrd
import copy
import logging
import os
import sys
import pprint
import json
from config import config

class mapper:
	def __init__(self,mappingWorkbookPath,mappingSheetName,customer):
		self.mappingWorkbookPath = mappingWorkbookPath
		self.mappingSheetName = mappingSheetName
		self.logger = logging.getLogger(__name__)
		self.loggerHdlr = logging.FileHandler(config.log_file)
		self.formatter = logging.Formatter('%(asctime)s %(levelname)s %(lineno)s %(message)s')
		self.workbook = None
		self.worksheet = None 
		self.mappingInfo=[]
		self.customer=customer



	def isMergedCell(self, rowx, colx):
		self.logger.debug ("inside isMergedCell rowx =%d colx = %d"% (rowx,colx))
		for crange in self.worksheet.merged_cells:
			rlo, rhi, clo, chi = crange
			
			if rowx in range(rlo, rhi):
				if colx in range(clo, chi):
					if rlo != rowx :
						return True
		return False 

	def unmergedValue(self,rowx,colx):
		for crange in self.worksheet.merged_cells:
			rlo, rhi, clo, chi = crange
			if rowx in range(rlo, rhi):
				if colx in range(clo, chi):
							return self.worksheet.cell_value(rlo,clo)
		#if you reached this point, it's not in any merged cells
		return self.worksheet.cell_value(rowx,colx)

	def isBlank(self,cell_value):
		if (cell_value == ""):
				return True
		else:
				return False  

	def strType(self,type,var):
		try:
			if type == xlrd.XL_CELL_BOOLEAN:
				return "bool"
			if int(var) == float(var):
				return 'int'
		except:
			try:
				float(var)
				return 'float'
			except:
				return 'str'


	def CellValue(self,cell_type, cell_value):
		cellval = cell_value
		rettype =  self.strType(cell_type,cell_value)
		self.logger.debug("******RETTYPE1 = %s %s******"%(rettype,cell_value))
		if (True == self.isBlank(cell_value)):
			string = ""
			self.logger.debug ("returning from here")
			return string 
		if (rettype == 'float'):
			self.logger.debug("inside float")
			if (cell_value == int(float(cell_value))):
				cellval = int(float(cell_value))
		elif (rettype == 'int'):
			self.logger.debug("Inside int") 
			cellval = int(cell_value)
			self.logger.debug("int value %d"%cellval)
		elif (rettype == 'bool'):
			self.logger.debug("Inside bool")
			cellval = ("FALSE", "TRUE")[cell_value]
		else:
			self.logger.debug ("inside else")
			cellval = cell_value
		self.logger.debug (cellval)	    	
		return cellval	 


								
	def construct_MappingInfo(self):
				 # open the mapping workbook and the worksheet
					self.workbook = xlrd.open_workbook  (self.mappingWorkbookPath )
					# check for errors
					self.worksheet = self.workbook.sheet_by_name(self.mappingSheetName)
		 			#self.logger.debug("customer--"+ self.customer)
					# check for errors
					if (self.worksheet.nrows > 0 and self.worksheet.ncols > 1):
						self.objectname = self.worksheet.cell_value(0,1)
						config.nokiaObjectName = self.worksheet.cell_value(0,1)
						self.logger.debug ("nokia object name = %s" %config.nokiaObjectName)
						self.logger.debug ("object name = %s "%self.objectname)
						self.logger.debug (" number of rows = %d " %self.worksheet.nrows)
						self.logger.debug ("number of cols1 = %d " %self.worksheet.ncols)
						print("\n %s :: Parsing Mapping Sheet"%(config.nokiaObjectName))
						mappingAtribute = {}
						#for row in range(2,self.worksheet.nrows):
						row = 2
						while row < self.worksheet.nrows:
							#print("row number %d\n",row)
							# it this is a non merged cell or first cell of a merged cell then store new mappingAttribute
							#if ((isMergedCell(row,0) == True and isMergedCell(row -1 , 0) == False) or
							#    isMergedCell(row,0) == False):
							if (self.isMergedCell(row,0) == False):
								# create a new mappintAttribute
								mappingAttribute = {}
								mappingAttribute['row'] = row
							#	print ( "nokiaAttrName = %s faluAttrName = %s characterset = %s" %(self.worksheet.cell_value(row,0),self.worksheet.cell_value(row,2),self.worksheet.cell_value(row,3) ))
								mappingAttribute['nokiaAttrName'] = self.CellValue(self.worksheet.cell_type(row,0), self.worksheet.cell_value(row,0))
								mappingAttribute['isMapped'] = self.CellValue(self.worksheet.cell_type(row,1), self.worksheet.cell_value(row,1))
								mappingAttribute['faluAttrName'] = self.CellValue(self.worksheet.cell_type(row,2), self.worksheet.cell_value(row,2))
								mappingAttribute['characterSet'] = self.CellValue(self.worksheet.cell_type(row,3), self.worksheet.cell_value(row,3))
								attrValMap = []
							#	print("non merged cell")
								valMap = {}
								valMap['faluAttrVal'] = self.CellValue(self.worksheet.cell_type(row,4), self.worksheet.cell_value(row,4))
								valMap['nokiaAttrVal'] = self.CellValue(self.worksheet.cell_type(row,5), self.worksheet.cell_value(row,5))
								attrValMap.append(valMap)
								mappingAttribute['valueSet'] = attrValMap
								self.mappingInfo.append(mappingAttribute)
							else:
								# in case of merged cell, attacheh teh valMap to the last mappintAttribute
								mappingAttribute = self.mappingInfo[-1]
								attrValMap = mappingAttribute['valueSet']
								nextrow = row
								while(self.isMergedCell(nextrow, 0)):
									valMap = {}
							#		print("processing merged cell row %d falu val %s nokia val %s" %(nextrow,self.worksheet.cell_value(nextrow,4),self.worksheet.cell_value(nextrow,5)))
									valMap['faluAttrVal'] = self.CellValue(self.worksheet.cell_type(nextrow,4), self.worksheet.cell_value(nextrow,4))
									valMap['nokiaAttrVal'] = self.CellValue(self.worksheet.cell_type(nextrow,5), self.worksheet.cell_value(nextrow,5))
									attrValMap.append(valMap)
									nextrow = nextrow + 1
							#	print(" setting row to %d"%nextrow) 
								row = nextrow - 1
							row = row + 1		
					return self.mappingInfo

	def storeMappingInfoInJson(self):
		#get the current working directory
		filepath = os.getcwd()
		#print (filepath)
		filepath = filepath + "log/"+self.customer+"/"+self.objectname+"/"
		filedir=config.project_path+'/log/'+"/"+self.customer+"/"+self.objectname+"/"
		
		filename = self.objectname + ".json"
		with open(filedir+filename, 'w') as f:
			json.dump(self.mappingInfo , f , indent=4)
		mappingRecord = {}	
		for mapping in self.mappingInfo:
			if (mapping['isMapped'].lower() == "Yes".lower()):
				mappingRecord[mapping['nokiaAttrName']] = str(mapping['faluAttrName']) + "<" + str(mapping['characterSet']) + ">"
				filename = mapping['nokiaAttrName'] + ".json"
				
				attributeValMap = {}
				for valueMap in  mapping['valueSet']:
					attributeValMap[valueMap['faluAttrVal']] = valueMap['nokiaAttrVal']
				with open(filedir+filename, 'w') as f:
					json.dump(attributeValMap, f, indent=4)
		filename = self.objectname + "_mapping.json"
		with open(filedir+filename,'w') as f:
			json.dump(mappingRecord,f,indent=4)
		
	def constructFaluAttributeSet(self):
					faluAttrSet= {}
					for  mapping in self.mappingInfo:
						if (mapping['isMapped'] == "Yes"):
							faluAttrSet[mapping['faluAttrName']] = 1
					config.faluAttrSet =  faluAttrSet.keys()
				
	def constructNokiaAttributeSet(self):
					NokiaAttrSet= {}
					for  mapping in self.mappingInfo:
						if (mapping['isMapped'] == "Yes"):
							#print ("%s",mapping['nokiaAttrName'])
							NokiaAttrSet[mapping['nokiaAttrName']] = 1
					config.nokiaAttrSet = 	NokiaAttrSet.keys()		

#if __name__ == '__main__':
#		MapperObj = mapper(sys.argv[1],sys.argv[2])
		
		#MapperObj.construct_MappingInfo()
		
