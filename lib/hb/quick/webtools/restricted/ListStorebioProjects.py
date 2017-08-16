# -*- coding: utf-8 -*-
import ast
import cStringIO
import pickle
import time
import urllib2
import zipfile
from urllib import quote, unquote
from xml.dom import minidom

import zmq

from proto.hyperbrowser.HtmlCore import HtmlCore
from proto.hyperbrowser.StaticFile import GalaxyRunSpecificFile
from quick.webtools.GeneralGuiTool import GeneralGuiTool


#This is a template prototyping GUI that comes together with a corresponding web page.
#

class ListStorebioProjects(GeneralGuiTool):
    
    cachedXml = ''
    nsDat="http://storebioinfo.norstore.no/service/datastorage"
    nsDat1="http://storebioinfo.norstore.no/schema/datastorage"
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")
    
    @staticmethod
    def getToolName():
        return "StoreBioInfo integration tools"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['Username at StoreBioinfo','Password at StoreBioinfo', 'Select Operation', 'hidden', 'Select Dataset', 'Select SubType' , 'Select Dataset Element', 'Project Names', 'Project Info', 'Datasets',  'Select Dataset Element', 'Select Dataset Element', 'Select Dataset Element', 'Select Dataset Element', 'Select Dataset Element', 'File Preview']#'hidden','Select files from zip archive'

    
    
    
    
    @staticmethod    
    def getOptionsBox1():
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ''
    
    @staticmethod    
    def getOptionsBox2(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return  '__password__'
    
    
            
    @staticmethod    
    def getOptionsBox3(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ['-----Select-----','List Projects', 'List Datasets', 'Download file from Dataset']
    
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        
        if prevChoices[2] == 'Download file from Dataset':
            if prevChoices[3] not in [None, '']:
                return ('__hidden__', prevChoices[3])
            else:
                userName = prevChoices[0] if prevChoices[0] else ''
                pwd = prevChoices[1] if prevChoices[1] else ''
                operation = 'List Datasets'
                ListStorebioProjects.socket.send('##'.join(['username:='+userName,'password:='+pwd, 'operation:='+operation,'class:=dataStorageService']))
                
                return ('__hidden__',  quote(ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')))#.decode("ascii",'ignore').encode("ascii")))#.encode("ascii",'ignore')
        
    @staticmethod    
    def getOptionsBox5(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')'''
        NS = ListStorebioProjects.nsDat1
        if prevChoices[2] == 'Download file from Dataset':
            datasetList = ['--select--']
            
            userName = prevChoices[0] if prevChoices[0] else ''
            pwd = prevChoices[1] if prevChoices[1] else ''
            operation = 'getSubTrackName'
            params = 'params:='+repr(['StoreBioInfo'])
            
            ListStorebioProjects.socket.send('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
            responseList = ast.literal_eval(ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore'))
            return ['--select--']+[v[0].split('(')[0].strip() for v in responseList]
        
    
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
    
        if prevChoices[4] != None and prevChoices[2] == 'Download file from Dataset' and prevChoices[-2]!='--select--':
            
            userName = prevChoices[0] if prevChoices[0] else ''
            pwd = prevChoices[1] if prevChoices[1] else ''
            operation = 'getSubTrackName'
            dsList = pickle.loads(unquote(prevChoices[3]))
            dsId = [ds.id for ds in dsList if ds.name == prevChoices[-2]][0]
            dsName = prevChoices[-2] + '(%s)' %  dsId   
            params = 'params:='+repr(['StoreBioInfo',dsName])
            
            ListStorebioProjects.socket.send('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
            responseList = ast.literal_eval(ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore'))
            return ['--select--']+[v[0] for v in responseList]
        
    @staticmethod    
    def getOptionsBox10(prevChoices):
    
        if prevChoices[4] != None and prevChoices[2] == 'Download file from Dataset' and prevChoices[5] and prevChoices[5]!='--select--' :
            
            userName = prevChoices[0] if prevChoices[0] else ''
            pwd = prevChoices[1] if prevChoices[1] else ''
            operation = 'getSubTrackName'
            dsList = pickle.loads(unquote(prevChoices[3]))
            dsId = [ds.id for ds in dsList if ds.name == prevChoices[4]][0]
            dsName = prevChoices[4] + '(%s)' %  dsId   
            params = 'params:='+repr(['StoreBioInfo', dsName, prevChoices[5]])
            
            ListStorebioProjects.socket.send('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
            resp = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
            if resp != '':
                return ['--select--']+[v[0] for v in ast.literal_eval(resp)]
    
    
    @staticmethod    
    def getOptionsBox11(prevChoices):
    
        if prevChoices[4] != None and prevChoices[2] == 'Download file from Dataset' and prevChoices[-2]:
            if prevChoices[-2] != '--select--' and prevChoices[-2].split(',')[-1] != 'FILE':
                userName = prevChoices[0] if prevChoices[0] else ''
                pwd = prevChoices[1] if prevChoices[1] else ''
                operation = 'getSubTrackName'
                dsList = pickle.loads(unquote(prevChoices[3]))
                dsId = [ds.id for ds in dsList if ds.name == prevChoices[4]][0]
                dsName = prevChoices[4] + '(%s)' %  dsId   
                params = 'params:='+repr(['StoreBioInfo', dsName, prevChoices[5], prevChoices[9]])
                
                ListStorebioProjects.socket.send('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
                resp = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
                if resp != '':
                    return ['--select--']+[v[0] for v in ast.literal_eval( resp )]
    
    @staticmethod    
    def getOptionsBox12(prevChoices):
    
        if prevChoices[4] != None and prevChoices[2] == 'Download file from Dataset' and prevChoices[-2]:
            if prevChoices[-2] != '--select--' and prevChoices[-2].split(',')[-1] != 'FILE':
                userName = prevChoices[0] if prevChoices[0] else ''
                pwd = prevChoices[1] if prevChoices[1] else ''
                operation = 'getSubTrackName'
                dsList = pickle.loads(unquote(prevChoices[3]))
                dsId = [ds.id for ds in dsList if ds.name == prevChoices[4]][0]
                dsName = prevChoices[4] + '(%s)' %  dsId   
                params = 'params:='+repr(['StoreBioInfo', dsName, prevChoices[5], prevChoices[9], prevChoices[10]])
                
                ListStorebioProjects.socket.send('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
                resp = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
                if resp != '':
                    return ['--select--']+[v[0] for v in ast.literal_eval( resp )]
    
    
    @staticmethod    
    def getOptionsBox13(prevChoices):
    
        if prevChoices[4] != None and prevChoices[2] == 'Download file from Dataset' and prevChoices[-2]:
            if prevChoices[-2] != '--select--' and prevChoices[-2].split(',')[-1] != 'FILE':
                userName = prevChoices[0] if prevChoices[0] else ''
                pwd = prevChoices[1] if prevChoices[1] else ''
                operation = 'getSubTrackName'
                dsList = pickle.loads(unquote(prevChoices[3]))
                dsId = [ds.id for ds in dsList if ds.name == prevChoices[4]][0]
                dsName = prevChoices[4] + '(%s)' %  dsId  
                params = 'params:='+repr(['StoreBioInfo', dsName, prevChoices[5], prevChoices[9], prevChoices[10], prevChoices[11]])
                
                ListStorebioProjects.socket.send('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
                resp = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
                if resp != '':
                    return ['--select--']+[v[0] for v in ast.literal_eval( resp )]
    
    @staticmethod    
    def getOptionsBox14(prevChoices):
    
        if prevChoices[4] != None and prevChoices[2] == 'Download file from Dataset' and prevChoices[-2]:
            if prevChoices[-2] != '--select--' and prevChoices[-2].split(',')[-1] != 'FILE':
                userName = prevChoices[0] if prevChoices[0] else ''
                pwd = prevChoices[1] if prevChoices[1] else ''
                operation = 'getSubTrackName'
                dsList = pickle.loads(unquote(prevChoices[3]))
                dsId = [ds.id for ds in dsList if ds.name == prevChoices[4]][0]
                dsName = prevChoices[4] + '(%s)' %  dsId  
                params = 'params:='+repr(['StoreBioInfo', dsName, prevChoices[5], prevChoices[9] , prevChoices[10], prevChoices[11], prevChoices[12]])
                
                ListStorebioProjects.socket.send('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
                resp = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
                if resp != '':
                    return ['--select--']+[v[0] for v in ast.literal_eval( resp )]
    
    
    @staticmethod    
    def getOptionsBox15(prevChoices):
    
        if prevChoices[4] != None and prevChoices[2] == 'Download file from Dataset' and prevChoices[-2]:
            if prevChoices[-2] != '--select--' and prevChoices[-2].split(',')[-1] != 'FILE':
                userName = prevChoices[0] if prevChoices[0] else ''
                pwd = prevChoices[1] if prevChoices[1] else ''
                operation = 'getSubTrackName'
                dsList = pickle.loads(unquote(prevChoices[3]))
                dsId = [ds.id for ds in dsList if ds.name == prevChoices[4]][0]
                dsName = prevChoices[4] + '(%s)' %  dsId  
                params = 'params:='+repr(['StoreBioInfo', dsName, prevChoices[5], prevChoices[9], prevChoices[10], prevChoices[11], prevChoices[12], prevChoices[13]])
                
                ListStorebioProjects.socket.send_unicode('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
                resp = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
                if resp != '':
                    return ['--select--']+[v[0] for v in ast.literal_eval( resp )]
            
            
    @staticmethod    
    def getOptionsBox16(prevChoices):
    
        if prevChoices[4] != None and prevChoices[2] == 'Download file from Dataset' and len([v for v in prevChoices[9:] if isinstance(v, basestring)  and v.find(',FILE')>0])>0:
            filPathTab = []
            
            for value in prevChoices[-7:-1]:
                if value and value.find(',')>0:
                    filPathTab.append(value.split(',')[0])
            if '/'.join([v for v in prevChoices[-7:-1]if isinstance(v, basestring)]).find(',FILE')>0:
                
                userName = prevChoices[0] if prevChoices[0] else ''
                pwd = prevChoices[1] if prevChoices[1] else ''
                operation = 'GetFilePreview'
                dsList = pickle.loads(unquote(prevChoices[3]))
                dsId = [ds.id for ds in dsList if ds.name == prevChoices[4]][0]
                    
                params = 'params:='+'<#>'.join([dsId, repr([prevChoices[5]]+filPathTab) ])
                ListStorebioProjects.socket.send_unicode('##'.join(['username:='+userName,'password:='+pwd, params, 'operation:='+operation,'class:=dataStorageService']))
                tmpResult = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
                return (tmpResult, len(tmpResult.split('\n')), True)
            
        
    @staticmethod    
    def getOptionsBox7(prevChoices):
        messageSep = '##'
        if prevChoices[2] == 'List Projects':
            params = ['username:='+prevChoices[0],'password:='+prevChoices[1], 'operation:='+prevChoices[2]]

            params += ['class:=userMngtService']
            ListStorebioProjects.socket.send(messageSep.join(params))
            
            
            projects = pickle.loads(ListStorebioProjects.socket.recv_unicode().encode('utf-8'))
            if len(projects) >1:
                return [v.name for v in projects]
            else:
                project = projects[0]
                streng = ''
                for attr in ['name','created','description','creator']:
                    streng+= attr+':  '+ str(getattr(project, attr))+'\n'
                
                streng+= 'Quota name:  ' + project.quota.name + '\n'
                streng+=     repr(getattr(project, 'members'))
                
                streng+='\n\nProject Datasets:\n'
                params = ['username:='+prevChoices[0],'password:='+prevChoices[1], 'operation:=getDatasetsByProject']
    
                params += ['class:=dataStorageService']
                params += ['params:='+'<#>'.join([project.id, 'False','False'])]
                ListStorebioProjects.socket.send_unicode(messageSep.join(params))
                
                dataSets = pickle.loads(ListStorebioProjects.socket.recv_unicode().encode('utf-8'))
                
                dataSetsString = '\n'.join(['  ,  '.join((v.name, v.created, v.description)) for v in dataSets])
                streng+=dataSetsString
                    
                return (streng, streng.count('\n')+1, True)
            
            
    
    @staticmethod    
    def getOptionsBox8(prevChoices):
        messageSep = '##'
        if prevChoices[2] == 'List Projects' and prevChoices[-2] not in ['-----Select-----', None]  and not prevChoices[-2].find('\n')>0:
            params = ['username:='+prevChoices[0],'password:='+prevChoices[1], 'operation:='+prevChoices[2]]

            params += ['class:=userMngtService']
            ListStorebioProjects.socket.send(messageSep.join(params))
            
            projName = prevChoices[-2]
            projects = pickle.loads(ListStorebioProjects.socket.recv_unicode().encode('utf-8'))
            
            project = [v for v in projects if v.name == projName][0] 
        
            streng = ''
            for attr in ['name','created','description','creator']:
                streng+= attr+':  '+ str(getattr(project, attr))+'\n'
            streng+= 'Quota name:  ' + project.quota.name + '\n'
            streng+=     repr(getattr(project, 'members'))
            streng+='\n\nProject Datasets:\n'
            params = ['username:='+prevChoices[0],'password:='+prevChoices[1], 'operation:=getDatasetsByProject']

            params += ['class:=dataStorageService']
            params += ['params:='+'<#>'.join([project.id, 'False','False'])]
            ListStorebioProjects.socket.send_unicode(messageSep.join(params))
            
            dataSets = pickle.loads(ListStorebioProjects.socket.recv_unicode().encode('utf-8'))
            
            dataSetsString = '\n'.join(['  ,  '.join((v.name.decode('ascii',errors='ignore'), v.created, v.description.decode('ascii',errors='ignore'))) for v in dataSets])
            streng+=dataSetsString        
            return (streng, streng.count('\n')+1, True)
    
    @staticmethod    
    def getOptionsBox9(prevChoices):
        messageSep = '##'
        if prevChoices[2] == 'List Datasets':
            params = ['username:='+prevChoices[0],'password:='+prevChoices[1], 'operation:=List Datasets']
            
            params += ['class:=dataStorageService']
            ListStorebioProjects.socket.send(messageSep.join(params))
            dataSets = pickle.loads(ListStorebioProjects.socket.recv_unicode().encode('utf-8'))
            streng = '\n'.join(['  ,  '.join((v.name.decode('ascii',errors='ignore'), v.created, v.description.decode('ascii',errors='ignore'))) for v in dataSets])
            return (streng, streng.count('\n'),True)
            
    

    #@staticmethod
    #def getDemoSelections():
    #    return ['testChoice1','..']
        
    @staticmethod    
    def execute(choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history. If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.gtr
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        messageSep = '##'
        start = time.time()
        outputFile=open(galaxyFn,"w")
        params = ['username:='+choices[0],'password:='+choices[1], 'operation:='+choices[2]]
        
        
        
            
        if choices[2] == 'List Projects':
            params += ['class:=userMngtService']
            ListStorebioProjects.socket.send(messageSep.join(params))
            message = ListStorebioProjects.socket.recv_unicode().encode('utf-8')#, 'ignore'
            if message == 'something went wrong...':
                return None
            else:
                print>>outputFile, message #ListStorebioProjects.ParseProjectListXmlDoc(minidom.parseString(message))
            
            
            
        elif choices[2] == 'Download file from Dataset':
            outputFile=open(galaxyFn,"w")
            
            filPathTab = []
            
            for i in range(9,15):
                if choices[i] and choices[i].find(',')>0:
                    filPathTab.append(choices[i].split(',')[0])
            dataSets = pickle.loads(unquote(choices[3]))
            datasetId = [ds.id for ds in dataSets if ds.name == choices[4]][0]        
            #datasetId = choices[4].split('(')[-1].split(')')[0].strip()
            subList = [{'Subtype': choices[5], 'FileToExtract': '/'.join(filPathTab)}]#
            paramlist = ['username:='+choices[0],'password:='+choices[1], 'operation:=GetFileUrlsFromDataSet','class:=dataStorageService',\
                'params:='+'<#>'.join([ repr(datasetId), repr(subList)])]
            ListStorebioProjects.socket.send(messageSep.join(paramlist))
            url = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
                
            
            fileType = url.split('.')[-1].strip()
            if fileType == 'zip':
                validFiles = [k for k,v in choices[7].items() if v]
                
                remotezip = urllib2.urlopen(url)
                zipinmemory = cStringIO.StringIO(remotezip.read())
                zip = zipfile.ZipFile(zipinmemory)
                
                for fn in zip.namelist():
                    if fn in validFiles:
                        print>>outputFile, zip.read(fn)
                        print>>outputFile, "\n\n\n\n\n\n\n"
            else:
                ftpList = [v.strip().split()[-1] for v in urllib2.urlopen(url).read().split('\n') if v.strip()!='']
                for relativeUrl in ftpList:
                    fileType = relativeUrl.split('.')[-1].strip()
                    if fileType in ['png','jpg', 'jpeg', 'gif']:
                        picFile = GalaxyRunSpecificFile([relativeUrl], galaxyFn)
                        #CHUNKS = 512*1024
                        open(picFile.getDiskPath(ensurePath=True), 'wb').write(urllib2.urlopen(url+relativeUrl).read())
                        #with open(picFile.getDiskPath(ensurePath=True), 'wb') as fp:
                        #    fileContent = req.read(CHUNKS)
                        #    if not  fileContent:
                        #        break
                        #    fp.write(fileContent)
                        print>>outputFile, '<img src="%s" width="500px" height="600px"/>' % picFile.getURL()
                    else:    
                        print>>outputFile, urllib2.urlopen(url+relativeUrl).read()
                    
                
            
        else:
            params += ['class:=dataStorageService']
            ListStorebioProjects.socket.send(messageSep.join(params))
            message = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
            print>>outputFile, ListStorebioProjects.ParseDatasetsXmlDoc(minidom.parseString(message))
            
        outputFile.close()
    
    
    @staticmethod
    def ParseProjectListXmlDoc(xmlDoc):  
        ProjectsList = []
        wsXmlParser = ParseXml()
        for project in  xmlDoc.getElementsByTagName('Project'):
            
            ProjectsList.append(wsXmlParser.ParseProjectXml(project))
        
        
        tableList = []
        for project in ProjectsList:
            tablestr = '<table>'
            keys = ['Name','Description','Creater','Created','Quota','DiskUsage']
            for key in keys:
                if key in project:
                    if key == 'Quota':
                        tablestr+= '<tr><td>%s: </td><td> </td><td>%s</td></tr>' % (key, project[key][key])
                    else:
                        tablestr+= '<tr><td>%s: </td><td> </td><td>%s</td></tr>' % (key, project[key])
            tablestr += '</table>'
            if 'ProjectMembers' in project:
                tablestr+= '<table><tr><td>ProjectMembers: </td><td> </td><td>Username </td><td>Roles </td><td> </td></tr>'
                for member in project['ProjectMembers']:
                    tablestr+= '<tr><td> </td><td> </td><td>'+member['Username']+'</td><td>'+member['Roles']+'</td><td> </td></tr>'
                tablestr += '</table>'
            tablestr += '<br/><br/>'
            tableList.append(tablestr)
        
        return '\n'.join(tableList)
    
    @staticmethod
    def ParseDatasetsXmlDoc(xmlDoc):
        core = HtmlCore()
        core.tableHeader(['Dataset Name', 'Description', 'Created', 'Owner', 'Size', 'Qty files in Dataset', 'State'], sortable=True)
        for dataset in xmlDoc.getElementsByTagName('DataSet'):
            datasetName =  DomUtility.getNodeValue(dataset, 'Name', 'str')
            owner = DomUtility.getNodeValue(dataset, 'Owner', 'str')
            dateCreated = DomUtility.getNodeValue(dataset, 'Created', 'date')
            size = sum([int(size.childNodes[0].nodeValue)  for size in dataset.getElementsByTagName('Size')])
            description = DomUtility.getNodeValue(dataset, 'Description', 'str')
            numOfFilesInDataset = len(dataset.getElementsByTagName('Resource'))
            state = DomUtility.getNodeValue(dataset, 'State', 'str')
            core.tableLine([datasetName, description, dateCreated, owner, str(size), str(numOfFilesInDataset), state])
        
        return str(core)
            



    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        
        if len(choices[1])>0:
            
        
            try:
                ListStorebioProjects.socket.send('##'.join(['username:='+choices[0],'password:='+choices[1], 'class:=userMngtService']))
                response = ListStorebioProjects.socket.recv_unicode().encode('ascii','ignore')
            except:
                return 'Invalid Username/Password combination!!'
            
            if choices[4] != None and choices[2] == 'Download file from Dataset':
                if '/'.join([v for v in choices[9:16] if isinstance(v, basestring)]).find(',FILE')<0:
                    return 'No file has been selected yet'
        else:
            return ''
    
    @staticmethod
    def isPublic():
        return False
    #
    #@staticmethod
    #def isRedirectTool():
    #    return False
    #
    #@staticmethod
    #def isHistoryTool():
    #    return True
    #
    #@staticmethod
    #def isDynamic():
    #    return True
    #
    #@staticmethod
    #def getResetBoxes():
    #    return []
    #
    #@staticmethod
    #def getToolDescription():
    #    return ''
    #
    #@staticmethod
    #def getToolIllustration():
    #    return None
    #
    #@staticmethod
    #def isDebugMode():
    #    return True
    #
    
    @staticmethod    
    def getOutputFormat(choices=None):
        '''The format of the history element with the output of the tool.
        Note that html output shows print statements, but that text-based output
        (e.g. bed) only shows text written to the galaxyFn file.
        '''
        if choices[2] in ['List Projects', 'List Datasets']:
            return 'html'
        returnType = 'bed'
        fileList = [v for v in choices[9:] if isinstance(v, basestring)  and v.find(',FILE')>0]
        if len(fileList)>0:
            returnType = fileList[0].split(',')[0].strip().split('.')[-1]
            if returnType in ['png','jpg', 'jpeg', 'gif']:
                returnType = 'html'
        
        return returnType
    
