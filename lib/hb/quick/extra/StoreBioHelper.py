import zmq
messageSep = '##'
from ftplib import FTP
from gold.application.LogSetup import logMessage

def getSBFnAndHBTrackAndFn(trackNameTuple):
    subtype = trackNameTuple[2]
    fileName = '/'.join(trackNameTuple[3:]).replace(',FOLDER','').split(',')[0]
    if fileName =='':
        return '',''
    hbFileName = fileName.split('/')[-1]
    hbTrackName = ['Track', subtype] +fileName.split('/')[:-1]+ [hbFileName.split('.')[0]]
    return fileName, hbTrackName, hbFileName

def getUrlToSBFile(trackNameTuple):
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")
    
    trackNameTuple[-1] = trackNameTuple[-1].split(',')[0]
    datasetId = getDatasetId(trackNameTuple[1])
    subtype = trackNameTuple[2]
    
    fileName, hbTrackName, hbFileName = getSBFnAndHBTrackAndFn(trackNameTuple)
    if fileName == '':
        return '','',''
    subList = [{'Subtype':subtype, 'FileToExtract':fileName}]#
    print datasetId, subList
    paramlist = ['operation:=GetFileUrlsFromDataSet','class:=dataStorageServicePub','params:='+'<#>'.join([ repr(datasetId), repr(subList)])]#'username:='+userName,'password:='+pwd, 
    socket.send(messageSep.join(paramlist))
    url = socket.recv_unicode().encode('ascii','ignore')
    
    return url, hbFileName, hbTrackName

def downloadFirstFtpFile(localFile, FtpAddress):
    user, pwdServ, port  = FtpAddress.replace('/','').split(':')[1:]
    pwd, server = pwdServ.split('@')
    logMessage('localFile:  '+localFile)
    ftp_h = FTP()
    ftp_h.connect(server, port)
    ftp_h.login(user, pwd)
    filenames = []
    ftp_h.retrlines('NLST', filenames.append)
    for fn in filenames:
        
        utfil = open(localFile,'wb')
        
        ftp_h.retrbinary('RETR '+ fn,  utfil.write)
        utfil.close()
        break
    ftp_h.close()


def getDatasetId(datasetStr):
    return datasetStr.split('(')[-1].split(')')[0].strip()

def getPreviewFile(trackNameTuple):
    logMessage('trackNameTuple :=  '+ repr(trackNameTuple))
    if trackNameTuple[-1].find(',FOLDER')>0:
        return None
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")
    
    trackNameTuple[-1] = trackNameTuple[-1].split(',')[0]
    datasetId = getDatasetId(trackNameTuple[1])
    subtype = trackNameTuple[2]
    fileName = '/'.join(trackNameTuple[3:]).replace(',FOLDER','').split(',')[0]
    if fileName =='':
        return None
    subList = [subtype, fileName]
    paramlist = ['params:='+'<#>'.join([ datasetId, repr(subList)]), 'operation:=GetFilePreviewFromPublicDataset','class:=dataStorageServicePub']
    socket.send(messageSep.join(paramlist))
    filePreview = socket.recv_unicode().encode('ascii','ignore')
    #startIndex, endIndex = filePreview.find('<Preview>')+9,  filePreview.rfind('</Preview>')
    #filePreview = filePreview[startIndex:endIndex]
    from tempfile import NamedTemporaryFile
    tempfile = NamedTemporaryFile()
    tempfile.write(filePreview)
    logMessage('fileName :=  '+fileName)
    logMessage('NamedTemporaryFile :=  '+tempfile.name)
    logMessage('FilePreview :=  '+ filePreview)
    return tempfile

#refusjon@norwegian.no
