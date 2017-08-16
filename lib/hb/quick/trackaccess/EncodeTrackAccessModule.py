import ast
import os
import sys
import shutil
import string
import urllib2
import re
from traceback import print_stack

from urlparse import urlparse
from ftputil import FTPHost

from config.Config import HB_SOURCE_CODE_BASE_DIR, HB_SOURCE_DATA_BASE_DIR
from quick.trackaccess.DatabaseTrackAccessModule import DatabaseTrackAccessModule
from quick.trackaccess.EncodeDatabase import EncodeDatabase
from quick.trackaccess.CommonVocabularyParser import CommonVocabularyParser

#from gold.gsuite.GSuite import GSuite
from gold.gsuite.GSuiteTrack import GSuiteTrack
import gold.gsuite.GSuiteFunctions




#============================Will be replaced============================
#import imp
#file,filename,data = imp.find_module('EncodeDatabase',\
#                                     ['/cluster/home/azab/T1'])
#mod1 = imp.load_module('EncodeDatabase', file, filename, data)
#file,filename,data = imp.find_module('CommonVocabularyParser',\
#                                     ['/cluster/home/azab/T1'])
#mod2 = imp.load_module('CommonVocabularyParser', file, filename, data)
#=========================================================================

from collections import OrderedDict
###from config.Config import GALAXY_REQUESTS_EMAIL_URL
from quick.util.CommonFunctions import ensurePathExists
from quick.trackaccess.TrackAccessModule import TrackAccessModule, StructIndexElement
import quick.trackaccess.TrackAccessModuleRegistry as TrackAccessModuleRegistry

def _onError(e):
    raise e

def getFileSuffixFromRow(row):
    url = None
    if 'url' in row:
        url = row['url']
    elif 'uri' in row:
        url = row['uri']
    elif '_url' in row:
        url = row['_url']

    attr_val_list = []

    for k in row.keys():
        if row[k] in ['None','']:
            continue
        ## some datatypes are not string, e.g. datetime, and some others contain non-printable characters, e.g. \x00
        value = filter(lambda x: x in string.printable, unicode(str(row[k]).decode('utf-8').strip()))
        if value.strip() == '':
            value = '.'
        attr_val_list.append((k,value))
    #print attr_val_list
    track = GSuiteTrack(url, doUnquote = True, genome='hg19', attributes=OrderedDict(attr_val_list))
    suffix = gold.gsuite.GSuiteFunctions.getSuffixWithCompressionSuffixesRemoved(track).lower()
    #print 'suffix: '+ suffix
    return suffix

#class RemoteAccessSite(object):
#    def __new__(cls, url, *args, **kwArgs):
#        scheme = urlparse(url).scheme
#        if scheme == 'ftp':
#            return FtpRemoteAccessSite.__new__(FtpRemoteAccessSite, url, *args, **kwArgs)
#        raise NotSupportedError
#
#    def __init__(self, url):
#        parsedUrl = urlparse(url)
#        netloc = parsedUrl.netloc.split(':')
#        self._hostURL = netloc[0]
#        self._path = parsedUrl.path

## from urllib2 import urlopen
## url = 'https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/'
## response = urlopen(url).read()
## re.findall('<a href=".*?">(.*?)</a>',response)

class HttpRemoteAccessSite(object):
    def __init__(self, url):
        self._URL = url
        
    def retrieveJSON(self,path):
        try:
            response = urllib2.urlopen(self._URL + path).read()
            return ast.literal_eval(response)
        except:
            return None
    
    def retrieveFileNames(self,path, pattern = '<a href=".*?">(.*?)</a>'):
       response = urllib2.urlopen(self._URL + path).read()
       fileList = re.findall(pattern,response)
       #print 'File List:'
       #print fileList
       return fileList
    
    def getFileNames(self,path):
        patternTag = '<a href=".*?">(.*?)</a>'
        patternName = '<a href="(.*?)">.*?</a>'
        response = urllib2.urlopen(self._URL + path).read()
        nameList = re.findall(patternName,response)
        tagList = re.findall(patternTag,response)
        specialTags = ['Name','Last modified','Size','Description','Parent Directory']
        cleanTagList = []
        for i in range(len(tagList)):
            isSpeacialTag = False
            for sn in specialTags:
                if tagList[i].find(sn)>-1:
                    isSpeacialTag = True
                    break
            
            if not isSpeacialTag:
                cleanTagList.append(tagList[i])
        
        return list(set(cleanTagList))
    
    def getFileNameFromTag(self, dirURL, tag):
        pattern = '<a href="(.*?)">'+tag+'</a>'
        response = urllib2.urlopen(dirURL).read()
        return re.findall(pattern,response)[0].split('"')[-1]
    
    def getFileTagsNames(self,dirName):
        dirURL = self._URL + dirName
        patternTag = '<a href=".*?">(.*?)</a>'
        patternName = '<a href="(.*?)">.*?</a>'
        lines = urllib2.urlopen(dirURL).read().split('\n')
        fileDict = {}
        for line in lines:
            try:
                name = re.findall(patternName,line)[0]
                tag = re.findall(patternTag,line)[0]
                if tag in ['Name','Last modified','Size','Description','Parent Directory']:
                    continue
            except:
                continue
            fileDict.update({tag:name})
        return fileDict
    
    def getIndexFileURL(self,dirPath,endsWith):
        print 'Getting Index File name from dir: '+dirPath
        lines = urllib2.urlopen(self._URL + dirPath).read().split('\n')
        for line in lines:
            try:
                fn = re.findall('<a href="(.*?)">.*?</a>',line)[0]
            except:
                continue
            if fn.endswith(endsWith):
                    return self._URL + dirPath + fn
                
        #files = self.retrieveFileNames(dirPath)
        #print 'Parent dir: '+dirPath
        #for fn in files:
        #    if fn.endswith(endsWith):
        #        return self._URL + dirPath + fn
        
    def retrieveFileData(self,fileURL):    
        return urllib2.urlopen(fileURL).read().split('\n')
    
        
class FtpRemoteAccessSite(object):
    def __init__(self, url):
        parsedUrl = urlparse(url)
        netloc = parsedUrl.netloc.split(':')
        self._URL = url
        self._hostURL = netloc[0]
        self._path = parsedUrl.path
        self._user = 'anonymous'
        ###emailUrl = GALAXY_REQUESTS_EMAIL_URL
        ###self._password = emailUrl.split(':')[-1] if emailUrl.startswith('mailto') else emailUrl
        self._host = None

    def _connectToHost(self):
        self._host = FTPHost(self._hostURL, self._user, '')###self._password)
        self._host.chdir(self._path)

    def _disconnectFromHost(self):
        try:
            self._host.close()
            self._host = None
        except:
            pass

    def syncFile(self, fn, localPath, returnFile=False):
        if fn.startswith('./'):
            fn = fn[2:]
        rsyncURL = 'rsync://' + self._hostURL + self._path + fn
        localFn = os.path.join(localPath, fn)
        ensurePathExists(localFn)

        import subprocess
        subprocess.call(['rsync', '-a', '-P', rsyncURL, localFn])

        if returnFile:
            #return open(localFn)
            return localFn

    def yieldFile(self, file_name,dir_name):
        try:
            self._connectToHost()
            if self._host.path.exists(file_name):
                f = self.syncFile(file_name, dir_name, returnFile=True)
                yield f
                ##f.close()
                #f = self._host.open(fn)
                #yield f
                #f.close()
        finally:
            self._disconnectFromHost()

    def yieldSecondLevelFiles(self, file_name,dir_name):
        try:
            self._connectToHost()
            for root, dirs, files in self._host.walk('.', _onError):
                break

            i = 0
            for dir in dirs:
                i += 1
                if i > 1000:
                   break
                index_file_name = '/'.join([root, dir, file_name])

                if self._host.path.exists(index_file_name):
                    f = self.syncFile(index_file_name, dir_name, returnFile=True)
                    yield f
                    ##f.close()
                    #f = self._host.open(idxFn)
                    #yield f
                    #f.close()
        finally:
            self._disconnectFromHost()

    def getEpigenomeFiles(self):#For Epigenome like file structure
        fileList = []
        try:
            self._connectToHost()
            #i = 0
            for root, dirs, files in self._host.walk('.', _onError):
                #i += 1
                #if i>5:
                #   break
                metadata = root.strip('./').split('/')
                print 'root: '+root
                if len(metadata) < 3:
                   continue
                for f in files:
                   fileURL = self._URL + root.strip('./')+ '/' + f
                   dataType = self.DB.getDataType(rowDict['url'].split('/')[-1], 'Epigenome')
                   rowDict = {'study':metadata[0],'sample':metadata[1],\
                   'experiment':metadata[2],'hb_datatype':dataType,'URL':fileURL}
                   rowDict['hb_filesuffix'] = getFileSuffixFromRow(rowDict)
                   fileList.append(rowDict)
        finally:
            self._disconnectFromHost()
        return fileList

