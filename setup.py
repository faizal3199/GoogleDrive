import server,simple,initial,userdata
import os

#needed files and folders
if not os.path.exists("/home/"+userdata.username+"/GoogleDrive"):
	os.makedirs("/home/"+username+"/GoogleDrive")

if not os.path.exists("/home/"+userdata.username+"/.GoogleDrive"):
	os.makedirs("/home/"+username+"/.GoogleDrive")

#Runs to download all files and saves list locally
initial.fetchIDAtSetup()

#make the old and new lists same for now
simple.updateOldList()