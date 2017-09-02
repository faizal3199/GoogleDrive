import auth
import httplib2
import os
import io
import datetime
import userdata

from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from apiclient.http import MediaIoBaseDownload
from apiclient.http import MediaFileUpload

class Node(object):
    def __init__(self,id,name,md5Checksum,mimeType):
        super(Node, self).__init__()
        self.id = id
        self.name = name
        self.md5Checksum = md5Checksum
        self.mimeType = mimeType
        self.link=None
service = None
DOWNLOAD_PATH_PREFIX = '/home/'+userdata.username+'/GoogleDrive'
path_hidden = "/home/"+userdata.username+"/.GoogleDrive"
MIME_FOLDER = 'application/vnd.google-apps.folder'

def setService():
    global service

    credentials = auth.get_credentials()
    http = credentials.authorize(httplib2.Http())
    service = discovery.build('drive', 'v3', http=http)

    return True

def initlastTime():
    global path_hidden
    try:
        file = open(path_hidden+'/lastTime.data','w')
        file.write(datetime.datetime.utcnow().isoformat())
        file.close()
        return True
    except :
        print "Can't write file lastTime.data "
    return False

def getChanges():
    global DOWNLOAD_PATH_PREFIX,path_hidden

    newData = []
    
    try:
        file = open(path_hidden+'/lastTime.data','r')
        lastTime = file.read().rstrip('\n')
        file.close()
    except :
        print "Can't read last time"
        return False

    search = "trashed=true or modifiedTime>'"+lastTime+"'"
    results = service.files().list(q=search,fields="nextPageToken, files(id,name,mimeType,trashed,parents,createdTime,modifiedTime)").execute()
    
    newData = newData+results.get('files',[])
    try:
        newPageToken = results.get('nextPageToken')
    except KerError:
        newPageToken = None
    while newPageToken:
        results = service.files().list(q=search,pageToken=newPageToken,fields='nextPageToken, files(id,name,mimeType,trashed,parents,createdTime,modifiedTime)').execute()
        newData = newData+results.get('files',[])

    
    with open(path_hidden+'/lastTime.data','w') as file:
        file.write(datetime.datetime.utcnow().isoformat())

    return parseNewData(newData)

def parseNewData(newData):
    global DOWNLOAD_PATH_PREFIX,path_hidden
    parsedData = []
    for file in newData:
        if file['trashed']:#1-Add and 0-del
            parsedData = parsedData +[[file['modifiedTime']]+[DOWNLOAD_PATH_PREFIX+getFullPath(file['id'])]+[file['id']]+[file['parents'][0]]+["LOCAL"]+["DEL"]]
        else:
            parsedData = parsedData +[[file['modifiedTime']]+[DOWNLOAD_PATH_PREFIX+getFullPath(file['id'])]+[file['id']]+[file['parents'][0]]+["LOCAL"]+["ADD"]]
    print "Comamnds From Server:"
    print parsedData
    return parsedData

def uploadFile(fileURI,parentID):
    if not parentID:
        parentID = 'root'
    if os.path.isdir(fileURI):
        name = fileURI.split("/")[-1]
        file_metadata = { 'name' : name, 'parents':[parentID], 'mimeType':MIME_FOLDER }
        results = service.files().create(body=file_metadata,fields='id').execute()

        list = os.listdir(fileURI)
        for file in list:
            uploadFile(fileURI+"/"+file,results.get('id'))

    else:
        name = fileURI.split("/")[-1]
        file_metadata = { 'name' : name, 'parents':[parentID] }
        media = MediaFileUpload(fileURI)
        results = service.files().create(body=file_metadata,media_body=media,fields='id').execute()
        print 'File ID: %s' % results.get('id')

def changeName(fileId,new_name):
    file_metadata = {'name' : new_name}
    results = service.files().update(fileId=fileId,body=file_metadata,fields='id, name, mimeType').execute()
    print results.get('name')
    return

def getFullPath(fileId):
    #return full path relative to foot using recursion
    results = service.files().get(fileId=fileId,fields='parents,name').execute()
    try:
        parentId = results.get('parents')[0]
        return getFullPath(parentId)+"/"+results.get('name')
    except :
        return ""

def deleteFile(fileId_pass):
    results = service.files().delete(fileId=fileId_pass).execute()
    return True

def doFinalAction(finalActions):
    print "Action to be performed after sorting"
    print finalActions
    for action in finalActions:
        if action[-1]=="DEL":
            if action[-2]=="LOCAL":
                print "DEL:LOCAL:",action[1]
                try:
                    os.remove(action[1])
                except :
                    print "Some Error occured may file doesn't exists locally"
            else:
                print "DEL:SERVER",action[2]
                deleteFile(action[2])
        else:
            if action[-2]=="LOCAL":
                print "ADD:LOCAL:",action[2]
                Download(action[2],None)
            else:
                print "ADD:SERVER:",action[1],"ParentId:",action[3]
                uploadFile(action[1],action[3])
    return True

