import sys
import os
import subprocess
import shutil

src_path = sys.path[0]+"\\src\\"
print(src_path)
dirList=["src","inputFiles","outputFiles","log"]

for item in dirList:
	source_dir=sys.path[0]+"\\"+item
	destination_dir=sys.path[0]+'\\installer\\nsr\\'+item
	if os.path.isdir(destination_dir):
		print("Deleting "+item)
		shutil.rmtree(destination_dir)
	
	print("copying data from "+ source_dir,destination_dir)
	shutil.copytree(source_dir, destination_dir)
print("modifying config file")
with open(src_path+"\config\config.py") as f:
   newText=f.read().replace("project_path =  os.path.split(src_path)[0]", "project_path =  os.path.split(src_path)[0]\nproject_path =  os.path.split(project_path)[0]")

with open(sys.path[0]+"\\installer\\nsr\\src\config\config.py", "w") as f:
    f.write(newText)
print("modifying main.py file")	
with open(sys.path[0]+"\\main.py") as f:
   oldText=	r'src_path = main_path+"\\src\\"'
   new='src_path = main_path+"\\lib\\src"'
   newText=f.read().replace(oldText,new )

with open(sys.path[0]+"\\installer\\nsr\\main.py", "w") as f:
    f.write(newText)

templateDest= sys.path[0]+'\\installer\\nsr\\templates'
templatesrc=sys.path[0]+'\\installer\\templates'
if os.path.isdir(templateDest):
	shutil.rmtree(templateDest)
print("copying template file from src="+templatesrc +"Dest=  "+templateDest) 		
shutil.copytree(templatesrc,templateDest)

shutil.copy(sys.path[0]+'\\installer\\setup.py',sys.path[0]+'\\installer\\nsr\\setup.py')
#python_path="C:\Users\djyoti\AppData\Local\Programs\Python\Python36"

subprocess.call(['python', sys.path[0]+'\\installer\\nsr\\setup.py', 'build'],cwd=sys.path[0]+'\\installer\\nsr\\')
shutil.make_archive(
  sys.path[0]+'\\installer\\nsr-mapper', 
  'zip',           # the archive format - or tar, bztar, gztar 
  root_dir=sys.path[0]+'\\installer\\nsr\\build\\exe.win-amd64-3.6\\',   # root for archive - current working dir if None
  base_dir=None) 
print("Deleting temporary directory")  
shutil.rmtree(sys.path[0]+'\\installer\\nsr\\')
print("packaging done")  