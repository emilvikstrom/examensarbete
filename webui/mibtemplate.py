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
    print(post['nodes'][nodeName])



#Recieves a list of dicts where every dict is {"moduleName" : moduleName, "node" : nodeName}
def getNodes(nodeList):
    for d in nodeList:
        getNode(d['moduleName'], d['node'])




if __name__ == '__main__':
    testDict = dict({'moduleName' : 'IF-MIB', 'node' : 'ifNumber'})
    testList = []
    testList.append(testDict)
    testDict = dict({'moduleName' : 'SNMPv2-MIB', 'node' : 'sysDescr'})
    testList.append(testDict)


    getNodes(testList)

