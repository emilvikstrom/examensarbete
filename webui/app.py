import web
from pymongo import MongoClient
import bson.json_util as json
import mibtools
import parseMIB as parser
import mibtemplate
import databasetool

urls = ('/', 'index',
        '/template', 'create_template',
        '/template/all', 'all_templates',
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

#TODO
#This should be moved, and database code shouldn't be handled here, it broke down right before deadline so this is a really stupid fix
def buildModuleTree():
    retString = "<div id='jstree'><ul>"
    for post in databasetool.getAllModules():
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
        web.debug(treeString)
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
        parser.parseMIB("./upload/"+filename)
        raise web.seeother('')

#Not sure if database should return json or the conversion should be here
class list_modules:
    def GET(self):
        return databasetool.getAllModuleNames()

class get_module:
    def GET(self, module):
        return databasetool.getModule(module)

class list_nodes:
    def GET(self, module):
        return databasetool.getModuleAllNodes(module)

class get_node:
    def GET(self, module, node):
        return databasetool.getNodeFromModule(module, node)

class all_templates:
    def GET(self):
        return databasetool.getAllTemplates()

class create_template:
    def GET(self):
        i = web.input()
        nodes = json.loads(i['jsonField'])
        templatename = i['templatename']
        recievednodes = mibtemplate.getNodes(nodes)
        template = mibtemplate.createTemplate(templatename, recievednodes)
        previewtemplate = json.dumps(template)
        web.debug(previewtemplate)
        return render.preview(previewtemplate)

    def POST(self):
        i = web.input()
        incoming = i.dataToSave
        template = json.loads(incoming)
        databasetool.insertTemplate(template)
        return template

if __name__ == '__main__':
    app.run()