##############################################################################
class TCGATrackAccessModule(object):
    CGAtlas_URL = 'https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/'

    def __init__(self, fileIndexTable,isSqlite = False):
        self._site = HttpRemoteAccessSite(self.CGAtlas_URL)
        self._fileIndexTable = fileIndexTable
        self.DB = DatabaseTrackAccessModule(isSqlite, raiseDBErrors = False)
        self.DB._db.connect()

    def makeFileIndexTable(self):
        List = self._site.retrieveFileNames('')
        cancerTypeList = [(x,) for x in List if x.endswith('/')]
        centerTypeList = []
        centerNameList = []
        dataTypeList = []
        platformNameList =[]
        dataFileList =[]
        #globalURLList = []
        #gpathList = []
        
        #cols = ['cancertype','centertype','centerName','datatype','platformname','url']
        cols = ['cancertype','centertype','centerName','platformname','datatype','hb_datatype','hb_filesuffix',\
                'curation','level','url']
        self.DB._db.dropTable(self._fileIndexTable)
        self.DB._db.createTableFromList(self._fileIndexTable,cols, pk = 'url')
        
        i = 0
        for (cancertype,) in cancerTypeList:
            #print cancertype+'-'
            ##print 'Index: '+str(i)
            i += 1
            #if i != 1:
            #    continue
            print 'Cancer Type:'  + cancertype + '('+ str(i)+ ' of '+str(len(cancerTypeList))+')'
            #self.DB._db.deleteRows(self._fileIndexTable,"cancertype LIKE '"+cancertype+"'")
            List = self._site.getFileNames(cancertype)
            centerTypeList = [(cancertype,x) for x in List if x.endswith('/')]
            #print len(centerTypeList)
            #ii = 0
            for (cancertype,centertype) in centerTypeList:
                if centertype.lower() != 'gsc/':#Requested by Daniel Vordak
                    continue
                print cancertype+'-'+centertype+'-'
                #ii+=1
                List = self._site.getFileNames(cancertype+centertype)
                centerNameList = [(cancertype,centertype,x) for x in List if x.endswith('/')]
                #print '-'+str(len(centerTypeList))
                #iii = 0
                for (cancertype,centertype,centerName) in centerNameList:
                    print cancertype+'-'+centertype+'-'+centerName+'-'
                    #iii += 1
                    List = self._site.getFileNames(cancertype+centertype+centerName)
                    dataTypeList = [(cancertype,centertype,centerName,x) for x in List if x.endswith('/')]
                    #iiii = 0
                    for (cancertype,centertype,centerName,datatype) in dataTypeList:
                        print cancertype+'-'+centertype+'-'+centerName+'-'+datatype+'-'
                        #iiii+=1
                        List = self._site.getFileNames(cancertype+centertype+centerName+datatype)
                        platformNameList = [(cancertype,centertype,centerName,datatype,x) for x in List if x.endswith('/')]
                        
                        curation = 'not specified'#Requested by Daniel Vordak
                        if len(datatype.split('_')) > 2:
                            curation = '_'.join(datatype.split('_')[2:]).strip('/')
                        
                        dataFileList = []
                        #iiiii = 0
                        for (cancertype,centertype,centerName,datatype,platformname) in platformNameList:
                            print cancertype+'-'+centertype+'-'+centerName+'-'+datatype+'-'+platformname+'-'
                            #iiiii +=1
                            #List = self._site.retrieveFileNames(cancertype+centertype+centerName+datatype+platformname)
                            List = self._site.getFileNames(cancertype+centertype+centerName+datatype+platformname)
                            #urlList = [self._site._URL+cancertype+centertype+centerName+datatype+platformname+x for x in List]
                            
                            #if path in gpathList:
                            #    print '-'.join([str(i),str(ii),str(iii),str(iiii),str(iiiii),'(R):'+path])
                            #else:
                            #    #print path
                            #    gpathList.append(path)
                            #urlList = []
                            #platformNameSubList = []
                            for name in List:
                                #if url in globalURLList:
                                #    continue
                                ##urlList.append(url)
                                #globalURLList.append(url)
                                if not name.endswith('/') and name.find('.')>-1 and name.endswith('.maf'):
                                    url = self._site._URL+cancertype+centertype+centerName+datatype+platformname+name
                                    rowDict = {'cancertype':cancertype.strip('/'),
                                              'centertype':centertype.strip('/'),
                                              'centername':centerName.strip('/'),
                                              'datatype':platformname.strip('/'),#platformname and datatype are exchanged (bug in the web-site)
                                              'hb_datatype':self.DB.getDataType(url.split('/')[-1], 'CGAtlas'),
                                              'platformname':datatype.strip('/').split('_')[0],
                                              'curation':curation,
                                              'level':None,
                                              #'url':self._site._URL+cancertype+centertype+centerName+datatype+platformname+x} for x in List if not x.endswith('/') and x.find('.')>-1]
                                              'url':url}
                                    rowDict['hb_filesuffix'] = getFileSuffixFromRow(rowDict)
                                    dataFileList.append(rowDict)
                                elif name.endswith('/'):
                                    print '>>'+cancertype+centertype+centerName+datatype+platformname+name
                                    subList = self._site.getFileNames(cancertype+centertype+centerName+datatype+platformname+name)
                                    urlList = [self._site._URL+cancertype+centertype+centerName+datatype+platformname+name+x for x in subList]
                                    for url in urlList:
                                        if not url.endswith('.maf'):#Requested by Daniel Vordak
                                            continue
                                        print '--' + url
                                        rowDict = {'cancertype':cancertype.strip('/'),
                                              'centertype':centertype.strip('/'),
                                              'centername':centerName.strip('/'),
                                              'datatype':platformname.strip('/'),#platformname and datatype are exchanged (bug in the web-site)
                                              'hb_datatype':self.DB.getDataType(url.split('/')[-1], 'CGAtlas'),
                                              'platformname':datatype.strip('/').split('_')[0],
                                              'curation':curation,
                                              'level':name.split('_')[-1].strip('/'),
                                              #'url':self._site._URL+cancertype+centertype+centerName+datatype+platformname+x} for x in List if not x.endswith('/') and x.find('.')>-1]
                                              'url':url}
                                        rowDict['hb_filesuffix'] = getFileSuffixFromRow(rowDict)
                                        dataFileList.append(rowDict)
                                        break#There is only one .maf file per dir
                                    #platformNameSubList = [(cancertype,centertype,centerName,datatype,platformname,name,x) for x in subList]
                                    #for (cancertype,centertype,centerName,datatype,platformname,name,x) in platformNameSubList:
                                        
                            #print '-'.join([str(i),str(ii),str(iii),str(iiii),str(iiiii)])
                        if len(dataFileList) > 0:
                            print cancertype+centertype+centerName+datatype+platformname
                            #print '-'.join([str(i),str(ii),str(iii),str(iiii),str(iiiii),path])
                            self.DB._db.insertRows(self._fileIndexTable,dataFileList)    
                    
        
    def setMetadata(self):
        METADATA_TABLE = 'file_col_metadata'
        rowList = []
        cols = self.DB._db.getTableCols(self._fileIndexTable)
        for col in cols:
            row = {'table_name':self._fileIndexTable,'col_val':'.'}
            if col == 'hb_datatype':
                rName = 'Type of data'
            if col == 'hb_filesuffix':
                rName = 'File Suffix'
            elif col.find('type') > -1:
                rName =  col.split('type')[0].title()+' Type'
            elif col.find('name') > -1:
                rName =  col.split('name')[0].title()+' Name'
            else:
                rName = col
            row.update({'col_name':col, 'col_readable_name':rName})
            rowList.append(row)
        cancertypes = [('laml','Acute Myeloid Leukemia','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=LAML&diseaseName=Acute%20Myeloid%20Leukemia'),\
                          ('acc','Adrenocortical carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=ACC&diseaseName=Adrenocortical%20carcinoma'),\
                          ('blca','Bladder Urothelial Carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=LGG&diseaseName=Brain%20Lower%20Grade%20Glioma'),\
                          ('lgg','Brain Lower Grade Glioma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=LGG&diseaseName=Brain%20Lower%20Grade%20Glioma'),\
                          ('brca','Breast invasive carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=BRCA&diseaseName=Breast%20invasive%20carcinoma'),\
                          ('cesc','Cervical squamous cell carcinoma and endocervical adenocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=CESC&diseaseName=Cervical%20squamous%20cell%20carcinoma%20and%20endocervical%20adenocarcinoma'),\
                          ('chol','Cholangiocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=CHOL&diseaseName=Cholangiocarcinoma'),\
                          ('coad','Colon adenocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=COAD&diseaseName=Colon%20adenocarcinoma'),\
                          ('esca','Esophageal carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=ESCA&diseaseName=Esophageal%20carcinoma'),\
                          ('fppp','FFPE Pilot Phase II','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=FPPP&diseaseName=FFPE%20Pilot%20Phase%20II'),\
                          ('gbm','Glioblastoma multiforme','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=GBM&diseaseName=Glioblastoma%20multiforme'),\
                          ('hnsc','Head and Neck squamous cell carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=HNSC&diseaseName=Head%20and%20Neck%20squamous%20cell%20carcinoma'),\
                          ('kich','Kidney Chromophobe','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=KICH&diseaseName=Kidney%20Chromophobe'),\
                          ('kirc','Kidney renal clear cell carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=KIRC&diseaseName=Kidney%20renal%20clear%20cell%20carcinoma'),\
                          ('kirp','Kidney renal papillary cell carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=KIRP&diseaseName=Kidney%20renal%20papillary%20cell%20carcinoma'),\
                          ('lihc','Liver hepatocellular carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=LIHC&diseaseName=Liver%20hepatocellular%20carcinoma'),\
                          ('luad','Lung adenocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=LUAD&diseaseName=Lung%20adenocarcinoma'),\
                          ('lusc','Lung squamous cell carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=LUSC&diseaseName=Lung%20squamous%20cell%20carcinoma'),\
                          ('dlbc','Lymphoid Neoplasm Diffuse Large B-cell Lymphoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=DLBC&diseaseName=Lymphoid%20Neoplasm%20Diffuse%20Large%20B-cell%20Lymphoma'),\
                          ('meso','Mesothelioma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=MESO&diseaseName=Mesothelioma'),\
                          ('ov','Ovarian serous cystadenocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=OV&diseaseName=Ovarian%20serous%20cystadenocarcinoma'),\
                          ('paad','Pancreatic adenocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=PAAD&diseaseName=Pancreatic%20adenocarcinoma'),\
                          ('pcpg','Pheochromocytoma and Paraganglioma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=PCPG&diseaseName=Pheochromocytoma%20and%20Paraganglioma'),\
                          ('prad','Prostate adenocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=PRAD&diseaseName=Prostate%20adenocarcinoma'),\
                          ('read','Rectum adenocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=READ&diseaseName=Rectum%20adenocarcinoma'),\
                          ('sarc','Sarcoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=SARC&diseaseName=Sarcoma'),\
                          ('skcm','Skin Cutaneous Melanoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=SKCM&diseaseName=Skin%20Cutaneous%20Melanoma'),\
                          ('stad','Stomach adenocarcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=STAD&diseaseName=Stomach%20adenocarcinoma'),\
                          ('tgct','Testicular Germ Cell Tumors','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=TGCT&diseaseName=Testicular%20Germ%20Cell%20Tumors'),\
                          ('thym','Thymoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=THYM&diseaseName=Thymoma'),\
                          ('thca','Thyroid carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=THCA&diseaseName=Thyroid%20carcinoma'),\
                          ('ucs','Uterine Carcinosarcoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=UCS&diseaseName=Uterine%20Carcinosarcoma'),\
                          ('ucec','Uterine Corpus Endometrial Carcinoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=UCEC&diseaseName=Uterine%20Corpus%20Endometrial%20Carcinoma'),\
                          ('uvm','Uveal Melanoma','https://tcga-data.nci.nih.gov/tcga/tcgaCancerDetails.jsp?diseaseType=UVM&diseaseName=Uveal%20Melanoma'),\
                          ('cntl','Controls',None),\
                         ]
        for val,rname,url in cancertypes:
            row = {'table_name':self._fileIndexTable,'col_name':'cancertype','col_readable_name':rname,'col_val':val,'col_description':url}
            rowList.append(row)
        self.DB._db.deleteRows(METADATA_TABLE, "table_name LIKE '"+self._fileIndexTable+"'")
        self.DB._db.insertRows(METADATA_TABLE,rowList)
