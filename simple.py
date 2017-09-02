import os
import ast
import hashlib
import datetime
import  initial
import server
import userdata

finalList=None
idList=None
path = "/home/"+userdata.username+"/GoogleDrive"
path_hidden = "/home/"+userdata.username+"/.GoogleDrive"

def getOldList(location):
	f= open(path_hidden+"/old_list.txt","r")
	data=f.read().rstrip('\n')
	f.close()
	if ast.literal_eval(data).get(location) is None:
		return []
	else:
		return ast.literal_eval(data).get(location)

def getNewList(location):
	allFiles=os.listdir(location)
	filelist=[]
	for file in allFiles:
		if os.path.isdir(location+"/"+file):
			filelist=filelist+[[file,"Folder"]]
		else:
			filelist=filelist+[[file,hashlib.md5(open(location+"/"+file, 'rb').read()).hexdigest()]]
	return filelist

def deleteSubtree(location ):
	global idList
	temp=idList.copy()
	for key,value in temp.iteritems():
		if location in key:
			del idList[key]


def checkNode(location):
	global finalList, idList
	list1=getOldList(location)
	list2=getNewList(location)
	
	for file in list1 :
		if file not in list2:
			finalList=finalList+[[None,location+"/"+file[0],idList.get(location+"/"+file[0]),None,"SERVER","DEL"]]
			deleteSubtree(location+"/"+file[0])
			

	for file in list2 :
		if file not in list1:
			finalList=finalList+[[datetime.datetime.utcfromtimestamp(os.path.getmtime(location+"/"+file[0])).isoformat(),location+"/"+file[0],None,idList.get(location),"SERVER","ADD"]]
	
	for file in list1 :
		if file in list2 :
			if os.path.isdir(location+"/"+file[0]):
				checkNode(location+"/"+file[0])
	return

def fetch(location):
	newList=getNewList(location)
	strng="\'"+location+"\'"+":"+str(newList)+","
	for file in newList:
		if file[1] == "Folder":
			strng=strng+fetch(location+"/"+file[0])
	return strng

def updateOldList(location=path):
	f = open(path_hidden + "/old_list.txt","w")
	strn = fetch(location)
	if strn[-1]==",":
		strn=strn[:-1]
	f.write("{"+strn+"}")
	f.close()

def main():
	global finalList,idList,path,path_hidden
	finalList=server.getChanges()

	mainNode=server.returnRootNode()
	server.prettyPrint(mainNode,0)

	f=open(path_hidden+"/ids.txt","r")
	idList=ast.literal_eval(f.read())
	f.close()

	checkNode(path)

	finalList.sort()
	server.doFinalAction(finalList)
	updateOldList()
	initial.fetchID()
	return True
