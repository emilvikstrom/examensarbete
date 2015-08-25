#!/usr/bin/env python
import sys
from subprocess import call
from operator import itemgetter
import re
from pymongo import MongoClient
import time
from datetime import datetime
import databasetool
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

    startTime = time.clock()

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

    stopTime = time.clock()
    #print("ON {} s ".format(stopTime - startTime))
    return retList

def assembleTree(smidump):
    startTime = time.clock()

    moduleDict = dict( [ ('module', smidump[ 'moduleName' ] ) ] )
    if 'imports' in smidump.keys():
        moduleDict['imports'] = smidump['imports']

    if 'typedefs' in smidump.keys():
        moduleDict['typedefs'] = smidump['typedefs']

    if 'nodes' in smidump.keys():
		tmp = createNodelist(smidump['nodes'])
		nodetree = organizeNodes(tmp)
		moduleDict['nodes'] = nodetree
    stopTime = time.clock()
    #print("AT {} s ".format(stopTime - startTime))
    return moduleDict

def buildNodeTree(treestring, nodes):
    startTime = time.clock()
    retString = treestring
    retString.append( '<ul>' )
    for n in nodes:
        retString.append( '<li id="')
        retString.append(str(n['name']))
        retString.append( '" class="node" data-root="')
        retString.append(n['moduleName'])
        retString.append('">')
        retString.append(str(n['name']))
        if n['nodes']:
            retString = buildNodeTree(retString, n['nodes'])
        retString.append( "</li>" )
    retString.append( '</ul>' )
    stopTime = time.clock()
    #print("BNT {} s ".format(stopTime - startTime))
    return retString

def buildModuleTree():
    startTime = time.clock()
    retString = []
    retString.append("<div id='jstree'><ul>")
    for post in databasetool.getAllModules():
#        module = mibtools.assembleTree(post)

        module = assembleTree(post)
        retString.append('<li id="')
        retString.append(module['module'])
        retString.append( '" class="module">' )
        retString.append( module['module'] )
        if 'nodes' in module.keys():
            nodes = module['nodes']
            retString = buildNodeTree(retString, nodes)
        retString.append( '</li>')
    retString.append( '</ul>' )
    stopTime = time.clock()
    print("BMT {} s ".format(stopTime - startTime))
    return ''.join(retString)

if __name__ == '__main__':
    buildModuleTree()