##############################################################################
class ICGCTrackAccessModule(object):
    #ICGC_URL = 'https://dcc.icgc.org/api/v1/download/info/current/Projects/'
    ICGC_URL = 'https://dcc.icgc.org/api/v1/download/info'
    ICGC_URL_download = 'https://dcc.icgc.org/api/v1/download'

    def __init__(self, fileIndexTable,isSqlite = False):
        self._site = HttpRemoteAccessSite(self.ICGC_URL)
        self._fileIndexTable = fileIndexTable
        self.DB = DatabaseTrackAccessModule(isSqlite)
        self.DB._db.connect()

    def makeFileIndexTable(self):
        self.DB._db.dropTable(self._fileIndexTable)
        cols = ['project','release','file_name','hb_datatype','hb_filesuffix','hb_target',\
                'hb_genomebuild','url']
        self.DB._db.createTableFromList(self._fileIndexTable,cols, pk = 'url')

        json_main = self._site.retrieveJSON('')
        releases = [x['name'].split('/')[-1] for x in json_main if not 'README' in x['name']]
        for release in releases:
            print 'Release: ' + release
            json_release = self._site.retrieveJSON('/'+release+'/Projects')
            if not isinstance(json_release,list) or release == 'current':
                #No available projects data for this release
                #Or it is 'current' (because the current release with it's own release number will be there)
                continue
            projects = [x['name'] for x in json_release]
            #print json_release
            #print projects
            for project in projects:
                print 'Project: '+project
                if project.upper().find('README') > -1:
                    continue
                json_project = self._site.retrieveJSON(project+'/')#The project path includes the release as well
                #print json_project
                tracks = []
                for x in json_project:
                    rowDict = {'release': release,'project':project.split('/')[-1], 'file_name':x['name'].split('/')[-1].split('.')[0],
                           'hb_datatype':self.DB.getDataType(self.ICGC_URL_download+'?fn='+x['name'].split('/')[-1], 'ICGC'),
                           'url': self.ICGC_URL_download+'?fn='+x['name']}
                    rowDict['hb_filesuffix'] = getFileSuffixFromRow(rowDict)
                    if 'project' in rowDict:
                        rowDict['hb_target'] = rowDict['project']
                    rowDict['hb_genomebuild'] = 'hg19'
                    tracks.append(rowDict)
                #print tracks[0]
                self.DB._db.insertRows(self._fileIndexTable,tracks)
        
    def setMetadata(self):
        METADATA_TABLE = 'file_col_metadata'
        rowList = []
        cols = self.DB._db.getTableCols(self._fileIndexTable)
        keywords = {'url':'URL','project':'Project','file_name':'File Name','hb_datatype':'Type of Data',\
                    'hb_filesuffix':'File Suffix','hb_target':'* Target',\
                    'hb_genomebuild':'* Genome Build','file_name':'File Type'}
        for col in cols:
            row = {'table_name':self._fileIndexTable}
            if col in keywords.keys():
                rName = keywords[col]
            else:
                rName = col.title()
            rName = rName.strip()
            row.update({'col_name':col, 'col_readable_name':rName,'col_val':'.'})
            rowList.append(row)
        f = open(HB_SOURCE_DATA_BASE_DIR + '/trackaccess/icgc-cancertypes','r')
        lines = f.readlines()
        f.close()
        
        for line in lines:
            val = line.split('[')[1].split(']')[0].strip()
            rname =  line.split(']')[1].strip(' \n')
            row = {'table_name':self._fileIndexTable,'col_name':'project','col_val':val,'col_readable_name':rname}
            rowList.append(row)
        #for name,rname in cancertypes:
        #    row = {'table_name':self._fileIndexTable,'col_name':'project','col_val':name,'col_readable_name':rname}
        #    rowList.append(row)
        self.DB._db.deleteRows(METADATA_TABLE, "table_name LIKE '"+self._fileIndexTable+"'")
        self.DB._db.insertRows(METADATA_TABLE,rowList)
