#!/usr/bin/env python

from pymongo import MongoClient

databasePath = 'mongodb://localhost:27017'

def getNode(module, nodeName):
    
    dbCon = MongoClient( databasePath )
    database = dbCon['mibModules']

    posts = database['mib']
    post = dict(posts.find_one({'moduleName' : module}))
    dbCon.close()

    #TODO SHOULD RETURN DICT
    return post['nodes'][nodeName]


#Recieves a list of dicts where every dict is {"moduleName" : moduleName, "node" : nodeName}
def getNodes(nodeList):
    nodesToTemplate = []
    for d in nodeList:
        node = getNode(d['moduleName'], d['node'])
        node['nodeName'] = d['node']
        nodesToTemplate.append(node)
    return nodesToTemplate

def syntaxParser(syntax):
    syntaxType = syntax['type']
    if 'basetype' in syntaxType.keys():
        return syntaxType['basetype']
    if 'name' in syntaxType.keys():
        return syntaxType['name']
    else:
        return

def createTemplate(name, nodes):
    template = {'templatename' : name}
    objects = []
    #Check for nodekind for error handling
	#TODO THIS IS REALLY IMPORTANT
    for n in nodes:
		if (n['nodetype'] == 'scalar') or (n['nodetype'] == 'column'):
			objectdict = dict()
			objectdict['nodeName'] = str(n['nodeName'])
			objectdict['access'] = str(n['access'])
			objectdict['oid'] = str(n['oid'])
			#TODO Make this import syntaxdefinitions from other mibs
			#At the same time, get rid of unicode u'
			objectdict['syntax'] = syntaxParser(n['syntax'])#str(n['syntax'])
			objects.append(objectdict)
    template['objects'] = objects
    return template


if __name__ == '__main__':
    testDict = dict({'moduleName' : 'IF-MIB', 'node' : 'ifNumber'})
    testList = []
    testList.append(testDict)
    testDict = dict({'moduleName' : 'SNMPv2-MIB', 'node' : 'sysDescr'})
    testList.append(testDict)

    recievednodes = getNodes(testList)
#    for r in recievednodes:
 #       print(r['syntax']['type'])
    temp = createTemplate("TEST", recievednodes)
    print(temp)
