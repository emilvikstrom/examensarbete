#!/usr/bin/env python
import sys
from subprocess import call
from operator import itemgetter
import re
from pymongo import MongoClient
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

def assembleTree(smidump):
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

