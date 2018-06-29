'''
Created on 20-Apr-2018

@author: djyoti
'''
class ApplicationError(Exception):
    def __init__(self, arg):
        self.msg=arg