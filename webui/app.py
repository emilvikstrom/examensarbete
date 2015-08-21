import web

from pymongo import MongoClient
import bson.json_util as json
import mibtools
import parseMIB as parser
import mibtemplate

databasePath = 'mongodb://localhost:27017'
dbCon = MongoClient( databasePath )
database = dbCon['mibModules']

posts = database['mib']
#collection = database['mib']
#posts = database.posts


#TODO Create views for errors


urls = ('/', 'index',
        '/template', 'create_template',
        '/modules', 'list_modules',

        '/modules/(.*)', 'get_module',

        '/nodes/(.*?)/(.*?)', 'get_node',
        '/nodes/(.*)', 'list_nodes' 


        )
render = web.template.render('templates/')

app  = web.application(urls, globals())

def buildNodeTree(treestring, nodes):
    retString = treestring
    retString += '<ul>'
    
    for n in nodes:
        retString += '<li id="' + str(n['name']) + '" class="node" data-root="' + n['moduleName'] + '">' + str(n['name'])
        if n['nodes']:
            retString = buildNodeTree(retString, n['nodes'])
        retString += "</li>"


    retString += '</ul>'

    return retString

def buildModuleTree():
    retString = "<div id='jstree'><ul>"

    for post in posts.find():
        module = mibtools.assembleTree(post)
        retString += '<li id="' + module['module'] +'" class="module">'
        retString += module['module']
        nodes = module['nodes']
        retString = buildNodeTree(retString, nodes)

        retString += '</li>'
    

    retString += '</ul>'
    return retString


class index:
    def GET(self):
        treeString = buildModuleTree()        
        return render.index(treeString)

    def POST(self):
        incoming = web.input(myfile={})
        web.debug(incoming['myfile'].filename)
        filename = incoming['myfile'].filename
        filecontent = incoming['myfile'].value
        with open("./upload/"+filename, 'w') as mibfile:
            mibfile.write(filecontent)
            mibfile.close()


        #TODO som real errorhandling
        #let parseMIB return an errorcode and redirect to relevant page
        print("DEBUG:: parsing file: " + filename)
        parser.parseMIB("./upload/"+filename)
        raise web.seeother('')

class list_modules:
    def GET(self):
        output = str()
        i = 0
        for post in posts.find():
            output += '{\'id\' : ' + str(i) + ',\'moduleName\' : \'' +   post['moduleName']  + '\'}'
            i += 1
        return output

class get_module:
    def GET(self, module):
        output = str()
        i = 0
        post = dict(posts.find_one({'moduleName' : module}))
        return json.dumps(post) 

class list_nodes:
    def GET(self, module):
        post = dict(posts.find_one({'moduleName' : module}))
        i = 0
        return json.dumps(post['nodes'].keys())

class get_node:
    def GET(self, module, node):

        post = dict(posts.find_one({'moduleName' : module}))
        retNode = post['nodes'][node]
        return json.dumps(post['nodes'][node])

class create_template:
    def GET(self):
        return "You can only post to this"

    def POST(self):
        data = web.data()
        incoming = json.loads(data)
        templateName = incoming['templateName']
        recievednodes = mibtemplate.getNodes(incoming['nodes'])
        web.debug(recievednodes)
        web.debug("DONEDONEDONEDONEDONE")
        template = mibtemplate.createTemplate(templateName, recievednodes)
        web.debug(template)
        raise web.seeother('')

if __name__ == '__main__':
    app.run()