##############################################################################
class Epigenome2TrackAccessModule(object):
    EPIGENOME2_URLs = ['http://egg2.wustl.edu/roadmap/data/byFileType/peaks/consolidated/',
                      'http://egg2.wustl.edu/roadmap/data/byFileType/peaks/consolidatedImputed/']
    #Metadata files, retrieved from the Google spreadsheet at 'http://egg2.wustl.edu/roadmap/web_portal/meta.html'
    #Open the sheet, then download the first and the second tabs as tsv files
    SUMMARY_TABLE = HB_SOURCE_CODE_BASE_DIR + '/quick/trackaccess/roadmap-epigenomics/jul2013.roadmapData.qc-Consolidated_EpigenomeIDs_summary_Table.tsv'
    QUALITY_CONTROL = HB_SOURCE_CODE_BASE_DIR + '/quick/trackaccess/roadmap-epigenomics/jul2013.roadmapData.qc-Consolidated_EpigenomeIDs_QC.tsv'
    
    def __init__(self, fileIndexTable,isSqlite = False):
        self._fileIndexTable = fileIndexTable
        self.DB = DatabaseTrackAccessModule(isSqlite = isSqlite,raiseDBErrors = False)
        self.DB._db.connect()
        self.trackMetadata = []
        self.cols = []
    
    def makeTrackMetadata(self):
        fs = open(self.SUMMARY_TABLE)
        fq = open(self.QUALITY_CONTROL)
        lines_fs = [l.strip('\n').split('\t') for l in fs.readlines()]
        lines_fq = [l.strip('\n').split('\t') for l in fq.readlines()]
        trackIDs = [line[1] for line in lines_fs[3:]]
        self.cols = ['url','hb_datatype','hb_filesuffix','hb_cell_tissue_type','hb_target','hb_genomebuild'] +\
            [col_name.replace('\r','').replace(',','_COMMA_') for col_name in lines_fq[0]]
        
        i=0
        for i in range(len(lines_fs[0])):
            # Repeated column names in both SUMMARY_TABLE and QUALITY_CONTROL --> get the values from QUALITY_CONTROL
            if lines_fs[0][i] in ['Epigenome name (from EDACC Release 9 directory)','NSC (Signal to noise)','RSC (Phantom Peak)']:
                continue
            ##Hard-coded list of unused columns from the summary table
            if lines_fs[0][i] in ['Pool Filenames','Nreads (36bp) 30M','Nreads (36bp) 50M','RSC (Phantom Peak)']:
                continue
            if lines_fs[0][i].strip() == '':
                continue
            colname = lines_fs[0][i]+'~'+lines_fs[1][i]+'~'+lines_fs[2][i]
            colname = colname.replace('\r','').replace(',','_COMMA_')
            #print colname
            # To avoid error in the search tool since colListString splits colum names by commas
            self.cols.append(colname)
        #print self.cols
        for line_q in lines_fq[1:]:
            row = {}
            i = 0
            #Add fields from QUALITY_CONTROL 
            for i in range(len(line_q)):
                col = lines_fq[0][i].replace('\r','').replace(',','_COMMA_')
                row[col] = line_q[i]
            
            #Find the associated line in SUMMARY_TABLE
            summary_line = None
            for line in lines_fs[3:]:
                if line[1].strip() == row['EID']:
                    summary_line = line
                    break
            
            #Add the associated fields from the SUMMARY_TABLE
            i = 0
            for i in range(len(summary_line)):
                    col_name = lines_fs[0][i]+'~'+lines_fs[1][i]+'~'+lines_fs[2][i]
                    col_name = col_name.replace('\r','').replace(',','_COMMA_')
                    if col_name in self.cols:
                        row[col_name] = summary_line[i]
            for k in row.keys():
                row[k] = row[k].replace('\r','').replace(',','_COMMA_')
                if k == 'MARK CLASS':
                    row[k] = row[k].replace(' ','')
            self.trackMetadata.append(row)    
    
    def makeFileIndexTable(self):
        
        self.makeTrackMetadata()
        
        self.DB._db.dropTable(self._fileIndexTable)
        self.DB._db.createTableFromList(self._fileIndexTable,self.cols, pk = 'url')
        searchPaths = ['broadPeak/','gappedPeak/','narrowPeak/']
        for URL in self.EPIGENOME2_URLs:
            site = HttpRemoteAccessSite(URL)
            for path in searchPaths:
                rows = []
                try:#Check if the path exists
                    urllib2.urlopen(URL+path)
                except:#Doesn't exist
                    continue
                print URL+path
                filenames = site.getFileNames(path)
                for filename in filenames:
                    for r in self.trackMetadata:
                        if r['FNAME'].split('.')[0] == filename.split('.')[0]:
                            row = r.copy() #Must use .copy() since the dict is a reference type
                            row['url'] = URL+path+filename
                            row['hb_datatype'] = self.DB.getDataType(filename, 'Epigenome2')
                            row['hb_filesuffix'] = getFileSuffixFromRow(row)
                            if 'Standardized Epigenome name~~' in row:
                                row['hb_cell_tissue_type'] = row['Standardized Epigenome name~~']
                            if 'MARK' in row:
                                row['hb_target'] = row['MARK']
                            row['hb_genomebuild'] = 'hg19'
                            rows.append(row)
                            break
                self.DB._db.insertRows(self._fileIndexTable,rows)    
        #with open('urls','w') as f:
        #    print >> f,urls
        
    def setMetadata(self):
        print 'Making metadata'
        METADATA_TABLE = 'file_col_metadata'
        rowList = []
        cols = self.DB._db.getTableCols(self._fileIndexTable)
        keywords = {'url':'URL','hb_datatype':'Type of Data','hb_filesuffix':'File Suffix',\
                    'hb_target':'* Target','hb_cell_tissue_type':'* Cell/Tissue Type','hb_genomebuild':'* Genome Build',\
                    'SEX (Male_COMMA_ Female_COMMA_ Mixed_COMMA_ Unknown)~33~50':'SEX',\
                    'Single Donor (SD) /Composite (C)~43~47':'Single Donor (SD) /Composite (C)',\
                    'AGE (Post Birth in YEARS/ Fetal in GESTATIONAL WEEKS/CELL LINE CL) ~~':'Age'}
        for col in cols:
            row = {'table_name':self._fileIndexTable,'col_val':'.'}
            if col in keywords.keys():
                rName = keywords[col]
            else:
                rName = col.replace('~',' ').replace('_COMMA_',',').strip()
            row.update({'col_name':col, 'col_readable_name':rName})
            rowList.append(row)
        self.DB._db.deleteRows(METADATA_TABLE, "table_name LIKE '"+self._fileIndexTable+"'")
        self.DB._db.insertRows(METADATA_TABLE,rowList)
        

