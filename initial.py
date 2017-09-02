import os
import ast
import hashlib
import time
import userdata

import server
idList={}
path = "/home/"+userdata.username+"/GoogleDrive"
path_hidden = "/home/"+userdata.username+"/.GoogleDrive"

def saveID (mainNode,location):
	global path,idList
	for node in mainNode.link:
		idList[path+location+node.name]=node.id
		if node.md5Checksum == "Folder":
			saveID(node,location+node.name+"/")
	return

def fetchID():
	global path,path_hidden
	mainNode=server.returnRootNode()
	saveID(mainNode,"/")
	idList[path]=mainNode.id
	f=open(path_hidden+"/ids.txt","w")
	f.write(str(idList))
	f.close()
	return

def fetchIDAtSetup():
	global path,path_hidden
	mainNode=server.DownloadAtSetup()
	print "Downloads completed"
	#server.prettyPrint(mainNode,0)
	saveID(mainNode,"/")
	idList[path]=mainNode.id
	f=open(path_hidden+"/ids.txt","w")
	f.write(str(idList))
	f.close()
	return