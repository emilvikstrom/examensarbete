#!/usr/bin/env python
import sys
from subprocess import call
#import re
from pymongo import MongoClient
from bson.objectid import ObjectId
import imp
from time import time
from datetime import datetime
import databasetool
import os

class ParseException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class LoadException(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def parseMIB(path):
    with open("MIBdict.py", "w+") as output:
        with open("logs/parserlog.log", "a+") as error:
    	#TODO USE THIS EXIT CODE TO HANDLE SEGMENTATION FAULTS	
       	    exitCode = call(["smidump", "-f", "python", path, "-k"], stdout=output, stderr=error)
    if exitCode > 0:
        raise Exception("Something went wrong in the parsing file: {1}".format(path))
    return exitCode


def logError(fileToWrite, error, mibname):
    with open(fileToWrite, 'a+') as f:
        ts = time()
        errTime = datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')
        errString = [errTime, str(error), " in ", mibname, '\n' ]
        f.write(''.join(errString))


def loadLatestParsedMIB():
    MIB = None
    loadedmodule = None
    modf, modfilename, moddescr = None, None, None
    try:
    	modf, modfilename, moddescr = imp.find_module("MIBdict")
    	try:
    	    loadedmodule = imp.load_module("MIBdict", modf, modfilename, moddescr)
        except:
            raise LoadException("Something went wrong with loading module")
        finally:
            MIB = loadedmodule.MIB
#            print(MIB['moduleName'])
            modf.close()
            return MIB
    
    except Exception as ex:
#        print(ex)
        raise Exception("Error in loading: " + str(ex))
#    	ts = time()
#    	errorString = "{0}\nmodule : {1} crashed\nexception: {2} args: {3}".format(datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'), pathToMIB, type(ex).__name__, ex.args )	
#    	sys.stderr.write(errorString)
#    	failedfiles = open("logs/failedmibs.log", "a" )
#    	failedfiles.write(pathToMIB)
#    	failedfiles.write('\n')
#    	failedfiles.close()
#    	quit(1)

def runparser(pathToMIB):
    initStr = "Start parsing {0}".format( pathToMIB )
    MIB = None
#    print( initStr )
    try:
         parseMIB(pathToMIB)
    except Exception as ex:
        #TODO save the exception time, name of module, change time to a+, maybe create a function that handles this
        print(ex)
        logError("logs/parser.log", ex, pathToMIB)
#        errorToLog = []
#        ts = time()
#        errorToLog.append(datetime.fromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S'))
#        errorToLog.append('\n')
#        errorToLog.append(ex)
#        with open("logs/failedmibs.log", "a" ) as f:
#            f.write(errorToLog.join())
    try:
        MIB = loadLatestParsedMIB()
        if MIB:
            databasetool.insertParsedMib(MIB)
        else:
            raise Exception("No module loaded")
    except Exception as ex:
        #TODO write to file and add print to what file that was parsed at the momemt
        print(ex)
        logError("logs/loadmodule.log", ex, pathToMIB)


    os.remove("MIBdict.py")
#    print("Done parsing")

#This is used if module is used as a program..
if __name__ == '__main__':
    #Uses the mib file given as argument with smidump and creates a dictionary from the MIB
    if len(sys.argv) < 2:
    	sys.stderr.write("No Mib file given as argument")
    	quit()
    else:
        runparser(sys.argv[1])
