import sys
import os
import yaml
import pwd
import subprocess
import grp
import ast
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


def call_runcmd(artifactObj):
    print(artifactObj['runcmd'])
    try:
      runcmd_ver = artifactObj['runcmd']
      print("executing runcmd: "  + runcmd_ver)
      runcmd_res = subprocess.Popen(runcmd_ver,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);
      runcmd_out,error = runcmd_res.communicate()
      if runcmd_out:
          print(runcmd_out)
      if error:
          print("Error> error " + str(error.strip()))
    except OSError as e:
      print("OSError > " + str(e.errno))
      print("OSError > " + str(e.strerror))
      print("OSError > " + str(e.filename))
      exit()
    except:
      print("Error > " + str(sys.exc_info()[0]))
      exit()


#Execute File create
def execute_file_create(fileObj):
  filename = fileObj['path']
  #set default userid and groupid
  uid = 0
  gid = 0
  try :
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    print("Writing file: " + filename )
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
     print("Changed file " + filename + " ownership to uid and gid " + str(uid) + ", " + str(gid))

     perms = fileObj['permissions']
     perms = int(perms,8)
     
     try:
        os.chmod(filename, perms)
        print("Changed file " + filename + " permission to " + oct(perms) )
     except OSError as error :
        print(error) 

def check_package_avail(packObj):
    package_name = packObj['name']
    package_version = packObj['version']
    try:
        apt_cache_ver = "apt-cache show " + package_name + "|grep Version|uniq|awk '{print $2}'"
        apt_cache_res = subprocess.Popen(apt_cache_ver,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);
        apt_cache_out,error = apt_cache_res.communicate()
        pkg_list_avail = apt_cache_out.decode("UTF-8").strip().split('\n')
        if (package_version in pkg_list_avail):
            print("Package " +  package_name + ":" + package_version + " is available")
            return True
        else:
            print("Package " +  package_name + ":" + package_version + " is not available")
            return False
    except OSError as e:
      print("OSError > " + str(e.errno))
      print("OSError > " + str(e.strerror))
      print("OSError > " + str(e.filename))
      exit()
    except:
      print("Error > " + str(sys.exc_info()[0]))
      exit()

def check_package_installed(packObj):
    package_name = packObj['name']
    package_version = packObj['version']
    try:
      dpkg_query = "dpkg-query -W '-f={\"name\":\"${package}\", \"version\":\"${version}\", \"status\":\"${status}\"}'" 
      dpkg_ver = dpkg_query + " " + package_name
      print(dpkg_ver)
      print("Checking if package is installed: " + package_name + ":" + package_version)
      dpkg_res = subprocess.Popen(dpkg_ver,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);
      dpkg_out,error = dpkg_res.communicate()
      if dpkg_out:
          install_status = ast.literal_eval(dpkg_out.decode("UTF-8"))
          if(install_status.get('status') == 'install ok installed' and install_status.get('version') == packObj['version']):
              print("Package: " + package_name + ":" + package_version + " status " + install_status.get('status'))
              return True 
          else:
              print("Package: " + package_name + ":" + package_version + " status " + install_status.get('status'))
              return False
      else:
          print("Package: " + package_name + ":" + package_version + " status " + str(error.strip()))
          return False
      if error:
          print("Error> error " + str(error.strip()))
    except OSError as e:
      print("OSError > " + str(e.errno))
      print("OSError > " + str(e.strerror))
      print("OSError > " + str(e.filename))
      exit()
    except:
      print("Error > " + str(sys.exc_info()[0]))
      exit()

def manage_package(packObj):
    print("In Manage package")
    package_name = packObj['name']
    package_version = packObj['version']
    package_action = packObj['action']
    
    try:
      apt_query = "apt-get " + package_action + " -y"
      apt_ver = apt_query + " " + package_name + "=" + package_version
      print(apt_ver)
      print("Performing action " + package_action  + " for  package: " + package_name + ":" + package_version)
      apt_res = subprocess.Popen(apt_ver,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE);
      apt_out,error = apt_res.communicate()
      if apt_out:
          print(apt_out)
          print("Action " + package_action  + " successful for  package: " + package_name + ":" + package_version)
      if error:
          print("Error> error " + str(error.strip()))
    except OSError as e:
      print("OSError > " + str(e.errno))
      print("OSError > " + str(e.strerror))
      print("OSError > " + str(e.filename))
      exit()
    except:
      print("Error > " + str(sys.exc_info()[0]))
      exit()


def execute_package_manager(packObj):
    print(type(packObj['action']))
    print((packObj['action']))
    action = str(packObj['action'])
    if not (action == 'install' or action == 'remove' or action == 'purge'):
        print("Unknown action " + packObj['action'] + " for package " + packObj['name']  )
    elif (action == 'install'):
        print("in install condition for " + packObj['name'])
        check_available = check_package_avail(packObj)
        package_status = check_package_installed(packObj)
        if (package_status == False) and (check_available == True):
            manage_package(packObj)
            print("runcmd: " + packObj['action'] + " will execute as package is installed" )
            call_runcmd(packObj)
        else:
            print("Nothing to do for package " + packObj['name'])
            print("runcmd: " + packObj['action'] + " will not be executed as package is not installed" )
    elif (packObj['action'] == 'remove' or packObj['action'] == 'purge'):
        package_status = check_package_installed(packObj)
        if (package_status == True):
            manage_package(packObj)
            print("runcmd: " + packObj['action'] + " will not be executed as it is package removal" )
        else:
            print("Nothing to do for package " + packObj['name'])

#Handling for write_file option function for validating yaml keys
def file_create_handler(input_file):
  file_params = ['runcmd','path', 'permissions','group', 'owner', 'content']
  file_create_yaml = read_yaml(input_file[1])
  # print(file_create_yaml.keys())
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
  #print("in package_install()")
  pack_params = ['runcmd','name', 'action','version']
  print(input_file)
  package_install_yaml = read_yaml(input_file[1])
  print(package_install_yaml.keys())
  for packNum in range(len(package_install_yaml['package'])):
    # print(package_install_yaml['package'][packNum])
     for key in package_install_yaml['package'][packNum].keys():
         for key in package_install_yaml['package'][packNum].keys():
           if key not in pack_params:
             exit("parameter for " + key + " for package  in " + input_file[1] + " yaml is invalid.Exiting....")
           else:
             break;
     execute_package_manager(package_install_yaml['package'][packNum])
 
def select_func(check_in):
  if check_in[0] == 'write_file':
     file_create_handler(check_in)
  if check_in[0] == 'package':
     package_install_handler(check_in)

pre_check = pre_check()
select_func(pre_check)