def Download(fileId,path):
    #check if file is  folder
    results = service.files().get(fileId=fileId,fields="mimeType").execute()
    if results['mimeType']==MIME_FOLDER:
        listing = getList(None,fileId)
        listing = itrerateFolder(listing)
        forFirstTime(listing,getFullPath(fileId)+"/")
        return True

    #If it is a file then download it
    results = service.files().get_media(fileId=fileId) #Get file media 

    fh = io.BytesIO() #Stream to write fetched data
    downloader = MediaIoBaseDownload(fh, results)
    done = False
    
    while done is False:
        status, done = downloader.next_chunk()

    #Set path
    if path:
        pathToFile = DOWNLOAD_PATH_PREFIX+path
    else:
        pathToFile = DOWNLOAD_PATH_PREFIX+getFullPath(fileId)
    
    #Create dirs
    if not os.path.exists(pathToFile[:pathToFile.rfind("/")]):
        os.makedirs(pathToFile[:pathToFile.rfind("/")])

    #Save file
    try:
        with open(pathToFile,'w') as saveFile:
            saveFile.write(fh.getvalue())
            print "File downloaded:",pathToFile
    except IOError as e:
        print "Error occured:",e

    return True

def convertArrayToNode(file_data):
    if len(file_data)==4:
        return Node(file_data['id'],file_data['name'],file_data['md5Checksum'],file_data['mimeType'])

    return Node(file_data['id'],file_data['name'],"Folder",file_data['mimeType'])

def getList(nextPageToken,parentId):
    qParameter = "parents in '"+parentId+"'"
    ret_val = []
    if nextPageToken:
        results = service.files().list(pageSize=1000,q=qParameter,pageToken=nextPageToken,fields="nextPageToken, files(id, name, md5Checksum, mimeType)").execute()
        
        items = results.get('files',[])
        for file_data in items:
            ret_val = ret_val + [convertArrayToNode(file_data)]

        nextToken = results.get('nextPageToken')
        if nextToken:
            ret_val = ret_val + getList(nextToken)
    else:
        results = service.files().list(pageSize=1000,q=qParameter,fields="nextPageToken, files(id, name, md5Checksum, mimeType)").execute()
        
        items = results.get('files',[])
        for file_data in items:
            ret_val = ret_val + [convertArrayToNode(file_data)]
        
        nextToken = results.get('nextPageToken')
        if nextToken:
            ret_val = ret_val + getList(nextToken)

    return ret_val

def prettyPrint(root,i):
    if root:
        try:
            for node in root:
                prettyPrint(node,i)
        except TypeError:
            if i>1:
                print "  "*(i)+"|--","Name:",root.name,"ID:",root.id,"Mime-Type:",root.mimeType,"md5Checksum:",root.md5Checksum
            elif i==1:
                print "|-- Name:",root.name,"ID:",root.id,"Mime-Type:",root.mimeType,"md5Checksum:",root.md5Checksum
            else:
                print "Name:",root.name,"ID:",root.id,"Mime-Type:",root.mimeType,"md5Checksum:",root.md5Checksum
            
            if root.link:
                prettyPrint(root.link,i+1)

def itrerateFolder(root):
    for folder in root:
        if folder.md5Checksum=="Folder":
            #print "Folder found with name: ",folder.name
            folder.link = getList(None,folder.id)
            #prettyPrint(folder.link)
            itrerateFolder(folder.link)

    return root

def forFirstTime(root,path):
    for file in root:
        if file.md5Checksum=="Folder":
            if not os.path.exists(DOWNLOAD_PATH_PREFIX+path+file.name):
                os.makedirs(DOWNLOAD_PATH_PREFIX+path+file.name)
            forFirstTime(file.link,path+file.name+"/")
        else:
            Download(file.id,path+file.name)

    return root

def DownloadAtSetup():
    root = getList(None,'root')
    root = itrerateFolder(root)
    forFirstTime(root,"/")
    initlastTime()
    mainRoot = Node('root','My Drive',"Folder",MIME_FOLDER)
    mainRoot.link = root
    return mainRoot

def returnRootNode():
    root = getList(None,'root')
    root = itrerateFolder(root)
    mainRoot = Node('root','My Drive',"Folder",MIME_FOLDER)
    mainRoot.link = root
    return mainRoot

setService()

if __name__ == '__main__':
    main()