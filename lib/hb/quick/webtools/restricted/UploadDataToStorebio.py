import ast
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager
from gold.util.CommonFunctions import createOrigPath
from shutil import copyfile, make_archive, copytree
from urllib import unquote
from gold.util.RandomUtil import random
import time
from os import makedirs, symlink, sep
from xml.dom import minidom
import shutil
import pickle
class UploadDataToStorebio(GeneralGuiTool):
    import zmq


    STOREBIO_ROOT_PATH = '/usit/invitro/work/hyperbrowser/nosync/nobackup/storeBioInfo_transfer/'
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")
    ProjectList = None
    DataSetTypeList = None
    @staticmethod
    def getToolName():
        return "Upload data to StoreBioInfo"

    @staticmethod
    def getInputBoxNames(prevChoices=None):
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        return ['UserName', 'Password', 'hidden', 'Select Project', 'Name for dataset', 'Description of dataset', 'Type of dataset']#'Select source for transfer', 'choose dataset', 'select tracks',  #'Select Resource Type'
    
    
    @staticmethod
    def getInputBoxOrder():
        '''
        Specifies the order in which the input boxes should be displayed, as a
        list. The input boxes are specified by index (starting with 1) or by
        key. If None, the order of the input boxes is in the order specified by
        getInputBoxNames.
        '''
        return [1,2,3,4,7,5,6]
    
    #@staticmethod    
    #def getOptionsBox1():
    #    return ['from history', 'from tracks']
    #    
    #@staticmethod    
    #def getOptionsBox2(prevChoices):
    #    #return ''
    #    if prevChoices[-2] == 'from history':
    #        return ('__multihistory__' ,'bed','wig')#
    #    else:
    #        return '__genome__'
    #
    #
    #@staticmethod    
    #def getOptionsBox3(prevChoices):
    #    if prevChoices[0] == 'from tracks':
    #        return '__track__'
        
    
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
        if prevChoices[-2] not in [None, '']:
            params = ['username:=%s' % prevChoices[-3], 'password:=%s' % prevChoices[-2], 'operation:=List Projects', 'class:=userMngtService']

            from quick.extra.WsStoreBioInfo import messageSep
            UploadDataToStorebio.socket.send(messageSep.join(params))
            projects = pickle.loads(UploadDataToStorebio.socket.recv_unicode().encode('utf-8'))#, 'ignore'
            UploadDataToStorebio.ProjectList = [(v.name, v.id, v.quota.id) for v in projects]
            #UploadDataToStorebio.ParseProjectListXmlDoc(minidom.parseString(message))
            return ('__hidden__', repr(UploadDataToStorebio.ProjectList))
            
    @staticmethod    
    def getOptionsBox4(prevChoices):
        if prevChoices[-2]:
            projectList = ast.literal_eval(prevChoices[-2])#UploadDataToStorebio.ProjectList#eval(prevChoices[-2])
            return [v[0] for v in projectList]
            resList = []
            for i in projectList:
                resList.append(i['Name'])
            return resList
        
    @staticmethod    
    def getOptionsBox5(prevChoices):
        return ''
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
        return ''
    
    @staticmethod    
    def getOptionsBox7(prevChoices):
        if prevChoices[1] not in [None, '']:
            params = ['username:=%s' % prevChoices[0], 'password:=%s' % prevChoices[1], 'operation:=List DataSetType', 'class:=dataStorageService']
            
            #params = list(prevChoices[1:3])+['List DataSetType', 'dataStorageService']
            from quick.extra.WsStoreBioInfo import messageSep
            UploadDataToStorebio.socket.send(messageSep.join(params))
            message = UploadDataToStorebio.socket.recv_unicode().encode('utf-8')#, 'ignore'
            return ['--select--'] + ast.literal_eval(message)
            #wsXmlParser = ParseXml()
            #UploadDataToStorebio.DataSetTypeList = wsXmlParser.ParseDataSetType(minidom.parseString(message))
            #return ['--select--']+[i['Name'] for i in UploadDataToStorebio.DataSetTypeList]
            
            
    #@staticmethod    
    #def getOptionsBox11(prevChoices):
    #    if prevChoices[-2] not in [None, '', '--select--']:
    #        return [i['subNames'] for i in UploadDataToStorebio.DataSetTypeList if i['Name']==prevChoices[-2]][0]
    #
    """
    if self.nodeExists(domTree, 'Id'):
            ProjectDict['Id'] = self.getNodeValue(domTree, 'Id', 'str')
    if self.nodeExists(domTree, 'Description'):
            ProjectDict['Description'] = self.getNodeValue(domTree, 'Description', 'str')
    
    projAccMal = '<ProjectAccessControlList><dat1:ProjectId>%s</dat1:ProjectId><dat1:UseDefaultPolicy>%s</dat1:UseDefaultPolicy>%s</ProjectAccessControlList>'
            
    ADD_DATASET_MAL = dat:AddDataset><Name>%s</Name>%s<QuotaId>%s</QuotaId><Type>%s</Type>%s
            <ResourceList><URLTypeMap><Url>%s</Url><ResourceType>%s</ResourceType></URLTypeMap>
            <Username>%s</Username><Password>%s</Password></ResourceList></dat:AddDataset
    """
    
    @staticmethod
    def ParseProjectListXmlDoc(xmlDoc):  
        ProjectsList = []
        from quick.extra.WsStoreBioInfo import ParseXml
        wsXmlParser = ParseXml()
        for project in  xmlDoc.getElementsByTagName('Project'):
            
            ProjectsList.append(wsXmlParser.ParseProjectXml(project))
        return ProjectsList
        
    
    
    @staticmethod    
    def execute(choices, galaxyFn=None, username=''):
        if username =='':
            username = ''.join([chr(random.randint(97,122)) for i in range(6)]) 
        dirForDataset = UploadDataToStorebio.STOREBIO_ROOT_PATH+username + '_'.join([str(v) for v in time.localtime()[:6]]) + str(time.time()).split('.')[-1]
        print dirForDataset
        makedirs(dirForDataset)
        
        
        #if choices[0] == 'from tracks':
        #    
        #    sourceLink = createOrigPath(genome=choices[1], trackName=choices[2].split(':'))
        #    #symboliclink = dirForDataset + sep + choices[2].split(':')[-1]
        #    #copytree(sourceLink, symboliclink)# symlink(sourceLink, symboliclink)
        #    
        #else:
        #    pass
        #    sourceLink = dirForDataset
        #    galaxyTnList = [unquote(v).split(':') for v in choices[1].values() if v]
        #
        #    for galaxyTn in galaxyTnList:
        #        
        #        fnSource = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTn)
        #        fnDestination = dirForDataset+'/' + galaxyTn[-1].replace(' ','_')+'.'+galaxyTn[1]
        #        print fnSource, fnDestination
        #        copyfile(fnSource, fnDestination)
        
        projectList = UploadDataToStorebio.ProjectList
        print choices
        projName = choices[3]
        projInfo = [ (i[1], i[2]) for i in projectList if i[0] == projName  ][0]
        #(self, name, quotaId, type, url ,resourceType, userName, password, description=None, projectAccessControlList=None):
        url = dirForDataset #'scp://invitro.titan.uio.no:'+ dirForDataset
        print 'Url: ', url
        print projectList
        print projInfo
        name, quotaId, dsType = choices[-3], projInfo[1], choices[-1]
        userName, password = choices[0], choices[1]
        projectAccessControlList = [projInfo[0], 'true']
        description = choices[-2] if choices[-2] not in ['', None] else ''
        
        params = ['username:='+userName, 'password:='+password, 'operation:=CreateDataSet', 'class:=dataStorageService',\
                  'params:='+'<#>'.join([name, quotaId, dsType, description, repr(projectAccessControlList)])]

        from quick.extra.WsStoreBioInfo import messageSep
        UploadDataToStorebio.socket.send_unicode(messageSep.join(params))
        message = UploadDataToStorebio.socket.recv_unicode().encode('utf-8')#, 'ignore'
        if message != 'something went wrong...':
            print 'Dataset successfully upploaded to Storebio server'
        else:
            print message
        print '<a href="http://hyperbrowser.uio.no/dev2/hyper?mako=generictool&tool_id=hb_add_files_to_storebioinfo_dataset">Start adding data to newly created dataset</a>'
    @staticmethod
    def isPublic():
        return False

    @staticmethod
    def getToolDescription():
        return 'Upload History elements to a new dataSet at StoreBioInfo'
        
    #@staticmethod
    #def getToolIllustration():
        #return ['illustrations','tools','GeneSetRegulators.png']
        #si = StaticImage(['illustrations','Tools','TfTargets'])

    
    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        #genome = choices[0]
        #seedSource = choices[1]
        #seedTfTnInput = choices[2]
        #
        #if seedSource != 'TFBS from history':
        #    tfTrackNameMappings = TfInfo.getTfTrackNameMappings(genome)
        #    seedTfTn = tfTrackNameMappings[seedSource] + [seedTfTnInput]
        #    #tfTrackName = tfTrackNameMappings[tfSource] + [selectedTF]
        #    if len(getOrigFns(genome, seedTfTn,'')) != 1:
        #        return 'Sorry. Only seed TFs that are internally represented as single files are currently supported. Please contact the HB team for assistance if needed. Track name that was not supported: ' + ':'.join(seedTfTn)
        #    
