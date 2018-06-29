'''
Created on 05-Apr-2018

@author: djyoti
common Logging pattern for whole application.
'''
import logging
from config import config
logging.basicConfig(filename=config.project_path+"/log/data.log",
            format='%(asctime)s %(levelname)s %(lineno)s %(message)s')
logger1=logging.getLogger()
logger1.setLevel(logging.DEBUG)
class loggingImpl:

    @staticmethod
    def getLogger():
        return logger1;
