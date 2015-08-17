#!/usr/bin/env python
from pymongo import MongoClient
from bson.objectid import ObjectId
#import json
import bson.json_util as json
def insertParsedMib(MIB):
	databasePath = 'mongodb://localhost:27017'
	dbCon = MongoClient( databasePath )
	database = dbCon['mibModules']
	collection = database['mib']
	MIB['_id'] = ObjectId()
	posts = database.posts
	collection.insert_one(MIB)
	dbCon.close()

def getAllModuleNames():
	databasePath = 'mongodb://localhost:27017'
	dbCon = MongoClient( databasePath )
	database = dbCon['mibModules']

	posts = database['mib']
	#posts = database.posts
	output = str()
	i = 0
	for post in posts.find():
		output += '{\'id\' : ' + str(i) + ',\'moduleName\' : \'' +   post['moduleName']  + '\'}'
		i += 1
	dbCon.close()
	return output

def getAllModules():
    databasePath = 'mongodb://localhost:27017'
    dbCon = MongoClient( databasePath )
    database = dbCon['mibModules']
    posts = database['mib']
    output = posts.find()
    dbCon.close()
    return output

def getModule(module):
	databasePath = 'mongodb://localhost:27017'
	dbCon = MongoClient( databasePath )
	database = dbCon['mibModules']
	posts = database['mib']

	post = dict(posts.find_one({'moduleName' : module}))
	output = json.dumps(post)
	dbCon.close()
	return output

def getModuleAllNodes(module):
	databasePath = 'mongodb://localhost:27017'
	dbCon = MongoClient( databasePath )
	database = dbCon['mibModules']
	posts = database['mib']
	post = dict(posts.find_one({'moduleName' : module}))
	return json.dumps(post['nodes'].keys())

def getNodeFromModule(module, node):
	databasePath = 'mongodb://localhost:27017'
	dbCon = MongoClient( databasePath )
	database = dbCon['mibModules']
	posts = database['mib']
	post = dict(posts.find_one({'moduleName' : module}))
	retNode = post['nodes'][node]
	return json.dumps(post['nodes'][node])

def insertTemplate(template):
	databasePath = 'mongodb://localhost:27017'
	dbCon = MongoClient( databasePath )
	database = dbCon['allTemplates']
	collection = database['template']
	template['_id'] = ObjectId()
	collection.insert_one(template)
	dbCon.close()

def getAllTemplates():
	databasePath = 'mongodb://localhost:27017'
	dbCon = MongoClient( databasePath )
	database = dbCon['allTemplates']
	posts = database['template']
	retList = []
	for post in posts.find():
		retList.append(post)
	return json.dumps(retList)
