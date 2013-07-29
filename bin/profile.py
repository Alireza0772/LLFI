#!/usr/bin/python

#This script profiles the program to produce llfi.stat.prof.txt

#The prof.ll.exe eds to be executed in the src directory 

#This should be run right after create-executables.py is run to provide
#up-to-date llfi.stat.prof.txt 

#basedir is actually the src directory with  c file(s)
#curdir is where the compilation files and executables will be stored

#To run this, please change optbin,llcbin,llvmgcc,llfilib, and llfilinklib to match your system, 
#and also change sys.path.append() to a path that points to your local Pyyaml library

import sys
sys.path.append('/ubc/ece/home/kp/ugrads/v7c7/lib/python/')
import yaml
import os
import re
import getopt
import time
import random
import signal
import subprocess
import shutil
import random

optbin = "/data/llvm-2.9/Debug+Asserts/bin/opt"
llcbin = "/data/llvm-2.9/Debug+Asserts/bin/llc"
llvmgcc = "/data/llvm-gcc/bin/llvm-gcc"
llfilib = "/data/llvm-2.9/Release/lib/LLFI.so"
llfilinklib = "/data/LLFI-experimental-master/lib"

optionlist = []
timeout = 500

basedir = os.getcwd()
#Check for input.yaml's presence
try:
	f = open(basedir+'/input.yaml','r')
except:
	print "ERROR. No input.yaml file in the current directory."
	exit(1)


#Check for input.yaml's correct formmating
try:
	doc = yaml.load(f)
	f.close()
except:
	print "Error. input.yaml is not formatted in proper YAML (reminder: use spaces, not tabs)"
	exit(1)

#Check for compileOption in input.yaml
try:
	cOpt = doc["compileOption"]
except:
	print "ERROR in input.yaml. Please include compileOptions."
	exit(1)

#Just a little tweak to make the output look less clustered
print "\n"	

################################################################################
def config():
	global inputProg,progbin,inputdir,outputdir,basedir,errordir,currdir
	# config
	currdir = basedir + "/"+inputProg
	progbin = currdir + "/"+inputProg

	inputdir = currdir + "/prog_input"
	outputdir = currdir + "/prog_output"
	basedir = currdir + "/baseline"
	errordir = currdir + "/error_output"

	if not os.path.isdir(currdir):
		os.mkdir(currdir)
	if not os.path.isdir(outputdir):
		os.mkdir(outputdir)
	if not os.path.isdir(basedir):
		os.mkdir(basedir)
	if not os.path.isdir(errordir):
		os.mkdir(errordir)
	if not os.path.isdir(inputdir):
		os.mkdir(inputdir)

################################################################################
def execute( execlist):
	#print "Begin"
	#inputFile = open(inputfile, "r")
  global outputfile
  print ' '.join(execlist)
  #get state of directory
  dirSnapshot()
  p = subprocess.Popen(execlist, stdout = subprocess.PIPE)
  elapsetime = 0
  while (elapsetime < timeout):
    elapsetime += 1
    time.sleep(1)
    #print p.poll()
    if p.poll() is not None:
      moveOutput()
      print "\t program finish", p.returncode
      print "\t time taken", elapsetime,"\n"
      outputFile = open(outputfile, "w")
      outputFile.write(p.communicate()[0])
      outputFile.close()
      replenishInput() #for cases where program deletes input or alters them each run
      #inputFile.close()
      return str(p.returncode)
  #inputFile.close()
  print "\tParent : Child timed out. Cleaning up ... " 
  p.kill()
  return "timed-out"
	#should never go here	
  sys.exit(syscode)

################################################################################
def storeInputFiles():
	global inputList
	inputList=[]
	for opt in optionlist:
		if os.path.isfile(opt):#stores all files in inputList and copy over to inputdir
			shutil.copy2(opt, inputdir+'/'+opt)
			inputList.append(opt)

################################################################################
def replenishInput():#TODO make condition to skip this if input is present
	for each in inputList:
		if not os.path.isfile(each):#copy deleted inputfiles back to basedir
			shutil.copy2(inputdir+'/'+each,each)

################################################################################
def moveOutput():
	#move all newly created files that are not "llfi.stat.prof.txt" < -- since this is a product of profiling
	for each in[file for file in os.listdir(".")]:
		if each not in dirBefore and each !="llfi.stat.prof.txt":
			fileSize = os.stat(each).st_size
			if fileSize == 0 and each.startswith("llfi"):
				#empty library output, can delete
				print each+ " is going to be deleted for having size of " + str(fileSize)
				os.remove(each)
			else:
				flds = each.split(".")
				newName = '.'.join(flds[0:-1])
				newName+='.prof.'+flds[-1]
				os.rename(each,outputdir+'/'+newName)

################################################################################
def dirSnapshot():
	#snapshot of directory before each execute() is performed
	global dirBefore
	dirBefore=[]
	for each in[file for file in os.listdir(".")]:
		dirBefore.append(each)

################################################################################
def main():
	global optionlist, outputfile

	config()
	inputllfile = currdir +"/"+llfile
	#proffile is the profiling executable that has the same name as inputllfile
	proffile = currdir+"/"+llfile[:-3]+"-prof.ll.exe" # -3 to omit the .ll


	if not os.path.isfile(inputllfile):
		print "Error. Cannot find the IR file - "+inputllfile
		print "Please try running compile-IR.py. Or build the IR file yourself.\n"
		exit(1)

	storeInputFiles()
	# baseline
	outputfile = basedir + "/golden_output"
	execlist = [proffile]
	execlist.extend(optionlist)
	run_id=''#execute requires run_id to be defined
	
	if not os.path.isfile(proffile):
		print "Error. The executable "+ proffile+" does not exist."
		print "Please build the executables with create-executables.py.\n"
		exit(1)
	else:
		print "======Profiling======"
		execute(execlist)


################################################################################

if __name__=="__main__":
  global inputProg, initTime, llfile
  assert len(sys.argv) > 1, 'Error. Must provide an argument to specify the IR file to inject into. (ie. python inject.py daxpy.ll'
  initTime= time.time()
  try:
    inputProg = doc["setUp"]["targetDirectoryName"]#the name of input program
  except:
    print "ERROR, Please include a targetDirectoryName field in input.yaml. See ReadMe for directions."
    exit(1)

  for ii,arg in enumerate(sys.argv):
    if ii==1:
	  llfile = arg
    if ii>1: #add all commandline arguments to optionlist except the first two which are the this script's name, and the IR file name
      optionlist.append(arg)

  main()