##############################################################################
class EpigenomeTrackAccessModule(object):
    EPIGENOME_URL = 'ftp://ftp.genboree.org/EpigenomeAtlas/Current-Release/study-sample-experiment/'

    def __init__(self, fileIndexTable,isSqlite = False):
        self._site = FtpRemoteAccessSite(self.EPIGENOME_URL)
        self._fileIndexTable = fileIndexTable
        self.DB = DatabaseTrackAccessModule(isSqlite)
        self.DB._db.connect()

    def makeFileIndexTable(self):
        cols = ['study','sample','experiment', 'hb_datatype','hb_filesuffix','url']
        files = self._site.getEpigenomeFiles()
        self.DB._db.dropTable(self._fileIndexTable)
        self.DB._db.createTableFromList(self._fileIndexTable,cols, pk = 'url')
        self.DB._db.insertRows(self._fileIndexTable,files)
        self.DB._db.deleteRows(self._fileIndexTable,where = "url LIKE '%DATA RELEASE POLICY%'")
    def setMetadata(self):
        METADATA_TABLE = 'file_col_metadata'
        rowList = []
        cols = self.DB._db.getTableCols(self._fileIndexTable)
        for col in cols:
            row = {'table_name':self._fileIndexTable,'col_val':'.'}
            if col == 'url':
                rName = 'URL'
            elif col == 'hb_datatype':
                rName = 'HB Data Type'
            elif col == 'hb_filesuffix':
                rName = 'HB File Suffix'
            else:
                rName = col.title()
            row.update({'col_name':col, 'col_readable_name':rName})
            rowList.append(row)
        self.DB._db.deleteRows(METADATA_TABLE, "table_name LIKE '"+self._fileIndexTable+"'")
        self.DB._db.insertRows(METADATA_TABLE,rowList)
##############################################################################
class FANTOM5TrackAccessModule(object):
    FANTOM5_URL = 'http://fantom.gsc.riken.jp/5/datafiles/latest/basic/'
    INDEX_FILENAME_ENDS_WITH = '_sdrf.txt'
    
    def __init__(self, fileIndexTable,isSqlite = False):
        self._site = HttpRemoteAccessSite(self.FANTOM5_URL)
        self._fileIndexTable = fileIndexTable
        self._indexFiles = []
        self._attributes = []
        self._attributesDict = {}
        self._rowList = []
        self._errorFiles = []
        self.DB = DatabaseTrackAccessModule(isSqlite)
        self.DB._db.connect()
        
    def setIndexFiles(self):
        dirList = [x for x in self._site.retrieveFileNames('') if x.endswith('/')]
        self._indexFiles = [self._site.getIndexFileURL(x,self.INDEX_FILENAME_ENDS_WITH) for x in dirList]
    
    def getIndexFiles(self):
        return self._indexFiles
    
    def setAttributes(self):
        allAttributes = self._site.retrieveFileData(self._indexFiles[0])[0].split('\t')
        #print 'All Attributes:'
        #print allAttributes
        self._attributesDict = {}
        self._attributes = []
        allAttributes2 = []
        i = 0
        setProtocolRef = False
        for attr in allAttributes:
            if attr.startswith('Extract') or attr.startswith('Parameter') or attr.startswith('Comment') or attr.find('File Name') > -1:
               self._attributesDict.update({attr:i})
            elif attr.find('Protocol REF') > -1 and setProtocolRef:
               self._attributesDict.update({attr:i})
               setProtocolRef = False
            
            if attr.find('library_protocol') > -1:
               setProtocolRef = True
            
            allAttributes2.append(attr)
            if allAttributes2.count(attr) > 1:
                self._attributes.append(attr+'__'+str(allAttributes2.count(attr))+'__')
            else:
                self._attributes.append(attr)
            i+=1
        self._attributes.extend(['url','hb_datatype','hb_filesuffix'])
    
    def getAttributes(self):
        return self._attributes
    
    def makeIndexTable(self):
        self.DB._db.dropTable(self._fileIndexTable)
        cols = [x for x in self._attributes]
        self.DB._db.createTableFromList(self._fileIndexTable,cols, pk = 'url')
    
    def insertIndexData(self, indexFileURL):
        print '**Index File: '+indexFileURL
        indexFileName = indexFileURL.split('/')[-1]
        dirURL = indexFileURL.rstrip(indexFileName)
        fileNamesTagsDict = self._site.getFileTagsNames(dirURL.split('/')[-2]+'/')
        lines = self._site.retrieveFileData(indexFileURL)#[0].split('\t')
        rowList = []
        for line in lines[1:]:
            
            lineList = line.split('\t')
            if len(lineList) < len(self._attributes) - 2: #2: url and _datatype
                continue
            #print 'Line List:'
            #print lineList
            #print 'Length: '+str(len(lineList))
            #print 'Length attributes:' +str(len(self._attributes))
            rowDict = {}
            i = 0
            error = None
            for attr in self._attributes:
                try:
                    if not attr in ['url','hb_datatype','hb_filesuffix']:
                        rowDict.update({attr:lineList[i].strip()})
                    else:
                        fileTag = rowDict['File Name__2__'].strip()
                        ##print 'Getting File: ' + dirURL + fileTag
                        #fileName = self._site.getFileNameFromTag(dirURL,rowDict['"File Name__2__"'])
                        fileName = fileNamesTagsDict[fileTag]
                        url = dirURL+fileName
                        rowDict.update({'url':url})
                        rowDict['hb_datatype'] = self.DB.getDataType(rowDict['url'].split('/')[-1], 'FANTOM5')
                        rowDict['hb_filesuffix'] = getFileSuffixFromRow(rowDict)
                except Exception as e:
                    error = {}
                    error ['FileName'] = fileTag
                    error['Index file'] = indexFileURL 
                    self._errorFiles.append(error)
                    break
                    #print '"File Name__2__": <' + fileTag + '>'
                    #print 'Index file: '+ indexFileURL
                    #print 'fileNamesTagsDict: '
                    #print fileNamesTagsDict
                    #raise
                    
                    
                i += 1
            #print rowDict
            if error is None:
                rowList.append(rowDict)
        
        self.DB._db.insertRows(self._fileIndexTable,rowList)
        return rowList
    
    def setMetadata(self):
        METADATA_TABLE = 'file_col_metadata'
        rowList = []
        cols = self.DB._db.getTableCols(self._fileIndexTable)
        for col in cols:
            row = {'table_name':self._fileIndexTable}
            if col == 'hb_datatype':
                rName = 'HB Data Type'
            if col == 'hb_filesuffix':
                rName = 'HB File Suffix'
            elif col.startswith('Comment') or col.startswith('Parameter'):
                rName = col.split('[')[1].strip(']')
            elif col.endswith('__'):
                rName = re.sub(r'__.__','',col)
            else:
                rName = col
            row.update({'col_name':col, 'col_readable_name':rName,'col_val':'.'})
            rowList.append(row)
        self.DB._db.deleteRows(METADATA_TABLE, "table_name LIKE '"+self._fileIndexTable+"'")
        self.DB._db.insertRows(METADATA_TABLE,rowList)
