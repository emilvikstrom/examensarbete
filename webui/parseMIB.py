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
databasePath = 'mongodb://localhost:27017'

def atoi(text):
	return int(text) if text.isdigit() else text

def natural_keys(text):
	'''
	alist.sort(key=natural_keys) sorts in human order
	http://nedbatchelder.com/blog/200712/human_sorting.html
	(See Toothy's implementation in the comments)
	'''
	return [ atoi(c) for c in re.split('(\d+)', text) ]



'''
Takes a MIB dictionary from SMIdump and returns all nodes as a list sorted by OID
'''

def createNodelist(nodes):
	nodelist = [ nodes[n] for n in nodes.keys() ]

	#THIS ONLY WORKS IF NODE KEYS ALWAYS PRINTED IN THE SAME ORDER..		
	#And it seems to work
	#p3 .items == .iteritems	p2
	for key, value in nodes.items():
		for listelement in nodelist:
			if listelement == value:
				listelement['name'] = key
	#Sort by OID	
	nodelist.sort(key=lambda k: natural_keys(k['oid']))
        return nodelist

def parentOid(oid):
    #Regex for splitting oid on .
    oidlist = re.split(r'[.](?![^][]*\])', oid)
    #Remove last element
    oidlist.pop()
    blaha = '.'.join( oidlist)
    return blaha	

def oidlen(oid):
    oidlist = re.split(r'[.](?![^][]*\])', oid)
    return len(oidlist)

def organizeNodes(sortedNodelist):
    nodequeue = list(sortedNodelist)
    allNodes = list(sortedNodelist)
    retList = list()
    if not nodequeue:
        return
    while nodequeue:
        parentCandidate = nodequeue.pop(0)
        childnodes = []
        for n in nodequeue:
            #Hmm, need to handle this so that it thinks 1.3.5.2 is a subid of 1.3.5.22
            if ( parentCandidate['oid'] in n['oid'] ) and (oidlen(parentCandidate['oid']) < oidlen(n['oid'] ) ) :
                childnodes.append(n)
              
        for n in childnodes:
            nodequeue.remove(n)
        childnodes = organizeNodes(childnodes)

        parentCandidate['nodes'] = childnodes
        retList.append(parentCandidate)

    return retList

def assembleDictionary(smidump):
    moduleDict = dict( [ ('module', smidump[ 'moduleName' ] ) ] )
    if 'imports' in smidump.keys():
        moduleDict['imports'] = smidump['imports']

    if 'typedefs' in smidump.keys():
        moduleDict['typedefs'] = smidump['typedefs']

    if 'nodes' in smidump.keys():
        tmp = createNodelist(smidump['nodes'])
        nodetree = organizeNodes(tmp)
        moduleDict['nodes'] = nodetree

    return moduleDict



def parseMIB(pathToMIB):
	print("FROM parser:: " + pathToMIB)
	with open("MIBdict.py", "w+") as output:
        	#TODO USE THIS EXIT CODE TO HANDLE SEGMENTATION FAULTS	
		exitCode = call(["smidump", "-f", "python", pathToMIB, "-k"], stdout=output)
		print("Exitcode:" + str(exitCode))
	
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
            


	initStr = "Start parsing {0}".format( MIB['moduleName'] )
	print( initStr )
        
        #APPENDING ID
	MIB['_id'] = ObjectId()

#        module = assembleDictionary(MIB)
	dbCon = MongoClient( databasePath )
	database = dbCon['mibModules']
        #TODO ERROR HANDLING
	#Observera dessa rader, jag kan alltslga varje mib som en egen collection?? 
	collection = database['mib']
	posts = database.posts
	#post_id = collection.insert_one(module).inserted_id

	#post_id = collection.insert_one(MIB).inserted_id

	collection.insert_one(MIB)
	dbCon.close()
	print("Done parsing")

#This is used if module is used as a program..
if __name__ == '__main__':
	#Uses the mib file given as argument with smidump and creates a dictionary from the MIB
	if len(sys.argv) < 2:
		sys.stderr.write("No Mib file given as argument")
		quit()
	else:
            parseMIB(sys.argv[1])
