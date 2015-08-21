#!/usr/bin/env python
import sys
from subprocess import call
from operator import itemgetter
import re
from pymongo import MongoClient
from bson.objectid import ObjectId
import imp
from time import time
from datetime import datetime
import databasetool




#TODO split this function to smaller functions
def parseMIB(pathToMIB):
	print("FROM parser:: " + pathToMIB)
        #TODO split this to parsefunction
	with open("MIBdict.py", "w+") as output:
        	#TODO USE THIS EXIT CODE TO HANDLE SEGMENTATION FAULTS	
		exitCode = call(["smidump", "-f", "python", pathToMIB, "-k"], stdout=output)
		print("Exitcode:" + str(exitCode))
	#TODO split this to loadMIB function
	try:
		modf, modfilename, moddescr = imp.find_module("MIBdict")
		try:
			loadedmodule = imp.load_module("MIBdict", modf, modfilename, moddescr)
		finally:
			MIB = loadedmodule.MIB
			modf.close()

	except Exception as ex:	
		ts = time()
		errorString = "{0}\nmodule : {1} crashed\nexception: {2} args: {3}".format(datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'), pathToMIB, type(ex).__name__, ex.args )	
		sys.stderr.write(errorString)
		print( "Aborting parsing on {0}".format(pathToMIB  ))
               #TODO
               #Create real errorhandling
		failedfiles = open("logs/failedmibs.log", "a" )
		failedfiles.write(pathToMIB)
		failedfiles.write('\n')
		failedfiles.close()	
		quit(1)
            

        #TODO Create database module that takes the MIB as argument
	initStr = "Start parsing {0}".format( MIB['moduleName'] )
	print( initStr )
        
        #APPENDING ID
#	MIB['_id'] = ObjectId()
        
        databasetool.insertParsedMib(MIB)
        
	print("Done parsing")

#This is used if module is used as a program..
if __name__ == '__main__':
	#Uses the mib file given as argument with smidump and creates a dictionary from the MIB
	if len(sys.argv) < 2:
		sys.stderr.write("No Mib file given as argument")
		quit()
	else:
            parseMIB(sys.argv[1])
