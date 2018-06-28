# this script compares two XML recusively and reports the diffrences.
# The elements are categorized into object tag.
# ELement within the object tag can be in different order and this script will take care of that.

import os
import xml.etree.ElementTree as ET
import logging
import sys
from sys import argv
from datetime import datetime , date, time
from pathlib import Path, PurePath
logger = logging.getLogger(__name__)
def show_exception_and_exit(exc_type, exc_value, tb):
    import traceback
    traceback.print_exception(exc_type, exc_value, tb)
    input("Press key to exit.")
    sys.exit(-1)
sys.excepthook = show_exception_and_exit


class audit_compare:
    
    def __init__(self,auditDirectoryPath):
        #check if the path exists 
        try:
            if os.path.exists(auditDirectoryPath):
                self.auditPath = (auditDirectoryPath)
                self.inboxPath = PurePath(self.auditPath,"inbox")
                self.outboxPath = PurePath(self.auditPath,"outbox")
                self.reportPath = PurePath(self.auditPath,"reports")
                self.timestamp = datetime.now()
                timestamp_str = self.timestamp.strftime("%d_%m_%H_%M")
                print(timestamp_str)
                print (self.reportPath)
                self.logFileName = str(self.reportPath) + '\AuditReport' + timestamp_str + ".log"
                print(self.logFileName) 
                logger = logging.getLogger(__name__)
                hdlr = logging.FileHandler(self.logFileName)
                formatter = logging.Formatter('%(message)s')
                hdlr.setFormatter(formatter)
                logger.addHandler(hdlr)
                logger.setLevel(logging.DEBUG)    
                if(Path(self.inboxPath).exists()):
                    p = Path(self.inboxPath)
                    for inputFile in p.glob('*.xml'):
                        print (inputFile)
                        #check if response file in the outbox directory
                        inputFileName = os.path.basename(inputFile)
                        outputFile = PurePath(self.outboxPath, inputFileName+ '.res')
                        if os.path.exists(outputFile):
                            print("Outputfile present")
                            objectName = inputFileName.split('_')[0]
                            logger.debug("***************COMPARING Object %s**************************"% objectName)
                            self.parse_xml_file(inputFile, outputFile)
                            logger.debug("********************Comparison End for Object %s"% objectName)
                        else:
                            print("No OutputFile")
        except IOError:
             print("Invalid Audit Directory")
        except Exception as e:
             print("Something went wrong in processing audit directory:")
             print (e)
                                     
    def parse_xml_file(self,srcFileName, dstFileName):
        sourcetree =ET.parse(srcFileName) 
        desttree = ET.parse(dstFileName)
        sourceroot = sourcetree.getroot()
        destroot = desttree.getroot()
        
        print("start comparison file %s"% srcFileName)
        
        for sourcerequest in sourcetree.findall("./request"):
             sourceobject = sourcerequest.find("object")
             source_ident = sourceobject[0].text
             #print("Comparing Identifier %s "% source_ident)
             identifier_found = False
             for destrequest in desttree.findall("./request"):
                destobject= destrequest.find("object")
                dest_ident = destobject.find("identifier").text
                
                print ("dest_ident = %s"%dest_ident)
                if ( source_ident == dest_ident):
                    identifier_found = True
                    self.xml_compare(sourceobject, destobject,source_ident,destobject[0].text)


             if ( identifier_found == False):
                logger.debug( "NO_IDENTIFIER: Idnetifier %r does NOTEXISTS!!" % (source_ident))
    def xml_compare(self,input, output, src_ident,dst_ident, excludes=[]):
       # Removing this print as tags can be present in any order
    #    if input.tag != output.tag:
     #       logger.debug('Tags do not match: %s and %s' % (input.tag, output.tag))
        ichild = input
        ochild = output 
            
        # check if the Element has children, If yes, use DFS to compare the tree recursively.
        cl1 = ichild.getchildren()
        cl2 = ochild.getchildren()
    #    Not required to be reported 
    #    if len(cl1) != len(cl2):
    #        logger.debug('children length differs, %i != %i'
    #                    % (len(cl1), len(cl2)))
          # Check for all the child node for ochild
        if len(cl1) > 0:
          for c1, c2 in zip(cl1, cl2):
              self.xml_compare(c1, c2,src_ident,dst_ident)
    
    
        # run through the child nodes of this object and compare
        for ichild in input:
            ochild_exists = False
            value_match = False
            # check if output tree has same tag
            for ochild in output.findall(ichild.tag):
                ochild_exists = True
                    
                #check for tag attribute match
                for name, value in ichild.attrib.items():
                    if not name in excludes:
                        if ochild.attrib.get(name) != value:
                                logger.debug('Identifier %s'%src_ident)
                                logger.debug('ATTRIBUTE_MISMATCH: Attributes do not match: %s=%r, %s=%r'
                                     % (name, value, name, output.attrib.get(name)))
                 
                # check of identifier values
                if self.text_compare(ichild.text, ochild.text):
                    value_match = True
                #break
            if(ochild_exists == False):
                logger.debug('Identifier %s'%src_ident)
                logger.debug("NO_TAG: Output does not have tag %r" % ichild.tag)
            else:
                if (value_match == False):
                    logger.debug('Identifier %s'%src_ident)
                    logger.debug('VALUE_MISMATCH: %r:%r != %r:%r' % (ichild.tag,ichild.text, ochild.tag,ochild.text))
    

    def text_compare(self,t1, t2):
        if not t1 and not t2:
            return True
        if t1 == '*' or t2 == '*':
            return True
               
        return ((t1 or '').strip()).lower() == ((t2 or '').strip()).lower()
    

if __name__ == '__main__':
    audit_compare_instance  = audit_compare(argv[1])
# Using the class to check
