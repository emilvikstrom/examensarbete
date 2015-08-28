import web
from pymongo import MongoClient
import bson.json_util as json
import mibtools
import parseMIB as parser
import mibtemplate
import databasetool
import time

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

class index:
    def GET(self):
        treeString = mibtools.buildModuleTree()

#       web.debug(treeString)
#        treeString = mibtools.htmlTree()
        return render.index(treeString)

    def POST(self):
        incoming = web.input(myfile={})
#        web.debug(incoming['myfile'].filename)
        filename = incoming['myfile'].filename
        filecontent = incoming['myfile'].value
        with open("./upload/"+filename, 'w') as mibfile:
            mibfile.write(filecontent)
            mibfile.close()
        #TODO som real errorhandling
        #let parseMIB return an errorcode and redirect to relevant page
        parser.runparser("./upload/"+filename)
#        treestring = buildModuleTree()
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
#        web.debug(previewtemplate)
        return render.preview(previewtemplate)

    def POST(self):
        i = web.input()
        incoming = i.dataToSave
        template = json.loads(incoming)
        databasetool.insertTemplate(template)
        return template

if __name__ == '__main__':
    app.run()