##############################################################################
class GWASTrackAccessModule(object):
    GWAS_URL = 'https://www.ebi.ac.uk/gwas/api/search/downloads/full'
    
    def __init__(self, fileIndexTable,isSqlite = False):
        self._site = HttpRemoteAccessSite(self.GWAS_URL)
        self._fileIndexTable = fileIndexTable
        self.DB = DatabaseTrackAccessModule(isSqlite)
        self.DB._db.connect()
        
        #self._trackCollection = []
        self._cols = {}
        self._rowList = []
        
    def makeFileIndexTable(self):
        indexFileLines = self._site.retrieveFileData(self.GWAS_URL)
        cols = indexFileLines[0].split('\t')
        self._cols = dict((x,None) for x in cols)
        
        
        for line in indexFileLines[1:]:
            if not line.strip():
                continue

            #cols = self._cols.keys()
            try:
                row = line.split('\t')
                self._rowList += self._parseRow(cols, row)

            # except ValueError:
            #     continue

            except Exception as e:
                print 'Error in track: '
                print zip(cols, row)
                print 'Error message:'
                print str(e)
                continue

        self._cols['uri'] = None
        self._cols['hb_genomebuild'] = None
        self._cols['hb_datatype'] = None
        self._cols['hb_filesuffix'] = None
        self._cols['hb_target'] = None
        self._cols['hb_experiment_type'] = None


        index = {}
        for row in self._rowList:
            #Append to the list of SNPS:
            #key = row['CHR_ID']+'-'+row['CHR_POS']
            key = row['SNPS']
            if key in index:
                index[key] += 1
            else:
                index[key] = 0
            row['uri'] = 'gwas://'+key+'-'+str(index[key])+'.gtrack'
            row['hb_datatype'] = self.DB.getDataType(row['uri'].split('/')[-1], 'GWAS')
            if 'DISEASE/TRAIT' in row:
               row['hb_target'] = row['DISEASE/TRAIT']
            row['hb_filesuffix'] = 'gtrack'#getFileSuffixFromRow(row)
            row['hb_experiment_type'] = 'GWAS'
            row['hb_genomebuild'] = 'hg19'
        ##print self._rowList[0]
        self.DB._db.dropTable(self._fileIndexTable)
        self.DB._db.createTableFromDict(self._fileIndexTable,self._cols, pk = 'uri')
        self.DB._db.insertRows(self._fileIndexTable,self._rowList)
        #To avoid problems caused by non-ascii characters for this particular case:
        #query = 'update file_gwas set "DISEASE/TRAIT" = "BETA2-Glycoprotein I (BETA2-GPI) plasma levels", hb_target = "BETA2-Glycoprotein I (BETA2-GPI) plasma levels" where  "DISEASE/TRAIT" like "&beta;2-Glycoprotein I (&beta;2-GPI) plasma levels";'
        query = 'update file_gwas set "DISEASE/TRAIT" = replace("DISEASE/TRAIT", "&beta;","BETA") where "DISEASE/TRAIT" like "%&beta;%"'
        output = self.DB._db.runQuery(query)

    def _parseRow(self, cols, row):
        rowList = []
        rowDict = OrderedDict()
        semicolonCols = []

        for i in range(len(cols)):
            curRow = row[i].strip('\r')
            rowDict[cols[i]] = curRow
            if ';' in curRow:
                semicolonCols.append(cols[i])

        # In order to fix lines containing multiple SNPs
        if semicolonCols and 'CHR_ID' in semicolonCols:
            assert 'CHR_POS' in semicolonCols
            numSemicolons = rowDict[semicolonCols[0]].count(';')
            for col in semicolonCols[1:]:
                if rowDict[col].count(';') != numSemicolons and col != 'DISEASE/TRAIT':
                    rowDict[col] = ''

            for j in range(numSemicolons + 1):
                newRowDict = rowDict.copy()
                for col in semicolonCols:
                    if ';' in rowDict[col]:
                        newRowDict[col] = rowDict[col].split(';')[j]
                rowList += self._parseRow(cols, newRowDict.values())
            return rowList

        if rowDict['CHR_ID'].strip() == '' or rowDict['CHR_POS'].strip() == '':
            snps = rowDict['SNPS'].strip().lower()
            if snps.startswith('chr'):
                for splitChar in ['.', ':']:
                    if splitChar in snps:
                        chrId, chrPos = snps.split(splitChar)[:2]
                        rowDict['CHR_ID'] = chrId[3:]
                        rowDict['CHR_POS'] = chrPos
                        break

            if rowDict['CHR_ID'].strip() == '' or rowDict['CHR_POS'].strip() == '':
                raise ValueError('Missing genome position information')

        rowList.append(rowDict)

        return rowList

    def setMetadata(self):
        METADATA_TABLE = 'file_col_metadata'
        rowList = []
        cols = self.DB._db.getTableCols(self._fileIndexTable)
        keywords = {'hb_datatype':'Type of Data','hb_filesuffix':'File Suffix',\
                    'hb_target':'* Target','hb_experiment_type':'* Experiment type',\
                    'hb_genomebuild':'* Genome Build'}
        for col in cols:
            row = {'table_name':self._fileIndexTable}
            if col in keywords.keys():
                rName = keywords[col]
            else:
                rName = col#.replace('_',' ').title()
            row.update({'col_name':col, 'col_readable_name':rName, 'col_val':'.'})
            rowList.append(row)
        self.DB._db.deleteRows(METADATA_TABLE, "table_name LIKE '"+self._fileIndexTable+"'")
        self.DB._db.insertRows(METADATA_TABLE,rowList)
##############################################################################
class EBIHubTrackAccessModule(object):
    EBIHub_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/blueprint/releases/20150128/homo_sapiens/hub/hg19/'
    INDEX_FILENAME = 'tracksDb.txt'
    COMPOSITE_DATA_LIST = ['subGroups','metadata']
    PARENT_TRACKS = ['bp','region']
    TRACK_FILE_URL = 'bigDataUrl'
    
    def __init__(self, fileIndexTable,isSqlite = False):
        self._site = HttpRemoteAccessSite(self.EBIHub_URL)
        self._fileIndexTable = fileIndexTable
        self.DB = DatabaseTrackAccessModule(isSqlite)
        self.DB._db.connect()
        
        self._trackCollection = []
        self._cols = {'name':None,'url':None, 'hb_datatype':None, 'hb_filesuffix': None}
        self._rowList = []
        
    def makeTrackIndexList(self):
        indexFileLines = self._site.retrieveFileData(self.EBIHub_URL+self.INDEX_FILENAME)
        readingTrack = False
        track = {}
        rowDict = {}
        for line in indexFileLines:
            #Starting track:
            if line.strip().startswith('track'):
                trackname = line.strip().split(' ')[1]
                if trackname in self.PARENT_TRACKS:
                    continue
                readingTrack = True
                track = {'name':trackname}
                rowDict = {'name':trackname}
            #Composite datatype --> read parameters splitting by '='
            elif readingTrack and line.strip().startswith(tuple(self.COMPOSITE_DATA_LIST)):
                title = line.strip().split(' ')[0]
                paramDict = dict((e.split('=')[0],e.split('=')[1]) for e in line.strip().split(' ')[1:])
                self._cols.update(dict((e.split('=')[0].lower(),None) for e in line.strip().split(' ')[1:]))
                track[title] = paramDict
                rowDict.update(dict((e.split('=')[0].lower(),e.split('=')[1]) for e in line.strip().split(' ')[1:]))
            #Empty line --> End of track
            elif readingTrack and line.strip() == '':
                self._trackCollection.append(track)
                if 'url' in rowDict:
                    self._rowList.append(rowDict)
                readingTrack = False
                track = {}
                rowDict = {}
            #Other non-composite datatypes (value might contain spaces)
            elif readingTrack:
                title = line.strip().split(' ')[0]
                if title != self.TRACK_FILE_URL:
                    self._cols[title.lower()] = None
                    rowDict[title.lower()] = ' '.join(line.strip().split(' ')[1:])
                else:
                    rowDict['url'] = line.strip().split(' ')[1]
                    rowDict['hb_datatype'] = self.DB.getDataType(rowDict['url'].split('/')[-1], 'EBIHub')
                    rowDict['hb_filesuffix'] = getFileSuffixFromRow(rowDict)
                track[title] = ' '.join(line.strip().split(' ')[1:])
                
    def makeFileIndexTable(self):
        #cols = ['project','file_name','url']
        self.DB._db.dropTable(self._fileIndexTable)
        self.DB._db.createTableFromDict(self._fileIndexTable,self._cols, pk = 'url')
        self.DB._db.insertRows(self._fileIndexTable,self._rowList)
    
    def setMetadata(self):
        METADATA_TABLE = 'file_col_metadata'
        rowList = []
        cols = self.DB._db.getTableCols(self._fileIndexTable)
        for col in cols:
            row = {'table_name':self._fileIndexTable}
            if col == 'hb_datatype':
                rName = 'HB Data Type'
            if col == 'hb_filesuffix':
                rName = 'HB File Suffix'
            else:
                rName = col.replace('_',' ').title()
            row.update({'col_name':col, 'col_readable_name':rName, 'col_val':'.'})
            rowList.append(row)
        self.DB._db.deleteRows(METADATA_TABLE, "table_name LIKE '"+self._fileIndexTable+"'")
        self.DB._db.insertRows(METADATA_TABLE,rowList)
