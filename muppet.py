import sys
import os
import yaml
import pwd
import grp
from pathlib import Path

#Operations supported
func_list = ['write_file','package']

#Arguments Input Check/Usage
def pre_check():
  #check if being executed as sudo/root
  if os.geteuid() != 0:
     exit("You need root permissions run this tool")
  #sys.argv contains arguments which are input in the terminal.
  if (len(sys.argv) != 3) or (str(sys.argv[1]) not in func_list):
     print("""Illegal Arguments
     Usage: sudo puppet.py [operation] [input yaml]
     valid operations:  write_file, package
     input yaml: valid yaml file for appropriate operation""")
     exit()
  else:
     foperation = sys.argv[1]
     ffile = str(sys.argv[2])
     return foperation,ffile; 

#Read yaml files and return values
def read_yaml(filename):
  try:
     yaml_file = open(filename, 'rb')
  except OSError:
     exit("Could not open/read file: ", filename)
  try:
     yaml_content = yaml.safe_load(yaml_file)
  except yaml.YAMLError as exc:
     print(exc)
     exit("Could not load yaml")
  return yaml_content

#Execute File create
def execute_file_create(fileObj):
  filename = fileObj['path']
  #set default userid and groupid
  uid = 0
  gid = 0
  
  try :
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "w") as f:
          f.write(fileObj['content'])
  except OSError as error :
    print(error)
 
  muppet_file = Path(filename)
  if muppet_file.exists():
     #set userid for ownership 
     try:
        uid = pwd.getpwnam(fileObj['owner']).pw_uid
     except KeyError:
        print('User ' + str(fileObj['owner']) + ' for file ' + str(fileObj['path'])  + ' does not exist will not change ownership from default.')
  
     #set groupid
     try:
        gid = grp.getgrnam(fileObj['group'])
     except KeyError:
        print('Group ' + str(fileObj['group']) + ' for file ' + str(fileObj['path'])  + ' does not exist will not change group ID from default.')
 
     #Change ownership
     try: 
        os.chown(filename, uid, gid)  
     except OSError as error : 
        print(error) 
     print("Changed file " + filename + "ownership to uid and gid " + str(uid) + ", " + str(gid))

     perms = fileObj['permissions']
     perms = int(perms,8)
     
     try:
        os.chmod(filename, perms)
        print("Changed file " + filename + " permission to " + oct(perms) )
     except OSError as error :
        print(error) 
         

#Handling for write_file option function for validating yaml keys
def file_create_handler(input_file):
  file_params = ['runcmd','path', 'permissions','group', 'owner', 'content']
  file_create_yaml = read_yaml(input_file[1])
  print(file_create_yaml.keys())
  # pyObj = len(file_create_yaml['write_file'])
  for fileNum in range(len(file_create_yaml['write_file'])):
       for key in file_create_yaml['write_file'][fileNum].keys():
           if key not in file_params:
             exit("parameter for " + key + " for write_file  in " + input_file[1] + " yaml is invalid.Exiting....")
           else:
             break;
       execute_file_create(file_create_yaml['write_file'][fileNum])
              
#package handling
def package_install_handler(input_file):
  print("in package_install()")
  print(input_file)
  read_yaml(input_file[1])

def select_func(check_in):
  if check_in[0] == 'write_file':
     file_create_handler(check_in)
  if check_in[0] == 'package':
     package_install_handler(check_in)


pre_check = pre_check()
select_func(pre_check)
