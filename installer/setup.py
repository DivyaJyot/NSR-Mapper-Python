from cx_Freeze import setup, Executable
import os
# NOTE: you can include any other necessary external imports here aswell
 
includefiles = ["inputFiles","outputFiles","log","templates"] # include any files here that you wish
includes = ["src"]
excludes = []
packages = ["src","numpy"]
 
# exe = Executable(
 # # what to build
   # script = "main.py", # the name of your main python script goes here 
   # initScript = None,
   # base = None, # if creating a GUI instead of a console app, type "Win32GUI"
   # targetName = "sdm mapper.exe", # this is the name of the executable file
   # #copyDependentFiles = True,
   # #compress = True,
   # #appendScriptToExe = True,
   # #appendScriptToLibrary = True
   # #icon = None # if you want to use an icon file, specify the file name here
# )
 
setup(
 # the actual setup & the definition of other misc. info
    name = "SDM Mapper", # program name
    version = "0.1",
    description = 'A general enhancement utility',
    #author = "Divya Jyoti",
    #author_email = "divya.jyoti@nokia.com",
    options = {"build_exe": {"excludes":excludes,"packages":packages,
      "include_files":includefiles}},
    executables = [Executable("main.py",base="console"),Executable("GenerateSPMLQuery.py",base="console"),Executable("xmlcompare.py",base="console")]
)
# http://programmingnotes.org/