##############################################################################
#class EncodeTrackAccessModule(TrackAccessModule):
class EncodeTrackAccessModule(object):
    TRACK_ACCESS_MODULE_ID = 'encode'

    ENCODE_UCSC_URL = 'ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC/'
    ENCODE_ENSEMBL_URL = 'ftp://ftp.ebi.ac.uk/pub/databases/ensembl/encode/integration_data_jan2011/'
    INDEX_DIRECTORY = 'encode_index_rep'
    INDEX_FILENAME = 'files.txt'
    

    def __init__(self, fileIndexTable = None,isSqlite = False):
        self._encodeUcscSite = FtpRemoteAccessSite(self.ENCODE_UCSC_URL)
        self._encodeEnsemblSite = FtpRemoteAccessSite(self.ENCODE_ENSEMBL_URL)
        self._fileIndexTable = fileIndexTable
        self.DB = DatabaseTrackAccessModule(isSqlite)
        self.DB._db.connect()
        self.indexFileList = []
        self._cols = {}
        self._rowList = []
        if os.path.exists(self.INDEX_DIRECTORY):
            shutil.rmtree(self.INDEX_DIRECTORY)
        
    def yieldUCSCIndexFile(self):
        for f in self._encodeUcscSite.yieldSecondLevelFiles(self.INDEX_FILENAME,self.INDEX_DIRECTORY):
            yield f

    def yieldEnsemblIndexFile(self):
        for f in self._encodeEnsemblSite.yieldFile(self.INDEX_FILENAME,self.INDEX_DIRECTORY):
            yield f
    
    def downloadIndexFiles(self):
        for f in self.yieldEnsemblIndexFile():
            self.indexFileList.append(os.path.abspath(f))
            print 'Downloaded index file: '+f
            self.addTrackIndexData(os.path.abspath(f))
            print 'Added Track Data from: '+f+'\n'+20*'='
            
        for f in self.yieldUCSCIndexFile():
            self.indexFileList.append(os.path.abspath(f))
            print 'Downloaded index file: '+f
            self.addTrackIndexData(os.path.abspath(f), isUCSC = True)
            print 'Added Track Data from: '+f+'\n'+20*'='

    def addTrackIndexData(self, indexFile, isUCSC = False):
        ENCODE_UCSC_URL='ftp://hgdownload.cse.ucsc.edu/goldenPath/hg19/encodeDCC'
        urlParent = ''
        source = 'Ensembl'
        if isUCSC:
            source = 'UCSC'
            urlParent = '/'.join([ENCODE_UCSC_URL,\
                                os.path.abspath(indexFile).split('/')[-2],''])
        
        self._cols.update({'_source':None})
        self._cols.update({'_url':None})
        self._cols.update({'hb_datatype':None})
        self._cols.update({'hb_filesuffix':None})
        self._cols.update({'hb_cell_tissue_type':None})
        self._cols.update({'hb_target':None})
        self._cols.update({'hb_genomebuild':None})

        with open(indexFile,'r') as f:
             lines = f.readlines()
        
        #rowList = []
        row = None
        i = 0
        for l in lines:
            if len(l.strip()) == 0:
                continue
            try:        
                rowDict = {}#{'filename':None,'filesuffix':None,'datatype':None}
                rowDict.update({'_source':source})
                if l.find('#') >= 0:
                    url = urlParent + l.split('#')[0].strip()
                    rowDict.update({'_url':url})
                    datatype = self.DB.getDataType(url.split('/')[-1],'Encode')

                    rowDict.update({'hb_datatype':datatype})
                    #rowDict.update({'filename':url})
                    self._rowList.append(rowDict)
                    i +=1
                    continue
                url = urlParent + l.split('\t')[0]
                rowDict.update({'_url':url})
                row = l.split('\t')[1].split(';')
                
                for element in row:
                    el = element.strip().split('=')
                    el_name = el[0].strip().lower()
                    if el_name == 'size':
                       rowDict.update({el_name:self.DB._db.getNumeric(el[1])})
                       self._cols.update({el_name:'DECIMAL(20,2)'})
                    elif el_name in ['datesubmitted',\
                                                   'dateresubmitted']:
                       rowDict.update({el_name:el[1]})
                       self._cols.update({el_name:'DATE'})
                    elif el_name in ['geosampleaccession','geosampleaccesion']:
                        if 'geosampleaccession' in self._cols.keys():
                            continue
                        rowDict.update({'geosampleaccession':el[1]})
                        self._cols.update({'geosampleaccession':None})
                    else:      
                       rowDict.update({el_name:el[1]})
                       self._cols.update({el_name:None})
                datatype = self.DB.getDataType(url.split('/')[-1],'Encode')
                rowDict['hb_datatype'] = datatype
                rowDict['hb_filesuffix'] = getFileSuffixFromRow(rowDict)
                if 'cell' in rowDict:
                    rowDict['hb_cell_tissue_type'] = rowDict['cell']
                if 'antibody' in rowDict:
                    rowDict['hb_target'] = rowDict['antibody']
                rowDict['hb_genomebuild'] = 'hg19'
                self._rowList.append(rowDict)

                #print i
                i +=1
            except IndexError as e:
                print 'Error in ['+indexFile+'] Line '+str(i)+': '+str(e)
                print 'Line Text: '+l
                
    def makeFileIndexTable(self):            
        #self.addTrackIndexData(self.indexFileList[0])
        #for f in self.indexFileList[1:]:
        #    self.addTrackIndexData(f, isUCSC = True)
    
        self.DB._db.dropTable(self._fileIndexTable)
        self.DB._db.createTableFromDict(self._fileIndexTable,self._cols, pk = '_url')
        self.DB._db.insertRows(self._fileIndexTable,self._rowList)
    
    def setMetadata(self):
        METADATA_TABLE = 'file_col_metadata'
        rowList = []
        cols = self.DB._db.getTableCols(self._fileIndexTable)
        keywords = {'_url':'URL','hb_datatype':'Type of Data','hb_filesuffix':'File Suffix',\
                        'hb_genomebuild':'* Genome Build','hb_cell_tissue_type':'* Cell/Tissue Type','hb_target':'* Target',\
                        'datatype':'* Experiment (Assay) Type','labprotocolid':'Lab Protocol ID',\
                        'dateresubmitted':'Date Resubmitted','objstatus':'Obj Status',\
                        'fragsize':'Fragment Size','expid':'Experiment ID','sourceobj':'Source Object','submitteddataversion':'Submitted Data Version',\
                        'insertlength':'Insert Length','subid':'Sub ID','labversion':'Lab Version','tablename':'Table Name',\
                        'dccaccession':'DCC Accession','origassembly':'Original Assembly','datesubmitted':'Date Submitted',\
                        'labexpid':'Lab Experiment ID','donorid':'Donor ID','dccrep':'DCC Rep','spikeinpool':'spike in Pool',\
                        'settype':'Experiment or Input','softwareversion':'Software Version','controlid':'Control ID',\
                        'dateunrestricted':'Date Unrestricted','geosampleaccession':'GEO sample accession',\
                        'dataversion':'Data Version','readtype':'Read Type','mapalgorithm':'Map Algorithm','rnaextract':'RNA Extract','seqplatform':'Seq-Platform',\
                        'obtainedby':'Obtained By', 'type':'File Type','antibody':'Antibody or target protein',\
                        'cell':'Cell, tissue or DNA sample','localization':'Cellular compartment','phase':'Cell Phase',\
                        'control':'Control or Input for ChIP-seq','view':'View - Peaks or Signals','quality':'Integrated quality flag',\
                        'biorep':'Cross Lab Bio-Replicate ID','sex':'Sex of donor organism','replicate':'Replicate number',\
                        'lab':'Lab producing data','softwareversion':'Lab specific informatics','seqplatform':'Sequencing Platform',\
                        'protocol':'Library protocol','dataversion':'ENCODE Data Freeze'}
        for col in cols:
            row = {'table_name':self._fileIndexTable}
            if col in keywords.keys():
                rName = keywords[col]
            else:
                rName = col.title()
            rName = rName.strip()
            row.update({'col_name':col, 'col_readable_name':rName,'col_val':'.'})
            rowList.append(row)
        self.DB._db.deleteRows(METADATA_TABLE, "table_name LIKE '"+self._fileIndexTable+"'")
        self.DB._db.insertRows(METADATA_TABLE,rowList)
    #
    #def _structIndexElementIterator(self):
    #    for fn,tagDict in [('fil',{'a':1,'b':2}), ('fil2',{'b':4}), ('fil3',{}), ('fil4',{'a':1, 'b':4})]:
    #        yield StructIndexElement(uniqueFileId=fn, tagDict=tagDict)


