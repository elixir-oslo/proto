import ast
from quick.webtools.GeneralGuiTool import GeneralGuiTool
from quick.application.ExternalTrackManager import ExternalTrackManager
from xml.dom import minidom
from urllib import quote, unquote
from gold.util.CustomExceptions import InvalidFormatError
from gold.util.CommonFunctions import getFileSuffix, createOrigPath
import time
import zmq
from shutil import copyfile, make_archive, copytree
from gold.util.RandomUtil import random
from os import makedirs, symlink, sep

class AddFilesToStorebioinfoDataset(GeneralGuiTool):
    STOREBIO_ROOT_PATH = '/usit/invitro/work/hyperbrowser/nosync/nobackup/storeBioInfo_transfer/'
    context = zmq.Context()
    socket = context.socket(zmq.REQ)
    socket.connect("tcp://localhost:5559")
    
    @staticmethod
    def getToolName():
        return "Add files to StoreBioInfo dataset"

    @staticmethod
    def getInputBoxNames():
        "Returns a list of names for input boxes, implicitly also the number of input boxes to display on page. Each such box will call function getOptionsBoxK, where K is in the range of 1 to the number of boxes"
        #can have two syntaxes: either a list of stings or a list of tuples where each tuple has two items(Name of box on webPage, name of getOptionsBox)
        return ['Select source of upload','select history or genome', 'select track','Username','password', 'Select dataset', 'select subtype', 'write path in subtype' ] # 'UIO username', 'UIO password'
    
    @staticmethod
    def getNextLevel(userName, password, inList):
        #from quick.extra.WsStoreBioInfo import *
        params = 'params:='+repr(inList)
        AddFilesToStorebioinfoDataset.socket.send('##'.join(['username:='+userName,'password:='+password, params, 'operation:=getSubTrackName','class:=dataStorageService']))
        responseList = ast.literal_eval(AddFilesToStorebioinfoDataset.socket.recv_unicode().encode('ascii','ignore'))
        return ['--select--']+[v[0] for v in responseList]
    
    
    @staticmethod    
    def getOptionsBox1():
        return ['from history', 'from tracks']
        
    @staticmethod    
    def getOptionsBox2(prevChoices):
        #return ''
        if prevChoices[-2] == 'from history':
            return '__multihistory__', 
        else:
            return '__genome__'
    
    
    @staticmethod    
    def getOptionsBox3(prevChoices):
        if prevChoices[0] == 'from tracks':
            return '__track__'
    
    
    @staticmethod    
    def getOptionsBox4(prevChoices):
        '''Returns a list of options to be displayed in the first options box
        Alternatively, the following have special meaning:
        '__genome__'
        '__track__'
        ('__history__','bed','wig','...')
        '''
        return ''
    
    @staticmethod    
    def getOptionsBox5(prevChoices): 
        '''Returns a list of options to be displayed in the second options box, which will be displayed after a selection is made in the first box.
        prevChoices is a list of selections made by the web-user in the previous input boxes (that is, list containing only one element for this case)        
        '''
        return  '__password__'
    
    @staticmethod    
    def getOptionsBox6(prevChoices):
        #from quick.extra.WsStoreBioInfo import *
        if prevChoices[-3]  and prevChoices[-2]:
            return AddFilesToStorebioinfoDataset.getNextLevel(prevChoices[-3], prevChoices[-2], ['StoreBioInfo'])
    
    
    @staticmethod    
    def getOptionsBox7(prevChoices):
        #from quick.extra.WsStoreBioInfo import *
        if prevChoices[-2]  and prevChoices[-2] != '--select--':
            return AddFilesToStorebioinfoDataset.getNextLevel(prevChoices[-4], prevChoices[-3], ['StoreBioInfo', prevChoices[-2]])
    
    
    @staticmethod    
    def getOptionsBox8(prevChoices):
        
        if prevChoices[-2]  and prevChoices[-2] != '--select--':
            return ''
    
    
    #@staticmethod    
    #def getOptionsBox9(prevChoices):
    #    if prevChoices[-2]:
    #        return ''
    #
    #@staticmethod    
    #def getOptionsBox10(prevChoices): 
    #    if prevChoices[-2]:
    #        return  '__password__'
    
    
    
    
        
    @classmethod    
    def execute(cls, choices, galaxyFn=None, username=''):
        '''Is called when execute-button is pushed by web-user.
        Should print output as HTML to standard out, which will be directed to a results page in Galaxy history.
        If getOutputFormat is anything else than HTML, the output should be written to the file with path galaxyFn.
        If needed, StaticFile can be used to get a path where additional files can be put (e.g. generated image files).
        choices is a list of selections made by web-user in each options box.
        '''
        #from quick.extra.WsStoreBioInfo import *
        
        if username =='':
            username = ''.join([chr(random.randint(97,122)) for i in range(6)]) 
        dirForDataset = cls.STOREBIO_ROOT_PATH+username + '_'.join([str(v) for v in time.localtime()[:6]]) + str(time.time()).split('.')[-1]
        print dirForDataset
        makedirs(dirForDataset)
        url = ''#'scp://invitro.titan.uio.no:'
        if choices[0] == 'from tracks':
            
            sourceLink = createOrigPath(genome=choices[1], trackName=choices[2].split(':'))
            folder = (dirForDataset + '/'+ choices[-1] +'/').replace('//','/')
            
            symboliclink = folder+ choices[2].split(':')[-1]
            if not os.path.isdir(folder):
                    os.makedirs(folder)
            copytree(sourceLink, symboliclink)# symlink(sourceLink, symboliclink)
            
        else:
            sourceLink = dirForDataset
            galaxyTnList = [unquote(v).split(':') for v in choices[1].values() if v]
        
            for galaxyTn in galaxyTnList:
                
                fnSource = ExternalTrackManager.extractFnFromGalaxyTN(galaxyTn)
                folder = (dirForDataset+'/'+choices[-1]+'/').replace('//','/')
                fnDestination = folder + galaxyTn[-1].replace(' ','_')+'.'+galaxyTn[1]
                if not os.path.isdir(folder):
                    os.makedirs(folder)
                copyfile(fnSource, fnDestination)
                url = url + fnDestination
                
                
        
        #AddFileToDataSet(dataSetId, subtype, pathInSubtype, url, userName, password)
        #['Username','password', 'Select dataset', 'select subtype', 'write path in subtype', 'UIO username', 'UIO password']
        
        userName, password = choices[3], choices[4]
        #uioUser, uioPwd = choices[-2], choices[-1]
        dataSetId, subtype = choices[5].split('(')[-1].split(')')[0] , choices[6]
        pathInSubtype = choices[7] if choices[7] else ''
        
        params = ['username:='+userName, 'password:='+password, 'operation:=AddFileToDataSet', 'class:=dataStorageService',\
                  'params:='+'<#>'.join([dataSetId, subtype, pathInSubtype, dirForDataset])]
        print params
        
        cls.socket.send(messageSep.join(params))
        message = cls.socket.recv_unicode().encode('utf-8')#, 'ignore'
        if message != 'something went wrong...':
            print 'Dataset successfully upploaded to Storebio server'
        else:
            print message

    @staticmethod
    def validateAndReturnErrors(choices):
        '''
        Should validate the selected input parameters. If the parameters are not valid,
        an error text explaining the problem should be returned. The GUI then shows this text
        to the user (if not empty) and greys out the execute button (even if the text is empty).
        If all parameters are valid, the method should return None, which enables the execute button.
        '''
        return None
    
    #@staticmethod
    #def isPublic():
    #    return False
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
    #@staticmethod    
    #def getOutputFormat(choices):
    #    '''The format of the history element with the output of the tool.
    #    Note that html output shows print statements, but that text-based output
    #    (e.g. bed) only shows text written to the galaxyFn file.
    #    '''
    #    return 'html'
    #
