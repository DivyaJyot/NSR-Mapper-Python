'''
Created on 05-Apr-2018

@author: djyoti
This contains project level configuration information
'''
import os

nokiaObjectName = None
faluObjectName = None
ericssonObjectName = None
faluAttrSet = []
nokiaAttrSet = []
src_path = None
project_path = None
customer= None
# Setting global path variables
config_path = os.path.dirname(os.path.abspath(__file__)) 
src_path = os.path.split(config_path)[0] # This is your Project source
project_path =  os.path.split(src_path)[0] # this is the project directory
log_file= project_path+'/log/data.log'