#TrackAccessModuleRegistry.register(EncodeTrackAccessModule())


#http=HttpRemoteAccessSite('https://tcga-data.nci.nih.gov/tcgafiles/ftp_auth/distro_ftpusers/anonymous/tumor/')
#http.getFileNames('acc/bcr/biotab/clin/')

##########################ENCODE_old(stable)#######################################
#encode = EncodeTrackAccessModule()
#files = []
#for f in t.yieldEnsemblIndexFile():
#    files.append(os.path.abspath(f))#.split('/')[-2])
#    #files.append(f)    
#
#for f in t.yieldUCSCIndexFile():
#    files.append(os.path.abspath(f))#.split('/')[-2])
#
#print files

#v = mod2.CommonVocabularyParser('cv.ra',\
#                           "host='localhost' dbname='abdulara' user='abdulara'"\
#                           "password='144144'",\
#                           'field','file_encode')

##print v.findAllKeys()
#v.makeFieldTable()

#v.addTrackIndexData_Independent(files[0])
#for f in files[1:]:
#    v.addTrackIndexData_Independent(f, isUCSC = True)
#v.makeFileIndexTable_Independent()

#print '======================================================================'
#colList = v._db.getTableCols('file_encode', ordered = True)
#ATTRIBUTES = []
#for col in colList:
#   searchable = v._db.runQuery("select term,_searchable,_datatype from field where term = '"+col+"';")
#   #print searchable
#   if searchable[0][1] == True:
#      ATTRIBUTES.append(col)
#print ATTRIBUTES
##########################Create file_type table###########################
#DB = DatabaseTrackAccessModule(isSqlite = True,raiseDBErrors = False)
#DB.createFileTypeTable()
##########################Create meta-data table###########################
#DB = DatabaseTrackAccessModule(isSqlite = True,raiseDBErrors = False)
#DB._db.createTableFromList('file_col_metadata',['col_readable_name','col_name',
#                                                'table_name','col_description',
#                                                'col_val'],
#                           pk = ['table_name','col_name','col_val'])
#############################################################################

def main(argv):
    arg = argv[0]
    DB = DatabaseTrackAccessModule(isSqlite = True,raiseDBErrors = False)
    if arg in ['-h','--help']:
        print 'An importer for remote genomic track repositories metadata'
        sys.exit()
    if arg == '--col-metadata':
         DB.createMetadataTable()
    elif arg == '--file-type':
        DB.createFileTypeTable()
    elif arg == '--data-type':
        DB.createDataTypeTable()
    elif arg == '--last-update':
        DB.createLastUpdateTable()
    elif arg.upper().strip() == 'ENCODE':
        encode = EncodeTrackAccessModule('file_encode',isSqlite = True)
        encode.downloadIndexFiles()
        encode.makeFileIndexTable()
        encode.setMetadata()
        DB.updateLastUpdateTable('file_encode')
    elif arg.upper().strip() == 'EPIGENOME2':
        epi2 = Epigenome2TrackAccessModule('file_epigenome2',isSqlite = True)
        epi2.makeTrackMetadata()
        epi2.makeFileIndexTable()
        epi2.setMetadata()
        DB.updateLastUpdateTable('file_epigenome2')
    elif arg.upper().strip() == 'EPIGENOME':
        epi = EpigenomeTrackAccessModule('file_epigenome',isSqlite = True)
        epi.makeFileIndexTable()
        epi.setMetadata()
        DB.updateLastUpdateTable('file_epigenome')
    elif arg.upper().strip() == 'TCGA':
        tcga = TCGATrackAccessModule('file_cgatlas',isSqlite = True)
        #tcga.makeFileIndexTable()
        tcga.setMetadata()
        DB.updateLastUpdateTable('file_cgatlas')
    elif arg.upper().strip() == 'ICGC':
        ##Test1:
        #http = HttpRemoteAccessSite('https://dcc.icgc.org/api/v1/download/info/current/Projects/')
        ##Test1.1:
        #print http.retrieveJSON('')
        icgc = ICGCTrackAccessModule('file_icgc',isSqlite = True)
        icgc.makeFileIndexTable()
        icgc.setMetadata()
        DB.updateLastUpdateTable('file_icgc')
    elif arg.upper().strip() == 'EBIHUB':
        ebi = EBIHubTrackAccessModule('file_ebihub',isSqlite = True)
        ebi.makeTrackIndexList()
        ##print ebi._trackCollection[0]
        ebi.makeFileIndexTable()
        ebi.setMetadata()
        DB.updateLastUpdateTable('file_ebihub')
    elif arg.upper().strip() == 'GWAS':
        gwas = GWASTrackAccessModule('file_gwas',isSqlite = True)
        gwas.makeFileIndexTable()
        gwas.setMetadata()
        DB.updateLastUpdateTable('file_gwas')
    elif arg.upper().strip() == 'FANTOM5':
        ##Test1:
        #http = HttpRemoteAccessSite('http://fantom.gsc.riken.jp/5/datafiles/latest/basic/')
        ##Test1.1:
        #print http.getFileTagsNames('human.cell_line.LQhCAGE/')
        
        ##Test1.2:
        #dirList = [x for x in http.retrieveFileNames('') if x.endswith('/')]
        #print str(len(dirList))+ ' disrectories'
        #for d in dirList:
        #    url = http.getIndexFileURL(x,'_sdrf.txt')
        #    print 'No. Attributes: ' + str(len(http.retrieveFileData(url)[0].split('\t')))
        #urlList = [http.getIndexFileURL(x,'_sdrf.txt') for x in dirList]
        #print urlList
        #print http.retrieveFileData(urlList[-1])[0].split('\t')
        ##Test3:
        #print '\nAttributes'
        #print fantom.getAttributes()
        #print '\nData:'
        #for d in fantom.insertIndexData(fantom.getIndexFiles()[0]):
        #    print d['url']        
        
        ##Working Code:
        fantom = FANTOM5TrackAccessModule('file_fantom5',isSqlite = True)
        fantom.setIndexFiles()
        fantom.setAttributes()
        fantom.makeIndexTable()
        #fantom.insertIndexData(fantom.getIndexFiles()[0])
        for f in fantom.getIndexFiles():
            fantom.insertIndexData(f)
        print 20 * '*'
        print str(len(fantom._errorFiles))+' files had errors:'
        print 20 * '*'
        for errf in fantom._errorFiles:
            print errf
        fantom.setMetadata()
        DB.updateLastUpdateTable('file_fantom5')
    else:
        print 'Invalid repository name.'
        sys.exit()


        

if __name__ == "__main__":
    # # from gold.application.DataTypes import getSupportedFileSuffixesForGSuite
    # # print getSupportedFileSuffixesForGSuite()
    if len(sys.argv) < 2:
        print 'Too few attributes!'
        sys.exit()
    main(sys.argv[1:])
