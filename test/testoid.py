from pymongo import MongoClient
import bson.json_util as json
import databasetool
import sys


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("No temlplate id given")
        quit(1)
    template = databasetool.getTemplate(sys.argv[1])
    if template != None:
        obj = template['objects']
        with open("oid.txt", "w") as oidfile:
            for o in obj:
                oidfile.write(o['oid'] + "\n")
            print("Saved found OID to oid.txt")
    else:
        print("No template")
            

